"""Calibration script: test renewable energy scoring across Philippine provinces.

Calls the EcoSim API for 25+ provinces, collects scores and recommendations,
and reports on bias distribution.

Usage:
  cd fastapi-backend
  set PYTHONPATH=.
  python scripts/calibrate_renewables.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

# Provinces spanning all regions of the Philippines
PROVINCES = [
    # Region I (Ilocos)
    (255, "Pangasinan"),
    (251, "Ilocos Norte"),
    (252, "Ilocos Sur"),
    (253, "La Union"),
    # Region II (Cagayan Valley)
    (257, "Ifugao"),
    (264, "Nueva Vizcaya"),
    (265, "Quirino"),
    (266, "Aurora"),
    # Region III (Central Luzon)
    (259, "Benguet"),
    (256, "Nueva Ecija"),
    (258, "Tarlac"),
    (260, "Zambales"),
    (261, "Bataan"),
    (262, "Pampanga"),
    (263, "Bulacan"),
    # Region IV-A (CALABARZON)
    (267, "Cavite"),
    (268, "Laguna"),
    (269, "Batangas"),
    (270, "Rizal"),
    (271, "Quezon"),
    # Region V (Bicol)
    (272, "Albay"),
    (273, "Camarines Sur"),
    # Region VI (Western Visayas)
    (274, "Iloilo"),
    (275, "Negros Occidental"),
    # Region VII (Central Visayas)
    (276, "Cebu"),
    # Region X (Northern Mindanao)
    (277, "Bukidnon"),
    (278, "Misamis Oriental"),
    # Region XI (Davao)
    (279, "Davao del Sur"),
    (280, "Compostela Valley"),
]

BASE_URL = os.environ.get("ECOSIM_URL", "http://127.0.0.1:8000")


def call_ecosim(province_id: int, timeout: int = 90) -> dict | None:
    url = (
        f"{BASE_URL}/api/v1/ecosim/"
        f"?municipality_id={province_id}&monthly_consumption=350"
        f"&monthly_bill=5000&electricity_rate=14.29"
        f"&desired_savings=0.5&mode=province"
    )
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return json.loads(resp.read())
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return None


def main() -> None:
    results = []

    print(f"Calibrating {len(PROVINCES)} provinces...")
    print(f"{'Province':<22} {'Solar':>7} {'Wind':>7} {'Hydro':>7} {'Rec':>7} {'SuitRec':>8} {'sScore':>7} {'wOut':>7} {'sOut':>7} {'hOut':>7}")
    print("-" * 100)

    for pid, name in PROVINCES:
        data = call_ecosim(pid)
        if not data:
            continue

        rr = data.get("renewable_energy_results", {})
        solar = rr.get("solar_output", {}) or {}
        wind = rr.get("wind_output", {}) or {}
        hydro = rr.get("hydro_output", {}) or {}
        assumptions = rr.get("assumptions", {}) or {}

        solar_score = solar.get("solar_score", 0)
        wind_score = wind.get("wind_score", 0)
        hydro_score = hydro.get("hydro_score", 0)
        solar_out = solar.get("monthly_solar_output", 0)
        wind_out = wind.get("monthly_energy_kwh", 0)
        hydro_out = hydro.get("monthly_hydro_output", 0)

        rec = data.get("recommended_source", "?")
        suit_rec = data.get("suitability_recommended_source", "?")
        suit_score = data.get("suitability_recommended_score", 0)

        results.append({
            "name": name,
            "solar_score": solar_score,
            "wind_score": wind_score,
            "hydro_score": hydro_score,
            "solar_out": solar_out,
            "wind_out": wind_out,
            "hydro_out": hydro_out,
            "rec": rec,
            "suit_rec": suit_rec,
            "suit_score": suit_score,
        })

        print(
            f"{name:<22} {solar_score:>7.1f} {wind_score:>7.1f} {hydro_score:>7.1f} "
            f"{rec:>7} {suit_rec:>8} {suit_score:>7.1f} "
            f"{wind_out:>7.1f} {solar_out:>7.1f} {hydro_out:>7.1f}"
        )
        time.sleep(0.3)

    if not results:
        print("\nNo results collected. Is the backend running?")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 100)
    print("CALIBRATION SUMMARY")
    print("=" * 100)

    for source in ["solar", "wind", "hydro"]:
        scores = [r[f"{source}_score"] for r in results]
        outputs = [r[f"{source}_out"] for r in results]
        print(f"\n{source.upper()}:")
        print(f"  Score:  min={min(scores):.1f}  median={sorted(scores)[len(scores)//2]:.1f}  max={max(scores):.1f}  mean={sum(scores)/len(scores):.1f}")
        print(f"  Output: min={min(outputs):.1f}  median={sorted(outputs)[len(outputs)//2]:.1f}  max={max(outputs):.1f}  mean={sum(outputs)/len(outputs):.1f}")

    # Recommendation distribution
    print("\nRECOMMENDATION DISTRIBUTION:")
    recs = [r["rec"] for r in results]
    for src in ["Solar", "Wind", "Hydropower", "None"]:
        count = sum(1 for r in recs if r == src)
        pct = 100 * count / len(recs) if recs else 0
        flag = " *** BIASED >80%" if pct > 80 else ""
        print(f"  {src:12s}: {count:3d} ({pct:5.1f}%){flag}")

    # Suitability recommendation distribution
    print("\nSUITABILITY RECOMMENDATION DISTRIBUTION (hidden field):")
    suit_recs = [r["suit_rec"] for r in results]
    for src in ["Solar", "Wind", "Hydropower", "None"]:
        count = sum(1 for r in suit_recs if r == src)
        pct = 100 * count / len(suit_recs) if suit_recs else 0
        print(f"  {src:12s}: {count:3d} ({pct:5.1f}%)")

    # Agreement between generation-based and suitability-based
    agree = sum(1 for r in results if r["rec"] == r["suit_rec"])
    print(f"\nAgreement (gen vs suitability): {agree}/{len(results)} ({100*agree/len(results):.1f}%)")

    # Score-output correlation
    print("\nSCORE-OUTPUT CORRELATION:")
    for source in ["solar", "wind", "hydro"]:
        scores = [r[f"{source}_score"] for r in results]
        outputs = [r[f"{source}_out"] for r in results]
        if len(scores) > 2 and max(outputs) > 0:
            # Simple correlation
            n = len(scores)
            mean_s = sum(scores) / n
            mean_o = sum(outputs) / n
            cov = sum((s - mean_s) * (o - mean_o) for s, o in zip(scores, outputs)) / n
            std_s = (sum((s - mean_s) ** 2 for s in scores) / n) ** 0.5
            std_o = (sum((o - mean_o) ** 2 for o in outputs) / n) ** 0.5
            corr = cov / (std_s * std_o) if std_s > 0 and std_o > 0 else 0
            print(f"  {source:6s}: r={corr:.3f}")

    # Bias check
    print("\nBIAS CHECK:")
    max_rec_pct = max(
        sum(1 for r in recs if r == src) / len(recs) * 100
        for src in ["Solar", "Wind", "Hydropower"]
    )
    if max_rec_pct > 80:
        print(f"  WARNING: One source wins {max_rec_pct:.1f}% of recommendations (>80% threshold)")
        print(f"  Consider reactivating suitability_recommended_source as primary recommendation")
    else:
        print(f"  OK: No source dominates (>80% threshold). Max = {max_rec_pct:.1f}%")

    # Write report
    report_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "docs", "04-ML-Data-Science", "calibration_report.md"
    )
    report_path = os.path.abspath(report_path)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Renewable Energy Calibration Report\n\n")
        f.write(f"**Provinces tested:** {len(results)}\n\n")
        f.write("## Score Distribution\n\n")
        f.write("| Source | Score Min | Score Median | Score Max | Score Mean | Output Min | Output Median | Output Max |\n")
        f.write("|--------|-----------|-------------|-----------|------------|------------|--------------|------------|\n")
        for source in ["solar", "wind", "hydro"]:
            scores = [r[f"{source}_score"] for r in results]
            outputs = [r[f"{source}_out"] for r in results]
            f.write(
                f"| {source.title()} | {min(scores):.1f} | "
                f"{sorted(scores)[len(scores)//2]:.1f} | {max(scores):.1f} | "
                f"{sum(scores)/len(scores):.1f} | {min(outputs):.1f} | "
                f"{sorted(outputs)[len(outputs)//2]:.1f} | {max(outputs):.1f} |\n"
            )
        f.write("\n## Recommendation Distribution\n\n")
        f.write("| Source | Count | Percentage |\n|--------|-------|------------|\n")
        for src in ["Solar", "Wind", "Hydropower", "None"]:
            count = sum(1 for r in recs if r == src)
            pct = 100 * count / len(recs) if recs else 0
            f.write(f"| {src} | {count} | {pct:.1f}% |\n")
        f.write("\n## Per-Province Results\n\n")
        f.write("| Province | Solar Score | Wind Score | Hydro Score | Recommended | Suit. Rec. |\n")
        f.write("|----------|------------|------------|-------------|-------------|------------|\n")
        for r in results:
            f.write(
                f"| {r['name']} | {r['solar_score']:.1f} | {r['wind_score']:.1f} | "
                f"{r['hydro_score']:.1f} | {r['rec']} | {r['suit_rec']} |\n"
            )
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
