"""Shared boundary types and constants used across LUMI routes.

These Literal/Enum types are intentionally small and route-focused. They let
FastAPI reject invalid enum-like values at the boundary with a standard 422
response instead of silently accepting bad input.
"""
from __future__ import annotations

from typing import Literal

# --- EnergyHub / Forecast metrics ---

ForecastMetric = Literal["consumption", "peak_demand", "renewable_generation"]
ForecastRunMetric = Literal["consumption", "peak_demand"]

# --- Map layer ---

MapRenewableType = Literal["solar", "wind", "hydro", "geothermal"]
MapCoverageLevel = Literal["municipality", "province"]

# --- EnergyHub map data ---

EnergyHubMapMetric = Literal[
    "renewable_potential",
    "solar_potential",
    "wind_potential",
    "hydro_potential",
    "geothermal_potential",
]
EnergyHubMapLevel = Literal["province", "municipality", "barangay"]

# --- Product recommendations ---

ProductEnergyType = Literal["solar", "wind", "hydro", "hydropower", "geothermal"]

# --- EcoSim data source ---

EcoSimDataSource = Literal["auto", "atlas", "era5"]

# --- Geospatial levels ---

GeospatialLevel = Literal["region", "province", "municipality", "barangay"]
