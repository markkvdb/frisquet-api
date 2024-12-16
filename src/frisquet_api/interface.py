from typing import Protocol, Dict, Any
from datetime import datetime
from enum import Enum


class Zone(Enum):
    """Zone enum"""

    ZONE_1 = 1
    ZONE_2 = 2
    ZONE_3 = 3


class ModeChange(Enum):
    """HVAC mode enum"""

    PERMANENT = "permanent"
    UNTIL_NEXT_CHANGE = "until_next_change"


class HeatingMode(Enum):
    """Preset mode enum"""

    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"


class Mode(Enum):
    """Mode enum"""

    AUTO = "auto"
    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"


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

    async def get_consumption_data(self, site_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get consumption data for a date range"""
        ...

    async def get_authentication(self) -> str:
        """Get authentication token"""
        ...

    async def get_site_data(self, site_id: str) -> Dict[str, Any]:
        """Get data for a specific site"""
        ...
