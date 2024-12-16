"""Frisquet API client."""

import logging
from contextlib import asynccontextmanager
import httpx
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import AsyncIterator

class Token(BaseModel):
    """Frisquet API token."""

    token: str
    expires_at: datetime

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "https://fcutappli.frisquet.com/api/v1/"

async def raise_on_4xx_5xx(response: httpx.Response) -> None:
    response.raise_for_status()

class FrisquetClient:
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

        self._token = Token(token=auth_data["token"], expires_at=datetime.now() + timedelta(hours=1))
        self._sites = {site["identifiant_chaudiere"]: site["nom"] for site in auth_data["utilisateur"]["sites"]}
        
    async def get_authentication(self) -> dict:
        """Get authentication token from Frisquet API."""
        headers = {'Content-Type': 'application/json'}
        auth_data = {
            "locale": "fr",
            "email": self._email,
            "password": self._password,
            "type_client": "IOS",
        }
        
        async with self._http_client(authenticated=False) as client:
            resp = await client.post("/authentifications", headers=headers, json=auth_data)

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

    async def get_consumption(self, site_id: str):
        """Get energy consumption data for a specific site."""
        token = await self._get_auth_token()
        url = f"{self.api_url}{site_id}/conso?token={token}&types[]=CHF&types[]=SAN"
        async with httpx.AsyncClient(event_hooks={'response': [raise_on_4xx_5xx]}) as client:
            resp = await client.get(url)
            return resp.json()

    async def set_zone_temperature(self, site_id: str, zone_id: str, temperature: float) -> bool:
        """Set temperature for a specific zone (placeholder for future implementation)."""
        # TODO: Implement temperature setting
        raise NotImplementedError("Temperature setting not yet implemented")

    async def set_zone_mode(self, site_id: str, zone_id: str, mode: str) -> bool:
        """Set mode for a specific zone (placeholder for future implementation)."""
        # TODO: Implement mode setting
        raise NotImplementedError("Mode setting not yet implemented")
    
    @asynccontextmanager
    async def _http_client(self, authenticated: bool = False) -> AsyncIterator[httpx.AsyncClient]:
        """Get an HTTP client with authentication headers."""
        headers = {'Content-Type': 'application/json'}
        params = {}
        if authenticated:
            token = await self.token
            params['token'] = token

        async with httpx.AsyncClient(headers=headers, params=params, base_url=self._url,  event_hooks={'response': [raise_on_4xx_5xx]}) as client:
            yield client  # Yield the client for use in the context