import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.ml.predictor import get_energyhub_ml, _sanitize_nan
from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.supabase_service import get_supabase_client
from app.services.redis_client import (
    get_suitability_cache_sync,
    set_suitability_cache_sync,
)
from app.services.geothermal.plants import (
    calculate_proximity_boost,
    get_all_ph_geothermal_plants,
)

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parents[3] / "DOE_Data_Extracted"
_GEOJSON_DIR = Path(__file__).resolve().parents[3] / "philippine_geojson"
_LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"

_VOLCANOES: list[dict[str, Any]] | None = None


# Canned fallbacks if Groq is unavailable (must match the style constraints)
_MAP_EXPLANATION_FALLBACKS = {
    "renewable_potential": (
        "The map shows a province-level composite renewable potential score. "
        "It averages the solar, wind, hydropower, and geothermal suitability values that are stored in the database. "
        "A province can look moderate even if it has volcanoes or rivers nearby because the composite is pulled down by any lower-scoring source; for example, strong geothermal potential can be offset by average solar or limited hydropower head. "
        "Scores are derived from municipality_climate_monthly (solar/wind), hydropower_suitability and geothermal_suitability tables."
    ),
    "solar_potential": (
        "The map colors provinces by solar suitability, calculated from NASA POWER all-sky surface shortwave downward radiation and normalized so that 5.0 kWh/m²/day equals the top score. "
        "Mountainous or cloudy regions, even those near volcanoes or water, can score moderate because terrain and cloud cover reduce usable irradiance. "
        "Data source: fastapi-backend/app/services/local_data/ and municipality_climate_monthly."
    ),
    "wind_potential": (
        "The map colors provinces by wind suitability, using 10 m wind speed from municipality_climate_monthly and normalized to 7.0 m/s as the upper benchmark. "
        "Coastal or elevated areas may still show moderate values if average wind speeds or terrain exposure are not consistently high. "
        "Data source: municipality_climate_monthly."
    ),
    "hydro_potential": (
        "The map shows hydropower suitability based on terrain slope, hydraulic head, runoff potential, and gravity-flow feasibility from the pre-computed hydropower_suitability table. "
        "A place can have abundant surface water yet a low or medium score if the land is flat, because low hydraulic head and gentle watershed gradients produce very little extractable power. "
        "Data source: regionalData/output/terrain_metrics/hydropower_suitability.csv and app/services/hydro_output_calc.py."
    ),
    "geothermal_potential": (
        "The map shows geothermal suitability boosted by proximity to operating geothermal plants. "
        "Areas near volcanoes or plants can still be moderate because surface heat is not enough: a viable geothermal site also needs permeable rock, reservoir temperature, water availability, and accessible terrain. "
        "Data source: geothermal_suitability table, fastapi-backend/app/services/geothermal/plants.py, and fastapi-backend/app/services/local_data/geothermal_volcanoes.json."
    ),
}


def _classify_score(value: float | None) -> str:
    if value is None:
        return "noData"
    if value >= 81:
        return "veryHigh"
    if value >= 61:
        return "high"
    if value >= 41:
        return "moderate"
    if value >= 21:
        return "low"
    return "veryLow"


