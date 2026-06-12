import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.ml.predictor import get_energyhub_ml
from app.services.supabase_service import get_supabase_client

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

    def build_map_data(self, metric: str = "renewable_potential") -> dict[str, Any]:
        """Build choropleth-ready data.

        Because the DOE dataset is national-level only, sub-national
        metrics are derived from:
        1. Existing Supabase climate / terrain tables (renewable potential).
        2. Grid-level generation shares (Luzon / Visayas / Mindanao)
           apportioned to regions based on known geographic membership.
        """
        items: list[dict[str, Any]] = []

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
            # Query Supabase for municipal climate averages and aggregate
            # to province / region level.
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

        return {"items": items, "metric": metric}

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

            # 3. Fetch municipality → province mapping
            muni_resp = client.table("municipalities").select(
                "municipality_id,province_id"
            ).execute()
            muni_rows = muni_resp.data or []

            # 4. Fetch raw climate data for 2023
            climate_resp = client.table("municipality_climate_monthly").select(
                "municipality_id,allsky_sfc_sw_dwn,ws10m"
            ).eq("year", 2023).execute()
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

            # Build province data dict keyed by normalized name
            province_data: dict[str, dict[str, Any]] = {}
            for p in prov_rows:
                pid = p.get("province_id")
                pname = p.get("name", "").strip()
                if not pid or not pname:
                    continue

                solar_vals = prov_climate.get(pid, {}).get("solar", [])
                wind_vals = prov_climate.get(pid, {}).get("wind", [])

                solar_avg = sum(solar_vals) / len(solar_vals) if solar_vals else 4.0
                wind_avg = sum(wind_vals) / len(wind_vals) if wind_vals else 3.0

                prov_lower = pname.lower()
                hydro_scores = hydro_by_prov.get(prov_lower, [0])
                hydro_avg = sum(hydro_scores) / len(hydro_scores) if hydro_scores else 0

                composite = (
                    (min(solar_avg / 6.0, 1.0) * 0.4)
                    + (min(wind_avg / 10.0, 1.0) * 0.3)
                    + (hydro_avg * 0.3)
                )
                composite = round(composite * 100, 2)

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
            "You are LUMI, an Environmental Intelligence assistant for Philippine energy data.\n\n"
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
            "\nProvide a comprehensive, in-depth 5-paragraph analysis:\n"
            "1. Summarize the current energy situation (consumption, peak demand, capacity margin) and place it in an ASEAN context.\n"
            "2. Discuss the renewable energy share, generation mix composition, and how each source has evolved.\n"
            "3. Analyze the ARIMA forecast implications for 2030 and what it means for infrastructure planning.\n"
            "4. Evaluate barriers to decarbonization including stranded assets, baseload needs, and grid constraints.\n"
            "5. Give forward-looking policy and investment recommendations for the DOE, NGCP, and local communities.\n"
            "Aim for 500–700 words. Use plain language suitable for students and communities, but include specific data points."
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
        """Strip JSON wrappers and clean LLM output for display."""
        text = text.strip()

        def _extract_text(obj) -> str:
            """Recursively extract all string values from a nested dict/list."""
            if isinstance(obj, str):
                return obj
            if isinstance(obj, list):
                parts = [_extract_text(item) for item in obj if item is not None]
                return "\n\n".join(p for p in parts if p)
            if isinstance(obj, dict):
                # Prefer narrative keys first
                for key in ("analysis", "insight", "explanation", "response", "text", "content", "result"):
                    if key in obj:
                        return _extract_text(obj[key])
                # Fallback: concatenate all values
                parts = [_extract_text(v) for v in obj.values() if v is not None]
                return "\n\n".join(p for p in parts if p)
            return str(obj) if obj is not None else ""

        # If the response is wrapped in a JSON object, extract the narrative content
        if text.startswith("{") and text.endswith("}"):
            try:
                import json
                parsed = json.loads(text)
                extracted = _extract_text(parsed)
                if extracted and len(extracted) > 20:
                    text = extracted
            except json.JSONDecodeError:
                pass

        # Normalize escaped newlines
        text = text.replace("\\n", "\n").replace("\\t", "\t")
        # Remove remaining JSON artifact braces if any
        text = text.strip()
        return text

    def _build_chart_prompt(self, chart_type: str, chart_data: dict[str, Any]) -> str:
        if chart_type == "trends":
            years = chart_data.get("years", [])
            consumption = chart_data.get("consumption", [])
            forecast = chart_data.get("forecast", [])
            return (
                "Explain the following Philippine energy consumption trend in 2-3 short paragraphs:\n"
                f"Historical years: {years[:5]}...{years[-3:]}\n"
                f"Consumption (GWh): {consumption[:5]}...{consumption[-3:]}\n"
                f"Forecast: {forecast}\n"
                "Highlight key patterns, inflection points, and what the forecast implies."
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
                "You are LUMI, an Environmental Intelligence assistant. Provide a deep, in-depth analysis of this Philippine total energy consumption chart in 4-5 detailed paragraphs:\n\n"
                f"Historical consumption (GWh): {consumption[:3]} ... {consumption[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Forecast: {forecast_values[0] if forecast_values else 'N/A'} GWh in {forecast_years[0] if forecast_years else 'N/A'} "
                f"to {forecast_values[-1] if forecast_values else 'N/A'} GWh in {forecast_years[-1] if forecast_years else 'N/A'}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} GWh = {growth:.1f}%\n\n"
                "In your analysis, cover:\n"
                "1) The overall growth trajectory and what economic or demographic drivers likely explain it.\n"
                "2) Notable acceleration or deceleration phases and what events may have caused them.\n"
                "3) How Philippine consumption growth compares to ASEAN neighbors.\n"
                "4) What the forecast implies for grid planning, transmission investment, and policy.\n"
                "5) Implications for energy security and the urgency of diversifying the generation mix."
            )
        if chart_type == "peak_demand":
            years = chart_data.get("years", [])
            peak_demand = chart_data.get("peak_demand", [])
            latest = peak_demand[-1] if peak_demand else 0
            first = peak_demand[0] if peak_demand else 0
            growth = ((latest / first) - 1) * 100 if first else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant. Provide a deep, in-depth analysis of this Philippine peak electricity demand chart in 4-5 detailed paragraphs:\n\n"
                f"Peak demand (MW): {peak_demand[:3]} ... {peak_demand[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Overall growth from {first:.0f} to {latest:.0f} MW = {growth:.1f}%\n\n"
                "In your analysis, cover:\n"
                "1) How peak demand growth compares to installed generation capacity and dependable capacity.\n"
                "2) What this means for grid reliability, reserve margins, and the risk of brownouts.\n"
                "3) The role of demand-side management and time-of-use pricing in flattening peaks.\n"
                "4) How renewables plus battery storage can reduce peak stress and displace peaker plants.\n"
                "5) Infrastructure and policy recommendations for NGCP and the DOE."
            )
        if chart_type == "renewable_generation":
            years = chart_data.get("years", [])
            renewable = chart_data.get("renewable_generation", [])
            total = chart_data.get("total_generation", [])
            latest_re = renewable[-1] if renewable else 0
            latest_total = total[-1] if total else 1
            share = (latest_re / latest_total) * 100 if latest_total else 0
            return (
                "You are LUMI, an Environmental Intelligence assistant. Provide a deep, in-depth analysis of this Philippine renewable energy generation chart in 4-5 detailed paragraphs:\n\n"
                f"Renewable generation (GWh): {renewable[:3]} ... {renewable[-3:]} across years {years[0]}–{years[-1]}\n"
                f"Total generation (GWh): {total[:3]} ... {total[-3:]}\n"
                f"Latest renewable share: {share:.1f}%\n\n"
                "In your analysis, cover:\n"
                "1) The absolute and relative pace of renewable growth over the historical period.\n"
                "2) How the share compares to the 35% RE target under the Renewable Energy Act of 2008.\n"
                "3) The composition of renewable sources (geothermal, hydro, solar, wind, biomass) and their relative contributions.\n"
                "4) What policy, investment, and regulatory signals the trend suggests.\n"
                "5) Challenges ahead such as grid integration, intermittency, and financing for large-scale RE projects."
            )
        if chart_type == "sources":
            shares = chart_data.get("shares", {})
            return (
                "You are LUMI, an Environmental Intelligence assistant. Provide a deep, in-depth analysis of the Philippine energy generation mix in 4-5 detailed paragraphs:\n\n"
                + "\n".join([f"  - {k}: {v}%" for k, v in shares.items()])
                + "\n\nIn your analysis, cover:\n"
                "1) The dominance of fossil fuels (coal and natural gas) and what drives their continued reliance.\n"
                "2) The role of each renewable source and its growth trajectory.\n"
                "3) What this mix means for the Philippines' climate commitments under the Paris Agreement.\n"
                "4) Barriers to decarbonization including stranded assets, baseload requirements, and grid constraints.\n"
                "5) A forward-looking roadmap for transitioning the generation mix toward 50% renewables by 2040."
            )
        if chart_type == "map":
            return (
                "You are LUMI, an Environmental Intelligence assistant. Provide a deep, in-depth explanation of what a province-level renewable potential choropleth map means for the Philippines in 4-5 detailed paragraphs.\n\n"
                "Scores are based on solar irradiance (40%), wind speed (30%), and hydropower suitability (30%).\n\n"
                "In your analysis, cover:\n"
                "1) Why some regions score higher and the geographic and climatic factors behind it.\n"
                "2) How this map can guide national renewable energy planning and policy.\n"
                "3) The practical implications for local government units, investors, and communities.\n"
                "4) Limitations of the composite score and what data would improve accuracy.\n"
                "5) Recommendations for integrating these insights into the Philippine Energy Plan."
            )
        return "Provide a brief energy insight based on the available data."


# Singleton
_energyhub_service: EnergyHubService | None = None


def get_energyhub_service() -> EnergyHubService:
    global _energyhub_service
    if _energyhub_service is None:
        _energyhub_service = EnergyHubService()
    return _energyhub_service
