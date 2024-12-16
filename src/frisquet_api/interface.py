from typing import Protocol
from enum import Enum

from .raw_models import SiteData, Consumption


class Zone(Enum):
    """Zone enum"""

    ZONE_1 = 1
    ZONE_2 = 2
    ZONE_3 = 3


class ModeChange(Enum):
    """HVAC mode enum"""

    PERMANENT = 6
    UNTIL_NEXT_CHANGE = 5


class HeatingMode(Enum):
    """Preset mode enum"""

    COMFORT = 6
    ECO = 7
    FROST_PROTECTION = 8


class WaterModeSimple(Enum):
    """Water mode enum"""

    ON = 5
    OFF = 0


class WaterMode(Enum):
    """Water mode enum"""

    MAX = 0
    ECO = 1
    ECO_TIMER = 2
    ECO_PLUS = 3
    ECO_PLUS_TIMER = 4
    OFF = 5


class Mode(Enum):
    """Mode enum"""

    AUTO = 5
    COMFORT = 6
    ECO = 7
    FROST_PROTECTION = 8


class FrisquetApiInterface(Protocol):
    """Interface defining the Frisquet API contract"""

    async def set_temperature(self, site_id: str, zone: Zone, heating_mode: HeatingMode, temperature: float) -> None:
        """Set temperature for a specific zone"""
        ...

    async def set_mode(self, site_id: str, zone: Zone, change: ModeChange, mode: Mode) -> None:
        """Set mode for a specific zone."""
        ...

    async def set_boost(self, site_id: str, zone: Zone, on: True) -> None:
        """Turn boost on and off."""
        ...

    async def set_water_mode(self, site_id: str, water_mode: WaterMode | WaterModeSimple) -> None:
        """Set water mode for a specific zone."""
        ...

    async def get_consumption(self, site_id: str) -> Consumption:
        """Get consumption data for a specific site."""
        ...

    async def get_authentication(self) -> str:
        """Get authentication token"""
        ...

    async def get_site_data(self, site_id: str) -> SiteData:
        """Get data for a specific site"""
        ...