def _load_volcanoes() -> list[dict[str, Any]]:
    """Load the Philippine volcano list used for map prompts and markers."""
    global _VOLCANOES
    if _VOLCANOES is not None:
        return _VOLCANOES
    candidates = [
        _LOCAL_DATA_DIR / "geothermal_volcanoes.json",
        Path(__file__).resolve().parents[3] / "react-frontend" / "public" / "geothermal_volcanoes.json",
        Path(__file__).resolve().parents[3] / "GeothermalDatasets" / "philippine_volcanoes.csv",
    ]
    _VOLCANOES = []
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            if candidate.suffix == ".csv":
                import csv
                with open(candidate, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get("Name of Volcano") or row.get("Name")
                        lat = row.get("Latitude")
                        lon = row.get("Longitude")
                        if name and lat and lon:
                            _VOLCANOES.append({
                                "name": name,
                                "lat": float(lat),
                                "lon": float(lon),
                                "province": row.get("Province", ""),
                            })
            else:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    _VOLCANOES = data
                elif isinstance(data, dict) and data.get("type") == "FeatureCollection":
                    _VOLCANOES = []
                    for feat in data.get("features", []):
                        props = feat.get("properties", {})
                        geom = feat.get("geometry", {})
                        coords = geom.get("coordinates") if geom.get("type") == "Point" else None
                        if coords:
                            _VOLCANOES.append({
                                "name": props.get("name", ""),
                                "lat": coords[1],
                                "lon": coords[0],
                                "province": props.get("province", ""),
                            })
            if _VOLCANOES:
                break
        except Exception as exc:
            logger.warning("Failed to load volcano data from %s: %s", candidate, exc)
    return _VOLCANOES


# Province name normalization: API/DB name → GeoJSON adm2_en name
_PROVINCE_NAME_MAP = {
    "compostela valley": "davao de oro",
    "cotabato (north cot.)": "cotabato",
    "davao (davao del norte)": "davao del norte",
    "davao (davao occidental)": "davao occidental",
    "davao del sur": "davao del sur",
    "maguindanao": "maguindanao del norte",  # primary mapping
    "ncr - 1st district (manila)": "ncr, city of manila, first district (not a province)",
    "ncr - 2nd district": "ncr, second district (not a province)",
    "ncr - 3rd district": "ncr, third district (not a province)",
    "ncr - 4th district": "ncr, fourth district (not a province)",
    "samar (western samar)": "samar",
    "taguig-pateros": "",  # not a province, skip
    "south cotabato": "south cotabato",
    "sultan kudarat": "sultan kudarat",
    "sulu": "sulu",
    "surigao del norte": "surigao del norte",
    "surigao del sur": "surigao del sur",
    "tawi-tawi": "tawi-tawi",
    "zambales": "zambales",
    "zamboanga del norte": "zamboanga del norte",
    "zamboanga del sur": "zamboanga del sur",
    "zamboanga sibugay": "zamboanga sibugay",
}


def _get_geojson_province_names() -> list[dict[str, str]]:
    """Return the list of GeoJSON province names used to align map data.

    The names come from the provinces table (geojson_name column) with a
    short-lived Redis cache.  If the DB is unavailable and local fallback is
    enabled, the original GeoJSON file is parsed.
    """
    cache_key = "energyhub:province_names"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    names: list[dict[str, str]] = []
    try:
        client = get_supabase_client()
        resp = client.table("provinces").select("name,geojson_name").execute()
        for row in resp.data or []:
            name = row.get("geojson_name") or row.get("name")
            if name:
                name = str(name).strip()
                names.append({"name": name, "name_lower": name.lower()})
    except Exception as exc:
        logger.warning("Supabase province geojson name query failed: %s", exc)

    if not names and os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true":
        geojson_path = _GEOJSON_DIR / "philippine_geojson_file_per_region.json"
        if geojson_path.exists():
            with open(geojson_path, "r", encoding="utf-8") as f:
                geo_data = json.load(f)
            for feat in geo_data.get("features", []):
                adm2 = (feat.get("properties", {}).get("adm2_en") or "").strip()
                if adm2:
                    names.append({"name": adm2, "name_lower": adm2.lower()})

    cache_set_sync(cache_key, names, ttl=86400)
    return names


class EnergyHubService:
    """Business logic layer for the EnergyHub module.

    Bridges the ML predictor (offline ARIMA artifacts), Supabase
    geographic/climate data, and the REST API.
    """

    PROMPT_VERSION = "2"

    def __init__(self) -> None:
        self._ml = get_energyhub_ml()

    # --- Overview ---

    def build_overview(self) -> dict[str, Any]:
        latest = self._ml.get_latest_statistics()
        forecast = self._ml.get_forecast("consumption")
        comparison = self._ml.get_model_comparison()

        # Derive a simple forecast growth metric for the overview card
        forecast_summary = {}
        if forecast.get("forecast_values"):
            current = latest.get("total_consumption_gwh", 0)
            f_2030 = forecast["forecast_values"][-1]
            forecast_summary = {
                "forecast_2030_gwh": f_2030,
                "forecast_growth_pct": round(((f_2030 / current) - 1) * 100, 2) if current else 0,
                "best_model": forecast.get("model", "ARIMA(1,1,1)"),
                "best_mape_pct": next(
                    (m["mape"] for m in comparison if m["model"] == "Linear Trend Regression"),
                    None,
                ),
            }

        return _sanitize_nan({
            "latest": latest,
            "forecast_summary": forecast_summary,
            "model_comparison": comparison,
        })

    # --- Forecast ---

    def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:
        return self._ml.get_forecast(metric)

    # --- Trends ---

    def build_trends(self) -> dict[str, Any]:
        historical = self._ml.get_historical_trends()
        forecast = self._ml.get_forecast("consumption")
        forecast_peak = self._ml.get_forecast("peak_demand")
        forecast_renewable = self._ml.get_forecast("renewable_generation")
        source_breakdown = self._ml.get_source_breakdown()
        grid_breakdown = self._ml.get_grid_breakdown()
        return _sanitize_nan({
            "years": historical["years"],
            "series": historical["series"],
            "forecast": forecast,
            "forecast_peak": forecast_peak,
            "forecast_renewable": forecast_renewable,
            "source_breakdown": source_breakdown,
            "grid_breakdown": grid_breakdown,
        })

    # --- Map Data ---

    def build_map_data(
        self,
        metric: str = "renewable_potential",
        level: str = "province",
    ) -> dict[str, Any]:
        """Return cached map data or build it on demand."""
        cache_key = f"energyhub:map:{metric}:{level}"
        cached = cache_get_sync(cache_key)
        if cached is not None:
            return cached
        result = self._build_map_data(metric, level)
        cache_set_sync(cache_key, result, ttl=3600)
        return result

    def _build_map_data(
        self,
        metric: str = "renewable_potential",
        level: str = "province",
    ) -> dict[str, Any]:
        """Build choropleth-ready data.

        All metrics use sub-national data:
        - Province-level: aggregated from municipality climate/terrain/suitability scores.
        - Municipality-level: pre-computed suitability scores from Supabase.
        - Barangay-level: inherits parent municipality suitability scores
          with centroid coordinates from geospatial_metadata.

        Args:
            metric: Metric to visualise. One of: renewable_potential,
                solar_potential, wind_potential, hydro_potential, geothermal_potential.
            level: "province", "municipality", or "barangay".
        """
        items: list[dict[str, Any]] = []

        # Municipality-level suitability metrics
        municipality_metrics = {
            "renewable_potential": "composite",
            "solar_potential": "solar",
            "wind_potential": "wind",
            "hydro_potential": "hydro",
            "geothermal_potential": "geothermal",
        }

        if metric in municipality_metrics and level == "municipality":
            column_prefix = municipality_metrics[metric]
            items = self._build_municipality_potential_map(column_prefix)
            return {"items": items, "metric": metric, "level": level}

        if metric in municipality_metrics and level == "barangay":
            items = self._build_barangay_potential_map(municipality_metrics[metric])
            return {"items": items, "metric": metric, "level": level}

        if metric == "renewable_potential":
            # Province-level aggregation (backward compatible)
            items = self._build_renewable_potential_map()

        elif metric == "geothermal_potential":
            items = self._build_geothermal_potential_map()

        elif metric in ("solar_potential", "wind_potential", "hydro_potential"):
            column_prefix = municipality_metrics[metric]
            items = self._build_province_metric_map(column_prefix, metric)

        return {"items": items, "metric": metric, "level": level}

    def _build_geothermal_potential_map(self) -> list[dict[str, Any]]:
        """Aggregate municipality-level geothermal scores to province level.

        Uses the pre-computed municipalities.geothermal_suitability_score as the
        base and applies a proximity boost for operating geothermal plants.
        Aggregation is by province_id, then matched to GeoJSON features by the
        provinces.geojson_name / name columns.
        """
        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        try:
            # 1. Province metadata (geojson_name is the canonical map feature name)
            prov_resp = client.table("provinces").select(
                "province_id,name,geojson_name,lat,lon"
            ).limit(10000).execute()
            prov_rows = prov_resp.data or []

            # 2. Municipalities with the pre-computed geothermal score
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id,name,lat,lon,"
                "geothermal_suitability_score,geothermal_classification,geothermal_factors"
            ).not_.is_("geothermal_suitability_score", "null").limit(10000).execute()
            muni_rows = muni_resp.data or []

            # Build province lookups keyed by id and by name variants
            province_by_id: dict[int, dict[str, Any]] = {}
            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                if not pid:
                    continue
                province_by_id[pid] = p
                for key in (
                    (p.get("geojson_name") or "").strip().lower(),
                    (p.get("name") or "").strip().lower(),
                ):
                    if key:
                        province_data[key] = {
                            "region": "",
                            "province": (p.get("name") or "").strip(),
                            "value": 0.0,
                            "lat": p.get("lat"),
                            "lon": p.get("lon"),
                            "nearby_plants": [],
                        }

            # Build per-province list of municipality scores (with boost)
            prov_scores: dict[int, list[float]] = {}
            prov_nearby: dict[int, list[dict]] = {}
            for row in muni_rows:
                pid = row.get("province_id")
                if pid is None:
                    continue
                base_score = float(row.get("geothermal_suitability_score") or 0)
                if base_score <= 0:
                    continue
                lat = row.get("lat")
                lon = row.get("lon")
                if lat is not None and lon is not None:
                    boosted, nearby = calculate_proximity_boost(
                        float(lat), float(lon), base_score
                    )
                else:
                    boosted = base_score
                    nearby = []
                prov_scores.setdefault(pid, []).append(boosted)
                if nearby:
                    existing = prov_nearby.setdefault(pid, [])
                    for p in nearby:
                        if not any(
                            e.get("project_name") == p["project_name"]
                            for e in existing
                        ):
                            existing.append(p)

            # Fill province data with the average boosted score
            for pid, p in province_by_id.items():
                scores = prov_scores.get(pid)
                if not scores:
                    continue
                avg = sum(scores) / len(scores)
                nearby = prov_nearby.get(pid, [])
                for key in (
                    (p.get("geojson_name") or "").strip().lower(),
                    (p.get("name") or "").strip().lower(),
                ):
                    if key:
                        province_data[key] = {
                            "region": "",
                            "province": (p.get("name") or "").strip(),
                            "value": round(avg, 2),
                            "lat": p.get("lat"),
                            "lon": p.get("lon"),
                            "nearby_plants": nearby,
                        }

            # 3. Match to GeoJSON province names
            geojson_provinces: list[dict[str, Any]] = _get_geojson_province_names()

            seen = set()
            for gp in geojson_provinces:
                gname = gp["name_lower"]
                if gname in seen:
                    continue
                seen.add(gname)
                data = province_data.get(gname)
                if not data:
                    for api_name, geo_name in _PROVINCE_NAME_MAP.items():
                        if geo_name.lower() == gname and api_name in province_data:
                            data = province_data[api_name]
                            break
                if data:
                    items.append({
                        "region": data["region"],
                        "province": gp["name"],
                        "municipality": None,
                        "value": data["value"],
                        "metric": "geothermal_potential",
                        "lat": data["lat"],
                        "lon": data["lon"],
                        "nearby_plants": data.get("nearby_plants", []),
                    })
                else:
                    items.append({
                        "region": "",
                        "province": gp["name"],
                        "municipality": None,
                        "value": None,
                        "metric": "geothermal_potential",
                        "lat": None,
                        "lon": None,
                        "nearby_plants": [],
                    })

        except Exception as exc:
            logger.warning("Supabase query failed for geothermal map data: %s", exc)
            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": 50.0,
                "metric": "geothermal_potential",
                "lat": 12.8797,
                "lon": 121.7740,
                "nearby_plants": [],
            })

        return items

    def _build_renewable_potential_map(self) -> list[dict[str, Any]]:
        """Aggregate municipality-level climate/terrain into
        province-level renewable potential scores."""
        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        try:
            # 1. Fetch provinces directly
            prov_resp = client.table("provinces").select(
                "province_id,name,lat,lon"
            ).limit(10000).execute()
            prov_rows = prov_resp.data or []

            # 2. Fetch hydropower suitability scores
            hydro_resp = client.table("hydropower_suitability").select(
                "province,municipality_name,hydro_suitability_score"
            ).limit(10000).execute()
            hydro_rows = hydro_resp.data or []

            # 2b. Fetch geothermal suitability scores
            geo_resp = client.table("geothermal_suitability").select(
                "municipality_id,geothermal_score"
            ).limit(10000).execute()
            geo_rows = geo_resp.data or []

            # 3. Fetch municipality → province mapping
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id"
            ).limit(10000).execute()
            muni_rows = muni_resp.data or []

            # 4. Fetch raw climate data (dataset is for 2010)
            climate_resp = client.table("municipality_climate_monthly").select(
                "municipality_id,allsky_sfc_sw_dwn,ws10m"
            ).eq("year", 2010).limit(10000).execute()
            climate_rows = climate_resp.data or []

            # Build mappings
            muni_to_prov = {m["municipality_id"]: m["province_id"] for m in muni_rows}

            # Aggregate climate by province_id
            prov_climate = defaultdict(lambda: {"solar": [], "wind": []})
            for row in climate_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is not None:
                    prov_climate[pid]["solar"].append(float(row.get("allsky_sfc_sw_dwn") or 0))
                    prov_climate[pid]["wind"].append(float(row.get("ws10m") or 0))

            # Aggregate hydro by province name
            hydro_by_prov: dict[str, list[float]] = {}
            for row in hydro_rows:
                prov = row.get("province", "").strip().lower()
                if prov:
                    score = float(row.get("hydro_suitability_score") or 0)
                    hydro_by_prov.setdefault(prov, []).append(score)

            # Aggregate geothermal by province_id
            geo_by_prov: dict[int, list[float]] = {}
            for row in geo_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is not None:
                    score = float(row.get("geothermal_score") or 0)
                    geo_by_prov.setdefault(pid, []).append(score)

            # Build province data dict keyed by normalized name
            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                pname = p.get("name", "").strip()
                if not pid or not pname:
                    continue

                solar_vals = prov_climate.get(pid, {}).get("solar", [])
                wind_vals = prov_climate.get(pid, {}).get("wind", [])

                # Convert raw climate values to 0-100 suitability scores
                # Solar: 5.0 kWh/m²/day = excellent → 100
                solar_score = round(min((sum(solar_vals) / len(solar_vals)) / 5.0 * 100, 100), 2) if solar_vals else None
                # Wind: 7.0 m/s = good onshore wind → 100
                wind_score = round(min((sum(wind_vals) / len(wind_vals)) / 7.0 * 100, 100), 2) if wind_vals else None

                prov_lower = pname.lower()
                hydro_scores = hydro_by_prov.get(prov_lower, [])
                # hydro_suitability_score is stored 0-1 → convert to 0-100
                hydro_score = round((sum(hydro_scores) / len(hydro_scores)) * 100, 2) if hydro_scores else None

                geo_scores = geo_by_prov.get(pid, [])
                # geothermal_score is stored 0-1 → convert to 0-100
                geo_score = round((sum(geo_scores) / len(geo_scores)) * 100, 2) if geo_scores else None

                # Average only the renewable scores that have actual data
                available_scores = [
                    s for s in (solar_score, wind_score, hydro_score, geo_score)
                    if s is not None
                ]
                composite = round(sum(available_scores) / len(available_scores), 2) if available_scores else None

                province_data[pname.lower()] = {
                    "region": "",
                    "province": pname,
                    "value": composite,
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                }

            # 5. Load GeoJSON to ensure every rendered province has data
            geojson_provinces: list[dict[str, Any]] = _get_geojson_province_names()

            # Build final items: for each GeoJSON province, find matching API data
            seen = set()
            for gp in geojson_provinces:
                gname = gp["name_lower"]
                if gname in seen:
                    continue
                seen.add(gname)

                # Direct match
                data = province_data.get(gname)

                # Try mapped names
                if not data:
                    for api_name, geo_name in _PROVINCE_NAME_MAP.items():
                        if geo_name.lower() == gname and api_name in province_data:
                            data = province_data[api_name]
                            break

                if data:
                    items.append({
                        "region": data["region"],
                        "province": gp["name"],  # Use GeoJSON name for frontend matching
                        "municipality": None,
                        "value": data["value"],
                        "metric": "renewable_potential",
                        "lat": data["lat"],
                        "lon": data["lon"],
                    })
                else:
                    # Missing from database — mark as no data
                    items.append({
                        "region": "",
                        "province": gp["name"],
                        "municipality": None,
                        "value": None,
                        "metric": "renewable_potential",
                        "lat": None,
                        "lon": None,
                    })

        except Exception as exc:
            logger.warning("Supabase query failed for map data: %s", exc)
            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": 50.0,
                "metric": "renewable_potential",
                "lat": 12.8797,
                "lon": 121.7740,
            })

        return items

    def _build_province_metric_map(
        self,
        column_prefix: str,
        metric_name: str,
    ) -> list[dict[str, Any]]:
        """Aggregate municipality suitability scores up to province level.

        Uses the pre-computed municipality scores from Supabase and Redis,
        averages them per province, and matches the result to GeoJSON province
        names. Aggregated factor values are also returned so map explanations
        can cite representative terrain/climate numbers.
        """
        muni_items = self._build_municipality_potential_map(column_prefix)

        client = get_supabase_client()
        try:
            prov_resp = client.table("provinces").select(
                "province_id,name,geojson_name,lat,lon"
            ).limit(10000).execute()
            prov_rows = (prov_resp.data or [])
        except Exception as exc:
            logger.warning("Supabase query failed for province metric map: %s", exc)
            prov_rows = []

        province_by_id: dict[int, dict[str, Any]] = {
            p["province_id"]: p for p in prov_rows if p.get("province_id")
        }

        # Group municipality data by province_id
        prov_scores: dict[int, list[float]] = {}
        prov_lats: dict[int, list[float]] = {}
        prov_lons: dict[int, list[float]] = {}
        prov_factors: dict[int, list[Any]] = {}
        prov_names: dict[int, str] = {}

        for item in muni_items:
            pid = item.get("province_id")
            if pid is None:
                continue
            value = item.get("value")
            if value is None:
                continue
            prov_names[pid] = item.get("province") or province_by_id.get(pid, {}).get("name", "")
            prov_scores.setdefault(pid, []).append(float(value))
            lat = item.get("lat")
            lon = item.get("lon")
            if lat is not None and lon is not None:
                prov_lats.setdefault(pid, []).append(float(lat))
                prov_lons.setdefault(pid, []).append(float(lon))
            factors = item.get("factors")
            if factors:
                prov_factors.setdefault(pid, []).append(factors)

        # Build province data keyed by normalized name
        province_data: dict[str, dict[str, Any]] = {}
        for pid, scores in prov_scores.items():
            avg = round(sum(scores) / len(scores), 2) if scores else None
            province = prov_names.get(pid, province_by_id.get(pid, {}).get("name", "")).strip()
            if not province:
                continue

            lats = prov_lats.get(pid, [])
            lons = prov_lons.get(pid, [])
            lat = round(sum(lats) / len(lats), 6) if lats else province_by_id.get(pid, {}).get("lat")
            lon = round(sum(lons) / len(lons), 6) if lons else province_by_id.get(pid, {}).get("lon")

            facts = self._aggregate_factors(prov_factors.get(pid, []))
            classification = _classify_score(avg)

            province_data[province.lower()] = {
                "region": "",
                "province": province,
                "municipality": None,
                "municipality_id": None,
                "value": avg,
                "classification": classification,
                "factors": facts,
                "metric": metric_name,
                "lat": lat,
                "lon": lon,
                "nearby_plants": [],
            }

            # Also index by geojson_name if different
            geojson_name = province_by_id.get(pid, {}).get("geojson_name", "").strip()
            if geojson_name and geojson_name.lower() != province.lower():
                province_data[geojson_name.lower()] = province_data[province.lower()]

        # Match to GeoJSON province names
        geojson_provinces: list[dict[str, Any]] = _get_geojson_province_names()
        items: list[dict[str, Any]] = []
        seen = set()
        for gp in geojson_provinces:
            gname = gp["name_lower"]
            if gname in seen:
                continue
            seen.add(gname)

            data = province_data.get(gname)
            if not data:
                for api_name, geo_name in _PROVINCE_NAME_MAP.items():
                    if geo_name.lower() == gname and api_name in province_data:
                        data = province_data[api_name]
                        break

            if data:
                items.append({
                    "region": data["region"],
                    "province": gp["name"],
                    "municipality": None,
                    "municipality_id": None,
                    "value": data["value"],
                    "classification": data["classification"],
                    "factors": data["factors"],
                    "metric": data["metric"],
                    "lat": data["lat"],
                    "lon": data["lon"],
                    "nearby_plants": data["nearby_plants"],
                })
            else:
                items.append({
                    "region": "",
                    "province": gp["name"],
                    "municipality": None,
                    "municipality_id": None,
                    "value": None,
                    "classification": None,
                    "factors": None,
                    "metric": metric_name,
                    "lat": None,
                    "lon": None,
                    "nearby_plants": [],
                })

        return items

    def _aggregate_factors(self, factors_list: list[Any]) -> dict[str, Any]:
        """Average numeric values across a list of factor JSON objects."""
        if not factors_list:
            return {}

        numeric_sums: dict[str, list[float]] = {}
        for raw in factors_list:
            parsed = raw
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                except Exception:
                    continue
            if not isinstance(parsed, dict):
                continue
            for key, value in parsed.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_sums.setdefault(key, []).append(float(value))

        if not numeric_sums:
            return {"_aggregation": "province-level average"}

        return {
            **{
                key: round(sum(vals) / len(vals), 4)
                for key, vals in numeric_sums.items()
            },
            "_aggregation": "province-level average",
        }

    def _apply_geothermal_boost(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply proximity boost and nearby_plants to municipality items."""
        for item in items:
            lat = item.get("lat")
            lon = item.get("lon")
            value = item.get("value", 0)
            factors = item.get("factors")
            if lat is None or lon is None:
                continue
            boosted, nearby = calculate_proximity_boost(
                float(lat), float(lon), float(value)
            )
            item["value"] = boosted
            item["nearby_plants"] = nearby
            if nearby and factors is not None:
                plant_names = ", ".join(
                    f"{p.get('project_name', 'Plant')} ({p.get('capacity_mw', '?')} MW)"
                    for p in nearby[:3]
                )
                note = f"Near operating geothermal plant(s): {plant_names}."
                try:
                    parsed = json.loads(factors)
                    if isinstance(parsed, dict):
                        parsed["nearby_plants"] = note
                        item["factors"] = json.dumps(parsed)
                except Exception:
                    item["factors"] = f"{factors}\n{note}" if factors else note
        return items

    def _build_municipality_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:
        """Return pre-computed municipality suitability scores from Supabase.

        Uses Redis cache first, then falls back to the municipalities table.
        """
        metric_name = f"{column_prefix}_potential" if column_prefix != "composite" else "renewable_potential"
        cached = get_suitability_cache_sync(metric_name, "municipality")
        if cached:
            logger.info("Cache hit for municipality %s suitability", metric_name)
            return cached  # type: ignore[return-value]

        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        score_col = f"{column_prefix}_suitability_score"
        class_col = f"{column_prefix}_classification"
        factors_col = f"{column_prefix}_factors"
        # composite_factors may not exist yet; omit from select if composite
        has_factors_col = column_prefix != "composite"
        select_cols = (
            f"municipality_id, name, province_id, lat, lon, "
            f"provinces(province_id, name), {score_col}, {class_col}"
        )
        if has_factors_col:
            select_cols += f", {factors_col}"

        try:
            resp = (
                client.table("municipalities")
                .select(select_cols)
                .not_.is_(score_col, "null")
                .execute()
            )
            rows = resp.data or []
            for r in rows:
                province_obj = r.get("provinces") or {}
                province_name = province_obj.get("name") or r.get("province_name", "")
                province_id = province_obj.get("province_id") or r.get("province_id")
                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": r.get("name"),
                    "municipality_id": r.get("municipality_id"),
                    "province_id": province_id,
                    "value": float(r.get(score_col) or 0),
                    "classification": r.get(class_col),
                    "factors": r.get(factors_col) if has_factors_col else None,
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                    "nearby_plants": [],
                })

            # Apply geothermal proximity boost after building items
            if column_prefix == "geothermal":
                items = self._apply_geothermal_boost(items)

            # Cache results for fast repeat loads (geothermal included)
            set_suitability_cache_sync(metric_name, "municipality", items)
        except Exception as exc:
            logger.warning("Supabase query failed for municipality map data: %s", exc)

        return items

    def _build_barangay_potential_map(self, column_prefix: str) -> list[dict[str, Any]]:
        """Build barangay-level suitability map by inheriting parent municipality scores.

        Barangays don't have their own suitability scores — they inherit
        from their parent municipality. Centroids come from geospatial_metadata
        or barangays.lat/lon as fallback.
        """
        metric_name = f"{column_prefix}_potential" if column_prefix != "composite" else "renewable_potential"
        cached = get_suitability_cache_sync(metric_name, "barangay")
        if cached and column_prefix != "geothermal":
            logger.info("Cache hit for barangay %s suitability", metric_name)
            return cached  # type: ignore[return-value]

        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        score_col = f"{column_prefix}_suitability_score"
        class_col = f"{column_prefix}_classification"

        try:
            # Fetch barangays with parent municipality info
            select_cols = (
                f"barangay_id, name, municipality_id, lat, lon, "
                f"municipalities(name, province_id, {score_col}, {class_col}, provinces(name))"
            )
            resp = (
                client.table("barangays")
                .select(select_cols)
                .limit(50000)
                .execute()
            )
            rows = resp.data or []

            for r in rows:
                muni = r.get("municipalities")
                if not muni:
                    continue
                score = muni.get(score_col)
                if score is None:
                    continue

                prov_obj = muni.get("provinces")
                province_name = prov_obj.get("name", "") if prov_obj else ""

                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": muni.get("name"),
                    "barangay": r.get("name"),
                    "barangay_id": r.get("barangay_id"),
                    "value": float(score),
                    "classification": muni.get(class_col),
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                    "nearby_plants": [],
                })

            if column_prefix != "geothermal" and items:
                set_suitability_cache_sync(metric_name, "barangay", items)

        except Exception as exc:
            logger.warning("Supabase query failed for barangay map data: %s", exc)

        return items

    # --- AI Insight ---

    def get_ai_insight(self, use_llm: bool = False) -> dict[str, str]:
        if use_llm:
            return self._generate_llm_insight()
        return self._ml.get_ai_insight()

    # --- Map Explanations ---

    VALID_MAP_METRICS = frozenset({
        "renewable_potential",
        "solar_potential",
        "wind_potential",
        "hydro_potential",
        "geothermal_potential",
    })

    def get_map_explanation(
        self,
        metric: str,
        level: str = "province",
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Generate a Groq-powered, data-grounded explanation for the current map."""
        if metric not in self.VALID_MAP_METRICS:
            return self._static_map_explanation(metric, error=f"Unknown metric: {metric}")

        map_data = self.build_map_data(metric, level)
        summary = self._summarize_map_data(map_data, metric, level)
        chart_type = f"map_{metric}"
        chart_hash = self._hash_chart_data(summary)

        if not force_refresh:
            cached = self._get_cached_insight(chart_type, chart_hash)
            if cached:
                logger.info("Cache hit for map %s (hash=%s)", metric, chart_hash[:8])
                return _sanitize_nan({
                    "insight": cached,
                    "recommendation": "",
                    "data_year": 2024,
                    "chart_type": chart_type,
                })

        try:
            from app.services.llm_client import generate_response
        except Exception:
            logger.warning("LLM client not available; falling back to static map explanation.")
            return self._static_map_explanation(metric)

        prompt = self._build_chart_prompt(chart_type, summary)
        try:
            text = generate_response(
                prompt,
                temperature=0.5,
                max_output_tokens=2000,
            )
        except Exception as exc:
            logger.warning("LLM call failed for map explanation: %s", exc)
            return self._static_map_explanation(metric)

        cleaned = self._clean_llm_text(text)
        self._cache_insight(chart_type, chart_hash, cleaned)

        return _sanitize_nan({
            "insight": cleaned,
            "recommendation": "",
            "data_year": 2024,
            "chart_type": chart_type,
        })

    def _static_map_explanation(
        self,
        metric: str,
        error: str | None = None,
    ) -> dict[str, Any]:
        base = _MAP_EXPLANATION_FALLBACKS.get(metric, "")
        if error:
            base = f"{error}. {base}" if base else error
        return _sanitize_nan({
            "insight": base,
            "recommendation": "",
            "data_year": 2024,
            "chart_type": f"map_{metric}",
        })

    def _summarize_map_data(
        self,
        map_data: dict[str, Any],
        metric: str,
        level: str,
    ) -> dict[str, Any]:
        """Build a compact, deterministic summary of map data for the LLM prompt.

        The summary is also the cache key, so changing values, factors, or nearby
        plants/volcanoes automatically invalidates the cached explanation.
        """
        items: list[dict[str, Any]] = map_data.get("items") or []

        distribution: dict[str, int] = {}
        values: list[float] = []
        for item in items:
            value = item.get("value")
            if value is None:
                continue
            values.append(float(value))
            cls = _classify_score(float(value))
            distribution[cls] = distribution.get(cls, 0) + 1

        avg = round(sum(values) / len(values), 2) if values else None
        min_val = round(min(values), 2) if values else None
        max_val = round(max(values), 2) if values else None

        # Pick deterministic examples by value tiers.
        sorted_items = sorted(
            [i for i in items if i.get("value") is not None],
            key=lambda x: float(x["value"]),
            reverse=True,
        )
        high_examples = sorted_items[:3]
        low_examples = sorted_items[-3:][::-1]
        moderate_examples = [i for i in sorted_items if 41 <= float(i.get("value", 0)) <= 60][:3]

        def _example(item: dict[str, Any]) -> dict[str, Any]:
            ex: dict[str, Any] = {
                "name": item.get("municipality") or item.get("province") or "Unknown",
                "province": item.get("province"),
                "value": float(item["value"]),
                "classification": _classify_score(float(item["value"])),
            }
            factors = item.get("factors")
            if factors:
                if isinstance(factors, str):
                    try:
                        factors = json.loads(factors)
                    except Exception:
                        factors = {"details": factors}
                if isinstance(factors, dict):
                    # Limit each factors object to keep prompts small.
                    ex["factors"] = {k: v for k, v in factors.items() if v is not None}
            nearby_plants = item.get("nearby_plants")
            if nearby_plants:
                ex["nearby_plants"] = [
                    {
                        "project_name": p.get("project_name", ""),
                        "capacity_mw": p.get("capacity_mw"),
                        "technology": p.get("technology"),
                        "status": p.get("status"),
                        "distance_km": p.get("distance_km"),
                    }
                    for p in nearby_plants[:2]
                ]
            return _sanitize_nan(ex)

        summary = _sanitize_nan({
            "metric": metric,
            "level": level,
            "count": len(items),
            "with_data": len(values),
            "score_avg": avg,
            "score_min": min_val,
            "score_max": max_val,
            "distribution": distribution,
            "high_examples": [_example(i) for i in high_examples],
            "moderate_examples": [_example(i) for i in moderate_examples],
            "low_examples": [_example(i) for i in low_examples],
            "volcano_count": len(_load_volcanoes()) if metric in ("geothermal_potential", "renewable_potential") else 0,
            "plant_count": len(get_all_ph_geothermal_plants()) if metric in ("geothermal_potential", "renewable_potential") else 0,
            "sources": self._map_data_sources(metric),
        })

        # Add nearest volcano and plant for each moderate/low example when relevant.
        if metric in ("geothermal_potential", "renewable_potential"):
            volcanoes = _load_volcanoes()
            for ex in summary.get("moderate_examples", []) + summary.get("low_examples", []) + summary.get("high_examples", []):
                lat = self._lookup_item_lat_lon(items, ex["name"])
                if lat is not None:
                    nearest = self._nearest_geo_feature(lat[0], lat[1], volcanoes)
                    if nearest:
                        ex["nearest_volcano"] = nearest

        return summary

    def _map_data_sources(self, metric: str) -> list[str]:
        """Citations for the prompt; these must match actual repo resources."""
        base = ["municipalities table", "provinces table"]
        if metric == "geothermal_potential":
            base.extend([
                "geothermal_suitability table",
                "fastapi-backend/app/services/geothermal/plants.py",
                "fastapi-backend/app/services/local_data/geothermal_volcanoes.json",
                "GeothermalDatasets/philippine_volcanoes.csv",
            ])
        elif metric == "hydro_potential":
            base.extend([
                "hydropower_suitability table",
                "municipalities.hydro_factors",
                "regionalData/output/terrain_metrics/hydropower_suitability.csv",
                "fastapi-backend/app/services/hydro_output_calc.py",
            ])
        elif metric == "solar_potential":
            base.extend([
                "municipality_climate_monthly table",
                "fastapi-backend/app/services/local_data/",
            ])
        elif metric == "wind_potential":
            base.extend([
                "municipality_climate_monthly table",
            ])
        elif metric == "renewable_potential":
            base.extend([
                "municipality_climate_monthly table",
                "hydropower_suitability table",
                "geothermal_suitability table",
                "municipalities.solar_suitability_score",
                "municipalities.wind_suitability_score",
                "municipalities.hydro_suitability_score",
                "municipalities.geothermal_suitability_score",
            ])
        return base

    def _lookup_item_lat_lon(
        self,
        items: list[dict[str, Any]],
        name: str,
    ) -> tuple[float, float] | None:
        for item in items:
            if (item.get("municipality") or item.get("province")) == name:
                lat = item.get("lat")
                lon = item.get("lon")
                if lat is not None and lon is not None:
                    return float(lat), float(lon)
        return None

    def _nearest_geo_feature(
        self,
        lat: float,
        lon: float,
        features: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        import math
        nearest = None
        nearest_dist = float("inf")
        for f in features:
            flat = f.get("lat")
            flon = f.get("lon")
            if flat is None or flon is None:
                continue
            dlat = math.radians(flat - lat)
            dlon = math.radians(flon - lon)
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat)) * math.cos(math.radians(flat)) * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist = 6371.0 * c
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = {**f, "distance_km": round(dist, 1)}
        return nearest

    def analyze_chart(self, chart_type: str, chart_data: dict[str, Any], force_refresh: bool = False) -> dict[str, str]:
        """Generate an LLM-powered explanation for a specific chart with DB caching and rotation."""
        chart_hash = self._hash_chart_data(chart_data)

        # 1. Check cache (unless force refresh)
        if not force_refresh:
            cached = self._get_cached_insight(chart_type, chart_hash)
            if cached:
                logger.info("Cache hit for chart %s (hash=%s)", chart_type, chart_hash[:8])
                return {
                    "insight": cached,
                    "recommendation": "",
                    "data_year": chart_data.get("latest_year", 2024),
                    "chart_type": chart_type,
                }

        # 2. Call LLM
        try:
            from app.services.llm_client import generate_response
        except Exception:
            logger.warning("LLM client not available; falling back to static insight.")
            return self._ml.get_ai_insight()

        prompt = self._build_chart_prompt(chart_type, chart_data)
        try:
            text = generate_response(prompt, temperature=0.5, max_output_tokens=2000)
        except Exception as exc:
            logger.warning("LLM call failed for chart analysis: %s", exc)
            return self._ml.get_ai_insight()

        cleaned = self._clean_llm_text(text)

        # 3. Store in cache
        self._cache_insight(chart_type, chart_hash, cleaned)

        return {
            "insight": cleaned,
            "recommendation": "",
            "data_year": chart_data.get("latest_year", 2024),
            "chart_type": chart_type,
        }

    def _hash_chart_data(self, chart_data: dict[str, Any]) -> str:
        """Stable hash for chart data so identical inputs share cache.

        Includes a prompt version so changes to tokens/prompts invalidate old cache.
        """
        import hashlib, json
        canonical = json.dumps(
            {"data": chart_data, "prompt_version": self.PROMPT_VERSION},
            sort_keys=True,
            default=str,
        )
        return hashlib.md5(canonical.encode()).hexdigest()

    def _get_cached_insight(self, chart_type: str, chart_hash: str) -> str | None:
        """Fetch a cached insight; if multiple exist, rotate randomly."""
        client = get_supabase_client()
        try:
            resp = (
                client.table("chart_ai_insights")
                .select("insight")
                .eq("chart_type", chart_type)
                .eq("chart_data_hash", chart_hash)
                .execute()
            )
            rows = resp.data or []
            if not rows:
                return None
            # Rotate: pick one at random from cached variants
            import random
            return random.choice(rows)["insight"]
        except Exception as exc:
            logger.debug("Cache read failed (table may not exist yet): %s", exc)
            return None

    def _cache_insight(self, chart_type: str, chart_hash: str, insight: str) -> None:
        """Store a new LLM insight in the cache. Keeps up to 3 variants per chart+hash."""
        client = get_supabase_client()
        try:
            # Count existing variants
            count_resp = (
                client.table("chart_ai_insights")
                .select("id", count="exact")
                .eq("chart_type", chart_type)
                .eq("chart_data_hash", chart_hash)
                .execute()
            )
            existing = count_resp.count or 0
            if existing >= 3:
                # Evict oldest to keep cache bounded
                oldest = (
                    client.table("chart_ai_insights")
                    .select("id")
                    .eq("chart_type", chart_type)
                    .eq("chart_data_hash", chart_hash)
                    .order("created_at")
                    .limit(1)
                    .execute()
                )
                if oldest.data:
                    old_id = oldest.data[0]["id"]
                    client.table("chart_ai_insights").delete().eq("id", old_id).execute()
            client.table("chart_ai_insights").insert({
                "chart_type": chart_type,
                "chart_data_hash": chart_hash,
                "insight": insight,
            }).execute()
        except Exception as exc:
            logger.debug("Cache write failed (table may not exist yet): %s", exc)

    def _generate_llm_insight(self) -> dict[str, str]:
        """Generate a comprehensive LLM insight from all energy data."""
        try:
            from app.services.llm_client import generate_response
        except Exception:
            logger.warning("LLM client not available; falling back to static insight.")
            return self._ml.get_ai_insight()

        latest = self._ml.get_latest_statistics()
        forecast = self._ml.get_forecast("consumption")
        source = self._ml.get_source_breakdown()

        forecast_values = forecast.get("forecast_values") or []
        f_2030 = forecast_values[-1] if forecast_values else 0
        consumption = latest.get("total_consumption_gwh", 0) or 0
        forecast_growth = ((f_2030 / consumption) - 1) * 100 if consumption else 0.0

        prompt = (
            "You are LUMI, an Environmental Intelligence assistant for Philippine energy data.\n"
            "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
            f"Latest Year: {latest.get('year', 2024)}\n"
            f"Total Consumption: {latest.get('total_consumption_gwh', 0):,.0f} GWh\n"
            f"Total Peak Demand: {latest.get('total_peak_demand_mw', 0):,.0f} MW\n"
            f"Renewable Share: {latest.get('renewable_share_pct', 0)}%\n"
            f"Capacity Margin: {latest.get('capacity_margin_pct', 0)}%\n\n"
            f"ARIMA Forecast 2030: {f_2030:,.0f} GWh\n"
            f"Forecast Growth: {forecast_growth:.1f}%\n\n"
            "Generation Mix (2024):\n"
        )
        for src, pct in source.get("share_pct", {}).items():
            prompt += f"  - {src}: {pct}%\n"

        prompt += (
            "\nProvide a SHORT, PRESCRIPTIVE analysis in 2-3 short paragraphs.\n"
            "Each paragraph must end with 1-2 concrete, specific recommendations (what should be done, by whom, and by when).\n"
            "Do NOT invent numbers that are not in the data above. Do NOT return JSON or code blocks.\n"
            "Finish with a complete sentence. Do not end with an ellipsis or partial thought.\n"
            "Use plain language suitable for students and communities."
        )

        try:
            text = generate_response(prompt, temperature=0.3, max_output_tokens=3000)
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            return self._ml.get_ai_insight()

        cleaned = self._clean_llm_text(text)
        return {
            "insight": cleaned,
            "recommendation": "",
            "data_year": latest.get("year", 2024),
        }

    @staticmethod
    def _clean_llm_text(text: str) -> str:
        """Strip JSON wrappers, markdown fences, and clean LLM output for display.

        Delegates to the unified llm_sanitizer module.
        """
        from app.services.llm_sanitizer import clean_ai_output
        return clean_ai_output(text)

    def _build_chart_prompt(self, chart_type: str, chart_data: dict[str, Any]) -> str:
        if chart_type == "trends":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast = chart_data.get("forecast", [])
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine energy consumption trend in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                f"Historical years: {years[:5]}...{years[-3:]}\n"
                f"Consumption (GWh): {consumption[:5]}...{consumption[-3:]}\n"
                f"Forecast: {forecast}\n\n"
                "Cover:\n"
                "1) Identify key consumption patterns and prescribe immediate demand-side management or efficiency programs.\n"
                "2) Flag inflection points and prescribe policy responses or infrastructure investments needed.\n"
                "3) Translate the forecast into concrete grid planning actions with timelines for the DOE and NGCP."
            )
        if chart_type == "consumption_trend":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast_years = chart_data.get("forecast_years", [])
            forecast_values = chart_data.get("forecast_values", [])
            latest = consumption[-1] if consumption else 0
            first = consumption[0] if consumption else 0
            growth = ((latest / first) - 1) * 100 if first else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine total energy consumption chart in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                f"Historical consumption (GWh): {consumption[:3]} ... {consumption[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Forecast: {forecast_values[0] if forecast_values else 'N/A'} GWh in {forecast_years[0] if forecast_years else 'N/A'} "
                f"to {forecast_values[-1] if forecast_values else 'N/A'} GWh in {forecast_years[-1] if forecast_years else 'N/A'}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} GWh = {growth:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Diagnose the growth trajectory and prescribe what the DOE and ERC should do now (policy, pricing, enforcement).\n"
                "2) Identify acceleration/deceleration phases and prescribe demand-side management or industrial efficiency programs.\n"
                "3) Compare to ASEAN benchmarks and prescribe specific capacity targets or import strategies.\n"
                "4) Translate the forecast into concrete grid planning and transmission investment priorities with timelines.\n"
                "5) Prescribe emergency and long-term actions to diversify the generation mix and improve energy security."
            )
        if chart_type == "peak_demand":
            years = chart_data.get("years", [])
            peak_demand = chart_data.get("peak_demand", [])
            latest = peak_demand[-1] if peak_demand else 0
            first = peak_demand[0] if peak_demand else 0
            growth = ((latest / first) - 1) * 100 if first else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine peak electricity demand chart in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                f"Peak demand (MW): {peak_demand[:3]} ... {peak_demand[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} MW = {growth:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Compare peak demand growth to installed capacity and prescribe immediate capacity additions or reserve contracts.\n"
                "2) Assess grid reliability risks and prescribe concrete brownout prevention measures for NGCP.\n"
                "3) Prescribe demand-side management programs and time-of-use pricing reforms with implementation steps.\n"
                "4) Recommend specific renewable + battery storage projects to displace peaker plants and reduce peak stress.\n"
                "5) Give a 5-year infrastructure roadmap with policy actions for the DOE and NGCP."
            )
        if chart_type == "renewable_generation":
            years = chart_data.get("years", [])
            renewable = chart_data.get("renewable_generation", [])
            total = chart_data.get("total_generation", [])
            latest_re = renewable[-1] if renewable else 0
            latest_total = total[-1] if total else 1
            share = (latest_re / latest_total) * 100 if latest_total else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine renewable energy generation chart in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                f"Renewable generation (GWh): {renewable[:3]} ... {renewable[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Total generation (GWh): {total[:3]} ... {total[-3:]}\n"
                f"Latest renewable share: {share:.1f}%\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Assess renewable growth pace and prescribe specific capacity targets and auction schedules to meet the 35% RE Act goal.\n"
                "2) Compare current share to the 35% target and prescribe regulatory reforms (permitting, grid access, FIT adjustments).\n"
                "3) Break down each renewable source and prescribe resource-specific investment priorities and locations.\n"
                "4) Identify financing gaps and prescribe blended finance instruments, green bonds, or development bank partnerships.\n"
                "5) Prescribe grid integration solutions, storage mandates, and transmission upgrades to handle intermittency."
            )
        if chart_type == "sources":
            shares = chart_data.get("shares", {})
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of the Philippine energy generation mix in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                + "\n".join([f"  - {k}: {v}%" for k, v in shares.items()])
                + "\n\nCover these points with actionable recommendations:\n"
                "1) Diagnose fossil fuel dominance and prescribe concrete coal phase-out milestones, natural gas transition plans, and replacement targets.\n"
                "2) Evaluate each renewable source and prescribe resource-specific procurement targets, auction volumes, and pipeline projects.\n"
                "3) Assess climate commitment gaps and prescribe NDC updates, carbon pricing, and just transition fund mechanisms.\n"
                "4) Identify decarbonization barriers and prescribe stranded asset mitigation strategies, flexible baseload contracts, and smart grid investments.\n"
                "5) Provide a decade-by-decade action roadmap with specific 2030, 2035, and 2040 milestones for reaching 50% renewables."
            )
        if chart_type.startswith("map_"):
            return self._build_map_explanation_prompt(chart_data)

        # Generic legacy map prompt (kept for backward compatibility)
        if chart_type == "map":
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine province-level renewable potential map in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations. Do NOT return JSON, code blocks, or raw data dumps. Finish with a complete sentence; do not end with an ellipsis or partial thought.\n\n"
                "Scores are based on solar irradiance (40%), wind speed (30%), and hydropower suitability (30%).\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Explain regional score variations and prescribe priority zones for solar parks, wind farms, and micro-hydro installations.\n"
                "2) Prescribe how the DOE and NREB should use this map for competitive RE auctions, zoning, and transmission planning.\n"
                "3) Recommend specific actions for LGUs (local government units), investors, and host communities to develop high-potential sites.\n"
                "4) Identify data limitations and prescribe additional surveys (LiDAR wind, streamflow gauging, grid capacity mapping).\n"
                "5) Prescribe how to integrate these scores into the Philippine Energy Plan with concrete capacity targets per region."
            )
        return "Provide a brief energy insight based on the available data."

    def _build_map_explanation_prompt(self, chart_data: dict[str, Any]) -> str:
        """Build a data-grounded prompt for map_* chart types."""
        metric = chart_data.get("metric", "unknown")
        summary_json = json.dumps(chart_data, indent=2, default=str)[:4000]

        if metric == "geothermal_potential":
            focus = (
                "Focus on why some areas that are close to volcanoes or operating geothermal plants still show only moderate suitability. "
                "Explain that surface volcanism is only one requirement; a viable geothermal resource also needs a hot, permeable reservoir and accessible terrain, which is why not every nearby location is high. "
                "Use the specific nearby plants and nearest volcano for the moderate/low examples."
            )
        elif metric == "hydro_potential":
            focus = (
                "Focus on why some areas with a lot of surface water or gentle, wet terrain can still show low or medium suitability. "
                "Explain that hydropower output depends on hydraulic head and watershed gradient, not just water presence, so flat or low-lying areas with water can have low scores. "
                "Use the hydraulic_head, watershed_gradient, and slope fields in the examples."
            )
        elif metric == "solar_potential":
            focus = (
                "Explain that the score is driven by solar irradiance and clear-sky conditions, not by proximity to volcanoes or water. "
                "Why can some volcanic or coastal regions still be moderate? Because terrain shading, cloud cover, or lower irradiance can lower the score."
            )
        elif metric == "wind_potential":
            focus = (
                "Explain that the score is driven by sustained wind speed and exposure. "
                "Areas near volcanoes or water can still be moderate if wind speeds or terrain exposure are not consistently high."
            )
        elif metric == "renewable_potential":
            focus = (
                "Explain that this is a composite of solar, wind, hydropower, and geothermal suitability. "
                "A region near volcanoes or water can still be moderate because the composite is pulled down by any lower-scoring source; for example, good geothermal proximity may be offset by average solar, limited hydro head, or modest wind."
            )
        else:
            focus = "Explain the score distribution and why some locations may be moderate or low."

        return (
            "You are LUMI, an Environmental Intelligence assistant for Philippine renewable energy data.\n"
            "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
            "Write a concise, plain-language explanation (150–250 words) for the map shown. "
            "Your explanation must be descriptive and interpretive, not prescriptive. "
            "Do not use litotes (e.g., do not write 'not uncommon', 'not impossible', or 'not far'). "
            "Do not invent data that is not in the provided context. Cite the listed data sources by name or file path.\n\n"
            f"Metric: {metric}\n"
            f"Geographic level: {chart_data.get('level')}\n"
            f"Total locations: {chart_data.get('count')}\n"
            f"Locations with data: {chart_data.get('with_data')}\n"
            f"Average score (observed in this view): {chart_data.get('score_avg')}\n"
            f"Observed score range in this view: {chart_data.get('score_min')} to {chart_data.get('score_max')}\n"
            "Important: all scores are on a 0–100 scale. The observed score range is the minimum and maximum in the current data, not the maximum possible score.\n\n"
            f"Score distribution by class:\n{json.dumps(chart_data.get('distribution', {}), indent=2)}\n\n"
            f"Representative examples:\n{summary_json}\n\n"
            f"Focus for this explanation:\n{focus}\n\n"
            "Cite the data sources listed in the examples. If you mention a specific place, use only the names and values shown above. "
            "End with a short 'Sources' line naming the files or tables you used."
        )

    # --- Provincial & Municipal Demand ---

    def get_provincial_consumption(self, region: str | None = None) -> dict[str, Any]:
        """Return DOE Annex 8 provincial/regional consumption."""
        data = self._ml.get_provincial_consumption(region)
        return {
            "items": data.get("items", []),
            "region": region,
            "note": "Values in MWh from DOE Annex 8 (2025).",
        }

    def estimate_municipal_demand(self, province_id: int) -> dict[str, Any]:
        """Estimate municipal demand via population-weighted disaggregation.

        Formula: D_muni = D_prov * (P_muni / P_prov)
        Requires PSA population data in the municipal_population table.
        """
        client = get_supabase_client()

        # 1. Fetch province total consumption from DOE v2
        prov_name_resp = (
            client.table("provinces")
            .select("name")
            .eq("province_id", province_id)
            .single()
            .execute()
        )
        if not prov_name_resp.data:
            return {"items": [], "province": None, "note": "Province not found."}
        province_name = prov_name_resp.data["name"]

        # Map province name to DOE region code (best-effort mapping)
        region_code = self._province_to_region_code(province_name)
        prov_data = self._ml.get_provincial_consumption(region_code)
        total_consumption_items = [
            item for item in prov_data.get("items", [])
            if item.get("sector") == "Total Consumption"
        ]
        if not total_consumption_items:
            return {
                "items": [],
                "province": province_name,
                "note": f"No DOE consumption data found for region {region_code}.",
            }
        total_consumption_mwh = float(total_consumption_items[0].get("value_mwh", 0))

        # 2. Fetch municipality populations
        try:
            pop_resp = (
                client.table("municipal_population")
                .select("municipality_id,population,municipalities(name)")
                .eq("province_id", province_id)
                .execute()
            )
            pop_rows = pop_resp.data or []
        except Exception:
            pop_rows = []

        if not pop_rows:
            return {
                "items": [],
                "province": province_name,
                "note": (
                    "PSA population data not yet loaded. "
                    "Municipal demand estimation requires municipal_population table."
                ),
            }

        total_pop = sum(r.get("population", 0) or 0 for r in pop_rows)
        if total_pop <= 0:
            return {
                "items": [],
                "province": province_name,
                "note": "Population data sums to zero.",
            }

        items = []
        for row in pop_rows:
            muni_pop = row.get("population", 0) or 0
            ratio = muni_pop / total_pop if total_pop > 0 else 0
            est_demand = total_consumption_mwh * ratio
            muni_name = (
                row.get("municipalities", {}).get("name")
                if isinstance(row.get("municipalities"), dict)
                else row.get("municipality_name", "Unknown")
            )
            items.append({
                "municipality_id": row.get("municipality_id"),
                "municipality_name": muni_name,
                "province_name": province_name,
                "estimated_demand_mwh": round(est_demand, 2),
                "method": "population_weighted_disaggregation",
                "note": "Estimated from provincial DOE data using PSA population ratios. Actual demand may vary.",
            })

        return {
            "items": items,
            "province": province_name,
            "note": f"Estimated for {len(items)} municipalities in {province_name}.",
        }

    @staticmethod
    def _province_to_region_code(province_name: str) -> str:
        """Best-effort mapping of province name to DOE region code.

        DOE Annex 8 uses region codes (I, II, III, IV-A, IV-B, V, VI,
        VII, VIII, IX, X, XI, XII, XIII, NCR, CAR, ARMM, NIR).
        """
        mapping = {
            "metro manila": "NCR",
            "ncr": "NCR",
            "abra": "CAR",
            "apayao": "CAR",
            "benguet": "CAR",
            "ifugao": "CAR",
            "kalinga": "CAR",
            "mountain province": "CAR",
            "ilocos norte": "I",
            "ilocos sur": "I",
            "la union": "I",
            "pangasinan": "I",
            "batanes": "II",
            "cagayan": "II",
            "isabela": "II",
            "nueva vizcaya": "II",
            "quirino": "II",
            "aurora": "III",
            "bataan": "III",
            "bulacan": "III",
            "nueva ecija": "III",
            "pampanga": "III",
            "tarlac": "III",
            "zambales": "III",
            "batangas": "IV-A",
            "cavite": "IV-A",
            "laguna": "IV-A",
            "quezon": "IV-A",
            "rizal": "IV-A",
            "marinduque": "IV-B",
            "occidental mindoro": "IV-B",
            "oriental mindoro": "IV-B",
            "palawan": "IV-B",
            "romblon": "IV-B",
            "albay": "V",
            "camarines norte": "V",
            "camarines sur": "V",
            "catanduanes": "V",
            "masbate": "V",
            "sorsogon": "V",
            "aklan": "VI",
            "antique": "VI",
            "capiz": "VI",
            "guimaras": "VI",
            "iloilo": "VI",
            "negros occidental": "VI",
            "bohol": "VII",
            "cebu": "VII",
            "negros oriental": "VII",
            "siargao": "XIII",
            "siquijor": "VII",
            "biliran": "VIII",
            "eastern samar": "VIII",
            "leyte": "VIII",
            "northern samar": "VIII",
            "samar": "VIII",
            "southern leyte": "VIII",
            "zamboanga del norte": "IX",
            "zamboanga del sur": "IX",
            "zamboanga sibugay": "IX",
            "bukidnon": "X",
            "camiguin": "X",
            "lanao del norte": "X",
            "misamis occidental": "X",
            "misamis oriental": "X",
            "compostela valley": "XI",
            "davao de oro": "XI",
            "davao del norte": "XI",
            "davao del sur": "XI",
            "davao occidental": "XI",
            "davao oriental": "XI",
            "cotabato": "XII",
            "sarangani": "XII",
            "south cotabato": "XII",
            "sultan kudarat": "XII",
            "agusan del norte": "XIII",
            "agusan del sur": "XIII",
            "dinagat islands": "XIII",
            "surigao del norte": "XIII",
            "surigao del sur": "XIII",
            "basilan": "ARMM",
            "lanao del sur": "ARMM",
            "maguindanao": "ARMM",
            "sulu": "ARMM",
            "tawi-tawi": "ARMM",
        }
        return mapping.get(province_name.lower().strip(), province_name)

    # --- IRENA Benchmarking ---

    def get_irena_capacity(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_irena_capacity(year)

    def get_irena_generation(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_irena_generation(year)

    def get_irena_renewable_share(self) -> dict[str, Any]:
        return self._ml.get_irena_renewable_share()

    def get_meralco_rate(self, year: int | None = None) -> dict[str, Any]:
        return self._ml.get_meralco_rate(year)

    def get_solar_atlas(self, location: str | None = None) -> dict[str, Any]:
        return self._ml.get_solar_atlas(location)

    def build_irena_overview(self) -> dict[str, Any]:
        """Combine capacity, generation, and renewable share for frontend benchmarking."""
        cap = self._ml.get_irena_capacity()
        gen = self._ml.get_irena_generation()
        share = self._ml.get_irena_renewable_share()
        return {
            "capacity": cap.get("items", []),
            "generation": gen.get("items", []),
            "renewable_share": share.get("items", []),
            "note": "Data from IRENA. Displayed alongside DOE for benchmarking purposes.",
        }


# Singleton
_energyhub_service: EnergyHubService | None = None


def get_energyhub_service() -> EnergyHubService:
    global _energyhub_service
    if _energyhub_service is None:
        _energyhub_service = EnergyHubService()
    return _energyhub_service
