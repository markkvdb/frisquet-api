"""Raw models for the Frisquet API.

These models are used to parse the raw data from the Frisquet API and rename fields to English.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    """Information about the boiler product."""

    range: str = Field(..., alias="gamme")
    model: str = Field(..., alias="chaudiere")
    version: str = Field(..., alias="version1")
    secondary_version: str | None = Field(None, alias="version2")
    power: str = Field(..., alias="puissance")


class BoilerStatus(BaseModel):
    """Current status of the boiler."""

    timestamp: datetime = Field(..., alias="DATE_HEURE_CHAUDIERE")
    is_standby: bool = Field(..., alias="CHAUDIERE_EN_VEILLE")
    is_auto_mode: bool = Field(..., alias="AUTO_MANU")


class HotWaterMode(BaseModel):
    """Hot water mode settings."""

    name: str = Field(..., alias="nom")
    id: int
    code: str | None = None


class HotWaterSettings(BaseModel):
    """Hot water system configuration."""

    type: int = Field(..., alias="TYPE_ECS")
    has_solar: bool = Field(..., alias="solaire")
    is_active: bool | None = Field(None, alias="AVEC_ECS")
    current_mode: HotWaterMode = Field(..., alias="MODE_ECS")
    solar_mode: HotWaterMode | None = Field(None, alias="MODE_ECS_SOLAIRE")
    heat_pump_mode: HotWaterMode | None = Field(None, alias="MODE_ECS_PAC")


class Environment(BaseModel):
    """Environmental measurements."""

    external_temperature: float = Field(..., alias="T_EXT")
    external_temperature_ge: float | None = Field(None, alias="T_EXT_GE")


class VacationMode(BaseModel):
    """Vacation mode settings."""

    departure_date: datetime | None = Field(None, alias="DATE_DEP_VACANCES")
    return_date: datetime | None = Field(None, alias="DATE_RET_VACANCES")
    is_active: bool = Field(..., alias="MODE_VACANCES")


class ZoneCharacteristics(BaseModel):
    """Heating zone characteristics."""

    heating_mode: int = Field(..., alias="MODE")
    mode: int = Field(..., alias="SELECTEUR")
    ambient_temperature: float = Field(..., alias="TAMB")
    target_temperature: float = Field(..., alias="CAMB")
    override_active: bool = Field(..., alias="DERO")
    eco_temperature: float = Field(..., alias="CONS_RED")
    comfort_temperature: float = Field(..., alias="CONS_CONF")
    frost_protection_temperature: float = Field(..., alias="CONS_HG")
    boost_active: bool = Field(..., alias="ACTIVITE_BOOST")


class DaySchedule(BaseModel):
    """Daily heating schedule."""

    day: int = Field(..., alias="jour")
    schedule: list[int] = Field(..., alias="plages")


class HeatingZone(BaseModel):
    """Heating zone configuration."""

    id: int
    identifier: str = Field(..., alias="identifiant")
    number: int = Field(..., alias="numero")
    name: str = Field(..., alias="nom")
    has_boost: bool = Field(..., alias="boost_disponible")
    characteristics: ZoneCharacteristics = Field(..., alias="carac_zone")
    weekly_schedule: list[DaySchedule] = Field(..., alias="programmation")


class Alert(BaseModel):
    """Alert configuration."""

    pass  # Extend based on actual alert structure


class SiteData(BaseModel):
    """Complete site data model."""

    # Basic site information
    site_id: str = Field(..., alias="sigmacom")
    name: str = Field(..., alias="nom")
    equipment_id: int = Field(..., alias="id_equipement")
    boiler_id: str = Field(..., alias="identifiant_chaudiere")
    timezone: str

    # Product and status information
    product: ProductInfo = Field(..., alias="produit")
    boiler_status: BoilerStatus = Field(..., alias="carac_site")
    last_update: datetime = Field(..., alias="date_derniere_remontee")

    # System configurations
    hot_water: HotWaterSettings = Field(..., alias="ecs")
    environment: Environment = Field(..., alias="environnement")
    vacation: VacationMode = Field(..., alias="vacances")
    zones: list[HeatingZone]

    # Available modes and alerts
    available_hot_water_modes: list[HotWaterMode] = Field(..., alias="modes_ecs")
    alerts: list[Alert] = Field(..., alias="alarmes")
    pro_alerts: list[Alert] = Field(..., alias="alarmes_pro")

    # Device identification
    agi: str


class ConsumptionAggregate(BaseModel):
    """Aggregate consumption data."""

    energy: int = Field(..., alias="valeur")
    month: int = Field(..., alias="mois")
    year: int = Field(..., alias="annee")


class Consumption(BaseModel):
    """Consumption data."""

    heating: list[ConsumptionAggregate] = Field(..., alias="CHF")
    hot_water: list[ConsumptionAggregate] = Field(..., alias="SAN")
    maximum: int = Field(..., alias="max")
