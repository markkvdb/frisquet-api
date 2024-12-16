"""Frisquet API client."""

import logging
from contextlib import asynccontextmanager
import httpx
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import AsyncIterator

from frisquet_api.interface import (
    FrisquetApiInterface,
    Zone,
    Mode,
    ModeChange,
    HeatingMode,
)

MODE_TO_VALUE = {Mode.AUTO: 5, Mode.COMFORT: 6, Mode.ECO: 7, Mode.FROST_PROTECTION: 8}
HEATING_MODE_TO_VALUE = {
    HeatingMode.COMFORT: 6,
    HeatingMode.ECO: 7,
    HeatingMode.FROST_PROTECTION: 8,
}
HEATING_MODE_TO_STR = {
    HeatingMode.COMFORT: "CONS_COMFORT",
    HeatingMode.ECO: "CONS_RED",
    HeatingMode.FROST_PROTECTION: "CONS_HG",
}
SELECT_TO_VALUE = {ModeChange.UNTIL_NEXT_CHANGE: 5, ModeChange.PERMANENT: 6}


class Token(BaseModel):
    """Frisquet API token."""

    token: str
    expires_at: datetime


logger = logging.getLogger(__name__)

DEFAULT_API_URL = "https://fcutappli.frisquet.com/api/v1/"


async def raise_on_4xx_5xx(response: httpx.Response) -> None:
    response.raise_for_status()


class FrisquetClient(FrisquetApiInterface):
    """API Client for Frisquet Connect."""

    def __init__(self, email: str, password: str, url: str = DEFAULT_API_URL):
        """Initialize the API client.

        Args:
            email: User's email address
            password: User's password
        """
        self._email = email
        self._password = password
        self._url = url.rstrip("/")
        self._token: Token | None = None
        self._sites: dict[str, str] | None = None

    async def set_temperature(
        self, site_id: str, zone: Zone, heating_mode: HeatingMode, temperature: float
    ) -> None:
        """Set temperature for a specific zone"""
        key = _temperature_key(zone, heating_mode)
        int_temperature = int(temperature * 10)
        payload = {key: int_temperature}
        await self._post_values(site_id, payload)

    async def set_mode(
        self, site_id: str, zone: Zone, change: ModeChange, mode: Mode
    ) -> None:
        """Set mode for a specific zone."""
        # If the mode is auto and the change is until next change, we need to set the mode to permanent
        if change == ModeChange.UNTIL_NEXT_CHANGE and mode == Mode.AUTO:
            logger.warning(
                "Auto mode cannot be set until next change. Setting to permanent instead."
            )
            change = ModeChange.PERMANENT

        key, value = _mode_change_payload(zone, change, mode)
        payload = {key: value}
        await self._post_values(site_id, payload)

    async def set_boost(self, site_id: str, zone: Zone, on: True) -> None:
        """Turn boost on and off."""
        key = f"ACTIVITE_BOOST_Z{zone.value}"
        payload = {key: 1 if on else 0}
        await self._post_values(site_id, payload)

    async def get_consumption_data(
        self, site_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """Get consumption data for a date range"""
        ...

    @property
    async def token(self) -> str:
        """Get authentication token from Frisquet API."""
        if not self._token or self._token.expires_at < datetime.now():
            await self.initialise()

        return self._token.token

    def initialised(self) -> bool:
        """Check if initialised."""
        return self._sites is not None

    async def initialise(self) -> None:
        """Initialise with token and site data."""
        auth_data = await self.get_authentication()

        self._token = Token(
            token=auth_data["token"], expires_at=datetime.now() + timedelta(hours=1)
        )
        self._sites = {
            site["identifiant_chaudiere"]: site["nom"]
            for site in auth_data["utilisateur"]["sites"]
        }

    async def get_authentication(self) -> dict:
        """Get authentication token from Frisquet API."""
        headers = {"Content-Type": "application/json"}
        auth_data = {
            "locale": "fr",
            "email": self._email,
            "password": self._password,
            "type_client": "IOS",
        }

        async with self._http_client(authenticated=False) as client:
            resp = await client.post(
                "/authentifications", headers=headers, json=auth_data
            )

            return resp.json()

    @property
    async def sites(self) -> dict[str, str]:
        """Return dictionary with boiler ID and name as value."""
        if not self.initialised():
            await self.initialise()

        return self._sites

    async def get_site_data(self, site_id: str) -> dict:
        """Get data for a specific site.

        Args:
            site_id: The site identifier

        Returns:
            Dict containing site data including zones, ECS, and energy consumption
        """
        if site_id not in await self.sites:
            raise ValueError(f"Site ID {site_id} not in available site IDs.")

        async with self._http_client(authenticated=True) as client:
            resp = await client.get(f"/sites/{site_id}")

        return resp.json()

    async def _post_values(self, site_id: str, values: dict) -> None:
        """Post values to Frisquet API."""
        values_dict = [{"cle": key, "valeur": value} for key, value in values.items()]
        async with self._http_client(authenticated=True) as client:
            res = await client.post(f"/ordres/{site_id}", json=values_dict)  # noqa: F841

        logger.info(f"Set values {values} for site {site_id}")

    @asynccontextmanager
    async def _http_client(
        self, authenticated: bool = False
    ) -> AsyncIterator[httpx.AsyncClient]:
        """Get an HTTP client with authentication headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "Frisquet Connect/2.5 (com.frisquetsa.connect; build:47; iOS 16.3.1) Alamofire/5.2.2",
            "Accept-Language": "en-FR;q=1.0, fr-FR;q=0.9",
        }
        params = {}
        if authenticated:
            token = await self.token
            params["token"] = token

        async with httpx.AsyncClient(
            headers=headers,
            params=params,
            base_url=self._url,
            event_hooks={"response": [raise_on_4xx_5xx]},
        ) as client:
            yield client  # Yield the client for use in the context


def _temperature_key(zone: Zone, heating_mode: HeatingMode) -> str:
    """Get the key for the temperature setting."""
    return f"{HEATING_MODE_TO_STR[heating_mode]}_Z{zone.value}"


def _mode_change_payload(zone: Zone, change: ModeChange, mode: Mode) -> tuple[str, int]:
    """Get the key for the mode setting."""
    if change == ModeChange.UNTIL_NEXT_CHANGE and mode == Mode.AUTO:
        raise ValueError(
            "Auto cannot be set until next change. Choose permanent instead."
        )

    key = (
        "MODE_DERO"
        if change == ModeChange.UNTIL_NEXT_CHANGE
        else f"SELECTEUR_Z{zone.value}"
    )
    return key, MODE_TO_VALUE[mode]
