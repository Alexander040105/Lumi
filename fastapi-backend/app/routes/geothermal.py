from fastapi import APIRouter, HTTPException, status

from app.schemas.geothermal import (
    GeothermalAnalysisResponse,
    GeothermalDashboardSummary,
    GeothermalSimulationParams,
)
from app.services.supabase_service import get_supabase_client
from app.services.geothermal.features import (
    compute_geothermal_suitability,
    compute_geothermal_output,
)

router = APIRouter()


@router.get("/{municipality_id}", response_model=GeothermalAnalysisResponse)
async def get_geothermal_analysis(municipality_id: int):
    """Return combined geothermal suitability and output for a municipality."""
    client = get_supabase_client()

    # Fetch municipality coordinates for fallback on-the-fly computation
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id, name, lat, lon")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    if not muni_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        )
    muni = muni_resp.data

    # Try pre-computed tables first
    suit_resp = (
        client.table("geothermal_suitability")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )

    suitability = suit_resp.data
    output = out_resp.data

    # Fallback to on-the-fly if pre-computed rows are missing
    if not suitability or not output:
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is None or lon is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Municipality missing coordinates; cannot compute geothermal.",
            )

        # Get surface temperature from climate averages
        temp_resp = (
            client.table("municipality_climate_monthly")
            .select("t2m")
            .eq("municipality_id", municipality_id)
            .limit(1)
            .execute()
        )
        surface_temp = None
        if temp_resp.data:
            surface_temp = float(temp_resp.data[0].get("t2m", 0))

        suit_data = compute_geothermal_suitability(lat, lon, surface_temp)
        out_data = compute_geothermal_output(
            surface_temp,
            suit_data.get("_gradient_c_km"),
            suit_data.get("aquifer_score"),
            suit_data.get("_perm_log10"),
        )

        if not suitability:
            suitability = {
                "municipality_id": municipality_id,
                "heat_flow_score": suit_data.get("heat_flow_score"),
                "fault_density": suit_data.get("fault_density"),
                "fault_distance_km": suit_data.get("fault_distance_km"),
                "volcano_distance_km": suit_data.get("volcano_distance_km"),
                "aquifer_score": suit_data.get("aquifer_score"),
                "temperature_score": suit_data.get("temperature_score"),
                "geothermal_score": suit_data.get("geothermal_score"),
                "classification": suit_data.get("classification"),
            }
        if not output:
            output = {
                "municipality_id": municipality_id,
                "reservoir_temperature_c": out_data.get("reservoir_temperature_c"),
                "estimated_flow_rate_kg_s": out_data.get("estimated_flow_rate_kg_s"),
                "thermal_power_mw": out_data.get("thermal_power_mw"),
                "electric_power_mw": out_data.get("electric_power_mw"),
                "annual_energy_gwh": out_data.get("annual_energy_gwh"),
                "confidence_score": out_data.get("confidence_score"),
                "source": out_data.get("source"),
                "assumption": out_data.get("assumption"),
            }

    return {
        "suitability": suitability,
        "output": output,
    }


@router.get("/ecosim/geothermal", response_model=GeothermalSimulationParams)
async def get_geothermal_simulation_params(municipality_id: int):
    """Return simulation-ready geothermal parameters for EcoSim."""
    client = get_supabase_client()

    suit_resp = (
        client.table("geothermal_suitability")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("*")
        .eq("municipality_id", municipality_id)
        .single()
        .execute()
    )

    if not suit_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Geothermal suitability not found for this municipality.",
        )

    suit = suit_resp.data
    out = out_resp.data or {}

    return {
        "municipality_id": municipality_id,
        "heat_flow_score": suit.get("heat_flow_score"),
        "fault_distance_km": suit.get("fault_distance_km"),
        "volcano_distance_km": suit.get("volcano_distance_km"),
        "aquifer_score": suit.get("aquifer_score"),
        "reservoir_temperature_c": out.get("reservoir_temperature_c"),
        "estimated_flow_rate_kg_s": out.get("estimated_flow_rate_kg_s"),
        "classification": suit.get("classification"),
    }


@router.get("/ecohub/geothermal-summary", response_model=list[GeothermalDashboardSummary])
async def get_geothermal_dashboard_summary():
    """Return province-level geothermal summary for EcoHub dashboard."""
    client = get_supabase_client()

    # Fetch all geothermal suitability rows with municipality -> province mapping
    suit_resp = (
        client.table("geothermal_suitability")
        .select("municipality_id, geothermal_score, classification")
        .execute()
    )
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id, province_id, name")
        .execute()
    )
    prov_resp = (
        client.table("provinces")
        .select("province_id, name")
        .execute()
    )
    out_resp = (
        client.table("geothermal_output")
        .select("municipality_id, electric_power_mw")
        .execute()
    )

    suit_rows = suit_resp.data or []
    muni_rows = muni_resp.data or []
    prov_rows = prov_resp.data or []
    out_rows = out_resp.data or []

    muni_to_prov = {m["municipality_id"]: m.get("province_id") for m in muni_rows}
    prov_names = {p["province_id"]: p.get("name", "") for p in prov_rows}
    out_by_muni = {o["municipality_id"]: o.get("electric_power_mw", 0) or 0 for o in out_rows}

    from collections import defaultdict

    prov_data = defaultdict(lambda: {
        "scores": [],
        "electric_mw": [],
        "classifications": defaultdict(int),
    })

    for row in suit_rows:
        mid = row.get("municipality_id")
        pid = muni_to_prov.get(mid)
        if pid is None:
            continue
        prov_name = prov_names.get(pid, "")
        if not prov_name:
            continue
        prov_data[prov_name]["scores"].append(float(row.get("geothermal_score") or 0))
        cls = row.get("classification") or "Unknown"
        prov_data[prov_name]["classifications"][cls] += 1

    for row in out_rows:
        mid = row.get("municipality_id")
        pid = muni_to_prov.get(mid)
        if pid is None:
            continue
        prov_name = prov_names.get(pid, "")
        if not prov_name:
            continue
        prov_data[prov_name]["electric_mw"].append(float(row.get("electric_power_mw") or 0))

    result = []
    for prov_name, data in prov_data.items():
        scores = data["scores"]
        e_mw = data["electric_mw"]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0
        total_mw = round(sum(e_mw), 3) if e_mw else 0.0
        result.append({
            "province": prov_name,
            "avg_geothermal_score": avg_score,
            "total_electric_potential_mw": total_mw,
            "classification_counts": dict(data["classifications"]),
        })

    return sorted(result, key=lambda x: x["avg_geothermal_score"], reverse=True)
