import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.ml.predictor import get_energyhub_ml
from app.services.supabase_service import get_supabase_client
from app.services.redis_client import (
    get_suitability_cache_sync,
    set_suitability_cache_sync,
)

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parents[3] / "DOE_Data_Extracted"
_GEOJSON_DIR = Path(__file__).resolve().parents[3] / "philippine_geojson"

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


class EnergyHubService:
    """Business logic layer for the EnergyHub module.

    Bridges the ML predictor (offline ARIMA artifacts), Supabase
    geographic/climate data, and the REST API.
    """

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

        return {
            "latest": latest,
            "forecast_summary": forecast_summary,
            "model_comparison": comparison,
        }

    # --- Forecast ---

    def get_forecast(self, metric: str = "consumption") -> dict[str, Any]:
        return self._ml.get_forecast(metric)

    # --- Trends ---

    def build_trends(self) -> dict[str, Any]:
        historical = self._ml.get_historical_trends()
        forecast = self._ml.get_forecast("consumption")
        source_breakdown = self._ml.get_source_breakdown()
        grid_breakdown = self._ml.get_grid_breakdown()
        return {
            "years": historical["years"],
            "series": historical["series"],
            "forecast": forecast,
            "source_breakdown": source_breakdown,
            "grid_breakdown": grid_breakdown,
        }

    # --- Map Data ---

    def build_map_data(
        self,
        metric: str = "renewable_potential",
        level: str = "province",
    ) -> dict[str, Any]:
        """Build choropleth-ready data.

        Because the DOE dataset is national-level only, sub-national
        metrics are derived from:
        1. Existing Supabase climate / terrain tables (renewable potential).
        2. Grid-level generation shares (Luzon / Visayas / Mindanao)
           apportioned to regions based on known geographic membership.

        Args:
            metric: Metric to visualise.
            level: "province" or "municipality". Municipality level uses
                pre-computed suitability scores from the municipalities table.
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

        if metric in ("energy_consumption", "peak_demand", "generation"):
            # National only — return a single national point
            latest = self._ml.get_latest_statistics()
            value = latest.get("total_consumption_gwh", 0)
            if metric == "peak_demand":
                value = latest.get("total_peak_demand_mw", 0)
            elif metric == "generation":
                value = latest.get("total_generation_gwh", 0)

            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": round(value, 2),
                "metric": metric,
                "lat": 12.8797,
                "lon": 121.7740,
            })

        elif metric == "renewable_potential":
            # Province-level aggregation (backward compatible)
            items = self._build_renewable_potential_map()

        elif metric == "forecasted_demand":
            forecast = self._ml.get_forecast("consumption")
            f_2030 = forecast["forecast_values"][-1] if forecast.get("forecast_values") else 0
            items.append({
                "region": "Philippines",
                "province": None,
                "municipality": None,
                "value": round(f_2030, 2),
                "metric": metric,
                "lat": 12.8797,
                "lon": 121.7740,
            })

        elif metric == "geothermal_potential":
            items = self._build_geothermal_potential_map()

        return {"items": items, "metric": metric, "level": level}

    def _build_geothermal_potential_map(self) -> list[dict[str, Any]]:
        """Aggregate municipality-level geothermal scores to province level."""
        client = get_supabase_client()
        items: list[dict[str, Any]] = []

        try:
            prov_resp = client.table("provinces").select(
                "province_id,name,lat,lon"
            ).execute()
            prov_rows = prov_resp.data or []

            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id"
            ).execute()
            muni_rows = muni_resp.data or []

            geo_resp = client.table("geothermal_suitability").select(
                "municipality_id,geothermal_score"
            ).execute()
            geo_rows = geo_resp.data or []

            muni_to_prov = {m["municipality_id"]: m["province_id"] for m in muni_rows}

            prov_geo: dict[int, list[float]] = {}
            for row in geo_rows:
                mid = row.get("municipality_id")
                pid = muni_to_prov.get(mid)
                if pid is not None:
                    score = float(row.get("geothermal_score") or 0)
                    prov_geo.setdefault(pid, []).append(score)

            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                pname = p.get("name", "").strip()
                if not pid or not pname:
                    continue
                scores = prov_geo.get(pid, [0])
                avg = (sum(scores) / len(scores) * 100) if scores else 0
                province_data[pname.lower()] = {
                    "region": "",
                    "province": pname,
                    "value": round(avg, 2),
                    "lat": p.get("lat"),
                    "lon": p.get("lon"),
                }

            geojson_path = _GEOJSON_DIR / "philippine_geojson_file_per_region.json"
            geojson_provinces: list[dict[str, Any]] = []
            if geojson_path.exists():
                with open(geojson_path, "r", encoding="utf-8") as f:
                    geo_data = json.load(f)
                for feat in geo_data.get("features", []):
                    adm2 = (feat.get("properties", {}).get("adm2_en") or "").strip()
                    if adm2:
                        geojson_provinces.append({
                            "name": adm2,
                            "name_lower": adm2.lower(),
                        })

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
            ).execute()
            prov_rows = prov_resp.data or []

            # 2. Fetch hydropower suitability scores
            hydro_resp = client.table("hydropower_suitability").select(
                "province,municipality_name,hydro_suitability_score"
            ).execute()
            hydro_rows = hydro_resp.data or []

            # 2b. Fetch geothermal suitability scores
            geo_resp = client.table("geothermal_suitability").select(
                "municipality_id,geothermal_score"
            ).execute()
            geo_rows = geo_resp.data or []

            # 3. Fetch municipality → province mapping
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id"
            ).execute()
            muni_rows = muni_resp.data or []

            # 4. Fetch raw climate data (dataset is for 2010)
            climate_resp = client.table("municipality_climate_monthly").select(
                "municipality_id,allsky_sfc_sw_dwn,ws10m"
            ).eq("year", 2010).execute()
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
            geojson_path = _GEOJSON_DIR / "philippine_geojson_file_per_region.json"
            geojson_provinces: list[dict[str, Any]] = []
            if geojson_path.exists():
                with open(geojson_path, "r", encoding="utf-8") as f:
                    geo_data = json.load(f)
                for feat in geo_data.get("features", []):
                    adm2 = (feat.get("properties", {}).get("adm2_en") or "").strip()
                    if adm2:
                        geojson_provinces.append({
                            "name": adm2,
                            "name_lower": adm2.lower(),
                        })

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
            f"provinces(name), {score_col}, {class_col}"
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
                province_obj = r.get("provinces")
                province_name = province_obj.get("name", "") if province_obj else ""
                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": r.get("name"),
                    "municipality_id": r.get("municipality_id"),
                    "value": float(r.get(score_col) or 0),
                    "classification": r.get(class_col),
                    "factors": r.get(factors_col) if has_factors_col else None,
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                })
            set_suitability_cache_sync(metric_name, "municipality", items)
        except Exception as exc:
            logger.warning("Supabase query failed for municipality map data: %s", exc)

        return items

    # --- AI Insight ---

    def get_ai_insight(self, use_llm: bool = False) -> dict[str, str]:
        if use_llm:
            return self._generate_llm_insight()
        return self._ml.get_ai_insight()

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
            text = generate_response(prompt, temperature=0.5, max_output_tokens=2500)
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

    @staticmethod
    def _hash_chart_data(chart_data: dict[str, Any]) -> str:
        """Stable hash for chart data so identical inputs share cache."""
        import hashlib, json
        canonical = json.dumps(chart_data, sort_keys=True, default=str)
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

        prompt = (
            "You are LUMI, an Environmental Intelligence assistant for Philippine energy data.\n"
            "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
            f"Latest Year: {latest.get('year', 2024)}\n"
            f"Total Consumption: {latest.get('total_consumption_gwh', 0):,.0f} GWh\n"
            f"Total Peak Demand: {latest.get('total_peak_demand_mw', 0):,.0f} MW\n"
            f"Renewable Share: {latest.get('renewable_share_pct', 0)}%\n"
            f"Capacity Margin: {latest.get('capacity_margin_pct', 0)}%\n\n"
            f"ARIMA Forecast 2030: {forecast.get('forecast_values', [0])[-1]:,.0f} GWh\n"
            f"Forecast Growth: {(((forecast.get('forecast_values', [0])[-1] / latest.get('total_consumption_gwh', 1)) - 1) * 100):.1f}%\n\n"
            "Generation Mix (2024):\n"
        )
        for src, pct in source.get("share_pct", {}).items():
            prompt += f"  - {src}: {pct}%\n"

        prompt += (
            "\nProvide a comprehensive 5-paragraph response that is PRESCRIPTIVE and ACTION-ORIENTED, not just descriptive.\n"
            "Each paragraph must end with concrete, specific recommendations (what should be done, by whom, and by when).\n\n"
            "1. Diagnose the current energy situation (consumption, peak demand, capacity margin) and prescribe immediate actions for the DOE and NGCP.\n"
            "2. Evaluate the renewable energy share and generation mix, then recommend specific policy changes, feed-in tariffs, or regulatory reforms to accelerate RE adoption.\n"
            "3. Interpret the ARIMA 2030 forecast and prescribe infrastructure investments, transmission upgrades, and capacity additions with timelines.\n"
            "4. Identify barriers to decarbonization and prescribe risk-mitigation strategies for stranded assets, baseload transitions, and grid integration.\n"
            "5. Give a forward-looking action plan with specific, measurable steps for the DOE, NGCP, local government units, and private investors.\n"
            "Aim for 400–600 words. Use plain language suitable for students and communities, but include specific data points and actionable steps."
        )

        try:
            text = generate_response(prompt, temperature=0.3, max_output_tokens=2500)
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
        from app.services.llm_sanitizer import sanitize_llm_output
        return sanitize_llm_output(text)

    def _build_chart_prompt(self, chart_type: str, chart_data: dict[str, Any]) -> str:
        if chart_type == "trends":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast = chart_data.get("forecast", [])
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine energy consumption trend in 2-3 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
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
                "Provide a PRESCRIPTIVE analysis of this Philippine total energy consumption chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
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
                "Provide a PRESCRIPTIVE analysis of this Philippine peak electricity demand chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
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
                "Provide a PRESCRIPTIVE analysis of this Philippine renewable energy generation chart in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
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
                "Provide a PRESCRIPTIVE analysis of the Philippine energy generation mix in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                + "\n".join([f"  - {k}: {v}%" for k, v in shares.items()])
                + "\n\nCover these points with actionable recommendations:\n"
                "1) Diagnose fossil fuel dominance and prescribe concrete coal phase-out milestones, natural gas transition plans, and replacement targets.\n"
                "2) Evaluate each renewable source and prescribe resource-specific procurement targets, auction volumes, and pipeline projects.\n"
                "3) Assess climate commitment gaps and prescribe NDC updates, carbon pricing, and just transition fund mechanisms.\n"
                "4) Identify decarbonization barriers and prescribe stranded asset mitigation strategies, flexible baseload contracts, and smart grid investments.\n"
                "5) Provide a decade-by-decade action roadmap with specific 2030, 2035, and 2040 milestones for reaching 50% renewables."
            )
        if chart_type == "map":
            return (
                "You are LUMI, an Environmental Intelligence assistant.\n"
                "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
                "Provide a PRESCRIPTIVE analysis of this Philippine province-level renewable potential map in 4-5 short paragraphs.\n"
                "Each paragraph must end with 1-2 specific, actionable recommendations.\n\n"
                "Scores are based on solar irradiance (40%), wind speed (30%), and hydropower suitability (30%).\n\n"
                "Cover these points with actionable recommendations:\n"
                "1) Explain regional score variations and prescribe priority zones for solar parks, wind farms, and micro-hydro installations.\n"
                "2) Prescribe how the DOE and NREB should use this map for competitive RE auctions, zoning, and transmission planning.\n"
                "3) Recommend specific actions for LGUs (local government units), investors, and host communities to develop high-potential sites.\n"
                "4) Identify data limitations and prescribe additional surveys (LiDAR wind, streamflow gauging, grid capacity mapping).\n"
                "5) Prescribe how to integrate these scores into the Philippine Energy Plan with concrete capacity targets per region."
            )
        return "Provide a brief energy insight based on the available data."


# Singleton
_energyhub_service: EnergyHubService | None = None


def get_energyhub_service() -> EnergyHubService:
    global _energyhub_service
    if _energyhub_service is None:
        _energyhub_service = EnergyHubService()
    return _energyhub_service
