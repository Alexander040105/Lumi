"""Comprehensive calibration: test ALL provinces and ALL municipalities.

Fetches every province and municipality ID from Supabase, calls the EcoSim
API for each, and exports results to CSV + markdown report.

Usage:
  cd fastapi-backend
  set PYTHONPATH=.
  python scripts/calibrate_all.py
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time
import urllib.request
from collections import Counter

from app.services.supabase_service import get_supabase_client

BASE_URL = os.environ.get("ECOSIM_URL", "http://127.0.0.1:8000")
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "04-ML-Data-Science"
)
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)


def fetch_all_provinces() -> list[dict]:
    """Fetch all provinces from Supabase."""
    client = get_supabase_client()
    resp = client.table("provinces").select("province_id,name").order("province_id").limit(500).execute()
    return resp.data or []


def fetch_all_municipalities() -> list[dict]:
    """Fetch all municipalities from Supabase in batches."""
    client = get_supabase_client()
    all_munis = []
    offset = 0
    batch_size = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,province_id")
            .order("municipality_id")
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        data = resp.data or []
        if not data:
            break
        all_munis.extend(data)
        offset += batch_size
        if len(data) < batch_size:
            break
    return all_munis


def call_ecosim(geo_id: int, mode: str, timeout: int = 120) -> dict | None:
    url = (
        f"{BASE_URL}/api/v1/ecosim/"
        f"?municipality_id={geo_id}&monthly_consumption=350"
        f"&monthly_bill=5000&electricity_rate=14.29"
        f"&desired_savings=0.5&mode={mode}"
    )
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return json.loads(resp.read())
    except Exception as exc:
        return None


def extract_result(data: dict, geo_id: int, name: str, mode: str) -> dict:
    rr = data.get("renewable_energy_results", {})
    solar = rr.get("solar_output", {}) or {}
    wind = rr.get("wind_output", {}) or {}
    hydro = rr.get("hydro_output", {}) or {}
    assumptions = rr.get("assumptions", {}) or {}

    return {
        "geo_id": geo_id,
        "name": name,
        "mode": mode,
        "solar_score": solar.get("solar_score", 0),
        "wind_score": wind.get("wind_score", 0),
        "hydro_score": hydro.get("hydro_score", 0),
        "solar_kwh": solar.get("monthly_solar_output", 0),
        "wind_kwh": wind.get("monthly_energy_kwh", 0),
        "hydro_kwh": hydro.get("monthly_hydro_output", 0),
        "recommended_source": data.get("recommended_source", "?"),
        "suitability_recommended_source": data.get("suitability_recommended_source", "?"),
        "suitability_recommended_score": data.get("suitability_recommended_score", 0),
        "hydro_data_source": assumptions.get("hydro_data_source", "?"),
        "hydro_catchment_name": assumptions.get("hydro_catchment_name", "?"),
        "hydro_stream_feasibility": assumptions.get("hydro_stream_feasibility", "?"),
    }


def run_batch(items: list[dict], mode: str, label: str) -> list[dict]:
    """Run EcoSim for a list of items (provinces or municipalities)."""
    results = []
    errors = 0
    total = len(items)
    id_key = "province_id" if mode == "province" else "municipality_id"

    for i, item in enumerate(items):
        geo_id = item[id_key]
        name = item.get("name", "?")

        data = call_ecosim(geo_id, mode)
        if data is None:
            errors += 1
            if errors <= 5 or errors % 50 == 0:
                print(f"  [{label}] ERROR #{errors}: {name} (id={geo_id})")
        else:
            results.append(extract_result(data, geo_id, name, mode))

        if (i + 1) % 50 == 0 or i + 1 == total:
            print(f"  [{label}] Progress: {i+1}/{total} ({100*(i+1)/total:.0f}%) — {len(results)} ok, {errors} errors")

        time.sleep(0.2)

    print(f"  [{label}] DONE: {len(results)} results, {errors} errors")
    return results


def write_csv(results: list[dict], path: str) -> None:
    """Write results to CSV."""
    if not results:
        return
    fields = list(results[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"  CSV written: {path} ({len(results)} rows)")


def fmt_stats(vals: list[float]) -> str:
    if not vals:
        return "n/a"
    return (
        f"min={min(vals):.1f}  median={statistics.median(vals):.1f}  "
        f"max={max(vals):.1f}  mean={statistics.mean(vals):.1f}  "
        f"std={statistics.stdev(vals):.1f}" if len(vals) > 1 else
        f"min={min(vals):.1f}  median={statistics.median(vals):.1f}  "
        f"max={max(vals):.1f}  mean={statistics.mean(vals):.1f}"
    )


def correlation(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 3:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    sx = (sum((x - mx) ** 2 for x in xs) / n) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys) / n) ** 0.5
    return cov / (sx * sy) if sx > 0 and sy > 0 else 0.0


def write_report(prov_results: list[dict], muni_results: list[dict], csv_path: str, report_path: str) -> None:
    """Write comprehensive markdown report."""
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Comprehensive Calibration Report — All Provinces & Municipalities\n\n")
        f.write(f"**Provinces tested:** {len(prov_results)}\n")
        f.write(f"**Municipalities tested:** {len(muni_results)}\n\n")
        f.write(f"**Raw data:** [`calibration_all_results.csv`]({os.path.basename(csv_path)})\n\n")

        for label, results in [("PROVINCE LEVEL", prov_results), ("MUNICIPALITY LEVEL", muni_results)]:
            f.write(f"---\n\n## {label}\n\n")

            # Score distribution
            f.write("### Score Distribution\n\n")
            f.write("| Source | Score Stats |\n|--------|-------------|\n")
            for source in ["solar", "wind", "hydro"]:
                scores = [r[f"{source}_score"] for r in results]
                outputs = [r[f"{source}_kwh"] for r in results]
                f.write(f"| {source.title()} Score | {fmt_stats(scores)} |\n")
                f.write(f"| {source.title()} Output (kWh) | {fmt_stats(outputs)} |\n")

            # Recommendation distribution
            f.write("\n### Recommendation Distribution (generation-based)\n\n")
            f.write("| Source | Count | Percentage |\n|--------|-------|------------|\n")
            recs = [r["recommended_source"] for r in results]
            for src in ["Solar", "Wind", "Hydropower", "None"]:
                count = sum(1 for r in recs if r == src)
                pct = 100 * count / len(recs) if recs else 0
                flag = " **BIASED >80%**" if pct > 80 else ""
                f.write(f"| {src} | {count} | {pct:.1f}%{flag} |\n")

            # Suitability recommendation
            f.write("\n### Suitability Recommendation Distribution (hidden field)\n\n")
            f.write("| Source | Count | Percentage |\n|--------|-------|------------|\n")
            suit_recs = [r["suitability_recommended_source"] for r in results]
            for src in ["Solar", "Wind", "Hydropower", "None"]:
                count = sum(1 for r in suit_recs if r == src)
                pct = 100 * count / len(suit_recs) if suit_recs else 0
                f.write(f"| {src} | {count} | {pct:.1f}% |\n")

            # Agreement
            agree = sum(1 for r in results if r["recommended_source"] == r["suitability_recommended_source"])
            f.write(f"\n**Agreement (gen vs suitability):** {agree}/{len(results)} ({100*agree/len(results):.1f}%)\n")

            # Hydro enrichment
            f.write("\n### Hydro Enrichment\n\n")
            enriched = sum(1 for r in results if "Boothroyd" in r["hydro_data_source"])
            f.write(f"- Using enrichment: {enriched}/{len(results)} ({100*enriched/len(results):.1f}%)\n")
            feas_counts = Counter(r["hydro_stream_feasibility"] for r in results)
            f.write(f"- Stream feasibility: {dict(feas_counts)}\n")

            # Hydro > 0
            hydro_nonzero = sum(1 for r in results if r["hydro_kwh"] > 0)
            hydro_gt5 = sum(1 for r in results if r["hydro_kwh"] > 5)
            hydro_gt10 = sum(1 for r in results if r["hydro_kwh"] > 10)
            f.write(f"- Hydro > 0: {hydro_nonzero}/{len(results)} ({100*hydro_nonzero/len(results):.1f}%)\n")
            f.write(f"- Hydro > 5 kWh: {hydro_gt5}/{len(results)} ({100*hydro_gt5/len(results):.1f}%)\n")
            f.write(f"- Hydro > 10 kWh: {hydro_gt10}/{len(results)} ({100*hydro_gt10/len(results):.1f}%)\n")

            # Correlation
            f.write("\n### Score-Output Correlation\n\n")
            for source in ["solar", "wind", "hydro"]:
                scores = [r[f"{source}_score"] for r in results]
                outputs = [r[f"{source}_kwh"] for r in results]
                r_val = correlation(scores, outputs)
                f.write(f"- {source}: r={r_val:.3f}\n")

            # Bias check
            f.write("\n### Bias Check\n\n")
            max_rec_pct = max(
                sum(1 for r in recs if r == src) / len(recs) * 100
                for src in ["Solar", "Wind", "Hydropower"]
            ) if recs else 0
            if max_rec_pct > 80:
                f.write(f"**WARNING:** One source wins {max_rec_pct:.1f}% of recommendations (>80% threshold)\n")
            else:
                f.write(f"**OK:** No source dominates (>80% threshold). Max = {max_rec_pct:.1f}%\n")

            # Top/bottom 10 for hydro
            f.write("\n### Top 10 Hydro Output\n\n")
            f.write("| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |\n")
            f.write("|------|-----------|-------------|-----------|-------------|\n")
            sorted_hydro = sorted(results, key=lambda r: r["hydro_kwh"], reverse=True)
            for r in sorted_hydro[:10]:
                f.write(f"| {r['name']} | {r['hydro_kwh']:.1f} | {r['hydro_score']:.1f} | {r['hydro_catchment_name']} | {r['hydro_stream_feasibility']} |\n")

            f.write("\n### Bottom 10 Hydro Output\n\n")
            f.write("| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |\n")
            f.write("|------|-----------|-------------|-----------|-------------|\n")
            for r in sorted_hydro[-10:]:
                f.write(f"| {r['name']} | {r['hydro_kwh']:.1f} | {r['hydro_score']:.1f} | {r['hydro_catchment_name']} | {r['hydro_stream_feasibility']} |\n")

    print(f"  Report written: {report_path}")


def main() -> None:
    print("=" * 80)
    print("COMPREHENSIVE CALIBRATION — ALL PROVINCES + ALL MUNICIPALITIES")
    print("=" * 80)

    # Fetch all IDs
    print("\nFetching province and municipality IDs from Supabase...")
    provinces = fetch_all_provinces()
    municipalities = fetch_all_municipalities()
    print(f"  Provinces: {len(provinces)}")
    print(f"  Municipalities: {len(municipalities)}")

    # Run provinces
    print(f"\n--- Testing {len(provinces)} provinces (province mode) ---")
    prov_results = run_batch(provinces, "province", "PROV")

    # Run municipalities
    print(f"\n--- Testing {len(municipalities)} municipalities (municipality mode) ---")
    muni_results = run_batch(municipalities, "municipality", "MUNI")

    # Combine for CSV
    all_results = prov_results + muni_results
    csv_path = os.path.join(OUTPUT_DIR, "calibration_all_results.csv")
    report_path = os.path.join(OUTPUT_DIR, "calibration_all_report.md")

    print("\n--- Writing outputs ---")
    write_csv(all_results, csv_path)
    write_report(prov_results, muni_results, csv_path, report_path)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Provinces tested:     {len(prov_results)}")
    print(f"Municipalities tested: {len(muni_results)}")
    print(f"Total results:        {len(all_results)}")

    for label, results in [("PROVINCE", prov_results), ("MUNICIPALITY", muni_results)]:
        print(f"\n{label}:")
        for source in ["solar", "wind", "hydro"]:
            scores = [r[f"{source}_score"] for r in results]
            outputs = [r[f"{source}_kwh"] for r in results]
            print(f"  {source:6s}: score {fmt_stats(scores)}")
            print(f"          output {fmt_stats(outputs)}")

        recs = [r["recommended_source"] for r in results]
        print(f"  Recommendations:")
        for src in ["Solar", "Wind", "Hydropower"]:
            count = sum(1 for r in recs if r == src)
            pct = 100 * count / len(recs) if recs else 0
            print(f"    {src:12s}: {count:4d} ({pct:5.1f}%)")

        hydro_nonzero = sum(1 for r in results if r["hydro_kwh"] > 0)
        print(f"  Hydro > 0: {hydro_nonzero}/{len(results)} ({100*hydro_nonzero/len(results):.1f}%)")

    print(f"\nCSV:   {csv_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
