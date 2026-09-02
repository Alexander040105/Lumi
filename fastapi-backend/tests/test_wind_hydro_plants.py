"""Unit tests for Wikipedia wind and hydro power plant loaders."""

from __future__ import annotations

import pytest

from app.services.wind_plants import (
    calculate_wind_proximity_boost,
    calculate_wind_generation_scale,
    get_wind_plants_in_province,
    get_wind_plants_near,
)
from app.services.hydro_plants import (
    calculate_hydro_proximity_boost,
    calculate_hydro_generation_scale,
    calculate_hydro_plant_floor,
    get_hydro_plants_in_province,
    get_hydro_plants_near,
)


class TestWindPlants:
    def test_wind_plants_loader_returns_list(self):
        plants = get_wind_plants_in_province("Ilocos Norte", only_operating=True)
        assert isinstance(plants, list)

    def test_get_wind_plants_near_ilocos(self):
        # Point near Bangui, Ilocos Norte
        nearby = get_wind_plants_near(18.53, 120.71, radius_km=25, only_operating=True)
        names = {p["project_name"] for p in nearby}
        assert "Bangui Wind Farm" in names

    def test_wind_proximity_boost_increases_score(self):
        # Bangui is at (18.52778, 120.71389)
        score, plants = calculate_wind_proximity_boost(
            18.53, 120.71, base_score=30.0, radius_km=25.0, max_bonus=25.0
        )
        assert score > 30.0
        assert score <= 100.0
        assert plants

    def test_wind_proximity_boost_no_plants(self):
        # Remote ocean point with no wind plants
        score, plants = calculate_wind_proximity_boost(
            5.0, 125.0, base_score=30.0, radius_km=25.0, max_bonus=25.0
        )
        assert score == 30.0
        assert not plants

    def test_wind_generation_scale_in_province(self):
        scale, plants = calculate_wind_generation_scale(
            None, None, province="Ilocos Norte"
        )
        assert scale >= 1.0
        assert plants

    def test_wind_generation_scale_capped(self):
        # Point with very large nearby capacity
        scale, plants = calculate_wind_generation_scale(
            18.53, 120.71, radius_km=50.0, scale_factor=10.0, max_scale=1.5
        )
        assert scale <= 1.5


class TestHydroPlants:
    def test_hydro_plants_loader_returns_list(self):
        plants = get_hydro_plants_in_province("Bulacan", only_operating=True)
        assert isinstance(plants, list)

    def test_get_hydro_plants_near_bulacan(self):
        # Angat dam is at approximately (14.87083, 120.14167)
        nearby = get_hydro_plants_near(14.87, 120.14, radius_km=25, only_operating=True)
        names = {p["project_name"] for p in nearby}
        assert "Angat Hydro Electric Power Plant" in names

    def test_hydro_proximity_boost_increases_score(self):
        score, plants = calculate_hydro_proximity_boost(
            14.87, 120.14, base_score=10.0, radius_km=50.0, max_bonus=25.0
        )
        assert score > 10.0
        assert score <= 100.0
        assert plants

    def test_hydro_proximity_boost_capped_at_100(self):
        score, plants = calculate_hydro_proximity_boost(
            14.87, 120.14, base_score=95.0, radius_km=50.0, max_bonus=25.0
        )
        assert score <= 100.0

    def test_hydro_generation_scale_in_province(self):
        scale, plants = calculate_hydro_generation_scale(
            None, None, province="Bulacan"
        )
        assert scale >= 1.0
        assert plants

    def test_hydro_plant_floor_zero_without_plants(self):
        floor, plants = calculate_hydro_plant_floor(
            5.0, 125.0, radius_km=50.0
        )
        assert floor == 0.0
        assert not plants

    def test_hydro_plant_floor_respects_max(self):
        floor, plants = calculate_hydro_plant_floor(
            None, None, province="Bulacan", max_floor_kwh=30.0
        )
        assert 0.0 < floor <= 30.0

    def test_hydro_plant_floor_in_named_province(self):
        floor, plants = calculate_hydro_plant_floor(
            None, None, province="Bulacan"
        )
        assert floor > 0.0
        assert plants
