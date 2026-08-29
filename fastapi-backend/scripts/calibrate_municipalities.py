"""Calibration script: test renewable energy scoring at MUNICIPALITY level.

Calls the EcoSim API for 30+ municipalities across the Philippines in
municipality mode (not province mode), collects scores and recommendations,
and reports on bias distribution.

Usage:
  cd fastapi-backend
  set PYTHONPATH=.
  python scripts/calibrate_municipalities.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

# Municipalities spanning different provinces and terrain types
MUNICIPALITIES = [
    # Benguet (mountainous)
    (5116, "Atok, Benguet"),
    (5117, "Bakun, Benguet"),
    (5118, "Bokod, Benguet"),
    (5126, "Kabayan, Benguet"),
    # Pangasinan (flat coastal)
    (5001, "Alaminos, Pangasinan"),
    (5002, "Anda, Pangasinan"),
    (5010, "Bolinao, Pangasinan"),
    # Pampanga (flat lowland)
    (5201, "Angeles, Pampanga"),
    (5202, "Arayat, Pampanga"),
    # Ilocos Sur (coastal + mountainous)
    (5301, "Alilem, Ilocos Sur"),
    (5302, "Banayoyo, Ilocos Sur"),
    # Nueva Vizcaya (valley)
    (6401, "Alfonso Castaneda, Nueva Vizcaya"),
    (6402, "Ambaguio, Nueva Vizcaya"),
    # Zambales (coastal + mountainous)
    (6001, "Botolan, Zambales"),
    (6002, "Cabangan, Zambales"),
    # Batangas (coastal)
    (6901, "Abra de Ilog, Batangas"),
    (6902, "Balayan, Batangas"),
    # Iloilo (mixed)
    (7401, "Ajuy, Iloilo"),
    (7402, "Alimodian, Iloilo"),
    # Cebu (island)
    (7601, "Alcantara, Cebu"),
    (7602, "Alcoy, Cebu"),
    # Bukidnon (plateau)
    (7701, "Baungon, Bukidnon"),
    (7702, "Cabanglasan, Bukidnon"),
    # Misamis Oriental (coastal)
    (7801, "Balingasag, Misamis Oriental"),
    (7802, "Balingoan, Misamis Oriental"),
    # Davao (mixed)
    (7901, "Bansalan, Davao del Sur"),
    # Ifugao (mountainous)
    (5701, "Aguinaldo, Ifugao"),
    (5702, "Alfonso Lista, Ifugao"),
    # La Union (coastal)
    (5401, "Agoo, La Union"),
    (5402, "Aringay, La Union"),
    # Quirino (mountainous)
    (6501, "Aglipay, Quirino"),
    (6502, "Cabarroguis, Quirino"),
]

BASE_URL = os.environ.get("ECOSIM_URL", "http://127.0.0.1:8000")


def call_ecosim(muni_id: int, timeout: int = 90) -> dict | None:
    url = (
        f"{BASE_URL}/api/v1/ecosim/"
        f"?municipality_id={muni_id}&monthly_consumption=350"
        f"&monthly_bill=5000&electricity_rate=14.29"
        f"&desired_savings=0.5&mode=municipality"
    )
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return json.loads(resp.read())
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return None


def main() -> None:
    results = []

    print(f"Calibrating {len(MUNICIPALITIES)} municipalities (municipality mode)...")
    print(f"{'Municipality':<40} {'Solar':>7} {'Wind':>7} {'Hydro':>7} {'Rec':>7} {'SuitRec':>8} {'wOut':>7} {'sOut':>7} {'hOut':>7}")
    print("-" * 120)

    for mid, name in MUNICIPALITIES:
        data = call_ecosim(mid)
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

        # Get enrichment info
        hydro_source = assumptions.get("hydro_data_source", "?")
        catchment = assumptions.get("hydro_catchment_name", "?")
        feas = assumptions.get("hydro_stream_feasibility", "?")

        results.append({
            "name": name,
            "id": mid,
            "solar_score": solar_score,
            "wind_score": wind_score,
            "hydro_score": hydro_score,
            "solar_out": solar_out,
            "wind_out": wind_out,
            "hydro_out": hydro_out,
            "rec": rec,
            "suit_rec": suit_rec,
            "suit_score": suit_score,
            "hydro_source": hydro_source,
            "catchment": catchment,
            "feas": feas,
        })

        print(
            f"{name:<40} {solar_score:>7.1f} {wind_score:>7.1f} {hydro_score:>7.1f} "
            f"{rec:>7} {suit_rec:>8} {wind_out:>7.1f} {solar_out:>7.1f} {hydro_out:>7.1f}"
        )
        time.sleep(0.3)

    if not results:
        print("\nNo results collected. Is the backend running?")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 120)
    print("MUNICIPALITY-LEVEL CALIBRATION SUMMARY")
    print("=" * 120)

    for source in ["solar", "wind", "hydro"]:
        scores = [r[f"{source}_score"] for r in results]
        outputs = [r[f"{source}_out"] for r in results]
        print(f"\n{source.upper()}:")
        print(f"  Score:  min={min(scores):.1f}  median={sorted(scores)[len(scores)//2]:.1f}  max={max(scores):.1f}  mean={sum(scores)/len(scores):.1f}")
        print(f"  Output: min={min(outputs):.1f}  median={sorted(outputs)[len(outputs)//2]:.1f}  max={max(outputs):.1f}  mean={sum(outputs)/len(outputs):.1f}")

    # Recommendation distribution
    print("\nRECOMMENDATION DISTRIBUTION (generation-based):")
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

    # Agreement
    agree = sum(1 for r in results if r["rec"] == r["suit_rec"])
    print(f"\nAgreement (gen vs suitability): {agree}/{len(results)} ({100*agree/len(results):.1f}%)")

    # Hydro enrichment details
    print("\nHYDRO ENRICHMENT DETAILS:")
    enriched = sum(1 for r in results if "Boothroyd" in r["hydro_source"])
    print(f"  Using enrichment: {enriched}/{len(results)} ({100*enriched/len(results):.1f}%)")
    feas_counts = {}
    for r in results:
        f = r["feas"]
        feas_counts[f] = feas_counts.get(f, 0) + 1
    print(f"  Stream feasibility: {feas_counts}")

    # Score-output correlation
    print("\nSCORE-OUTPUT CORRELATION:")
    for source in ["solar", "wind", "hydro"]:
        scores = [r[f"{source}_score"] for r in results]
        outputs = [r[f"{source}_out"] for r in results]
        if len(scores) > 2 and max(outputs) > 0:
            n = len(scores)
            mean_s = sum(scores) / n
            mean_o = sum(outputs) / n
            cov = sum((s - mean_s) * (o - mean_o) for s, o in zip(scores, outputs)) / n
            std_s = (sum((s - mean_s) ** 2 for s in scores) / n) ** 0.5
            std_o = (sum((o - mean_o) ** 2 for o in outputs) / n) ** 0.5
            corr = cov / (std_s * std_o) if std_s > 0 and std_o > 0 else 0
            print(f"  {source:6s}: r={corr:.3f}")

    # Hydro > 0 count
    hydro_nonzero = sum(1 for r in results if r["hydro_out"] > 0)
    print(f"\nHydro > 0: {hydro_nonzero}/{len(results)} ({100*hydro_nonzero/len(results):.1f}%)")
    hydro_gt5 = sum(1 for r in results if r["hydro_out"] > 5)
    print(f"Hydro > 5 kWh: {hydro_gt5}/{len(results)} ({100*hydro_gt5/len(results):.1f}%)")
    hydro_gt10 = sum(1 for r in results if r["hydro_out"] > 10)
    print(f"Hydro > 10 kWh: {hydro_gt10}/{len(results)} ({100*hydro_gt10/len(results):.1f}%)")

    # Bias check
    print("\nBIAS CHECK:")
    max_rec_pct = max(
        sum(1 for r in recs if r == src) / len(recs) * 100
        for src in ["Solar", "Wind", "Hydropower"]
    )
    if max_rec_pct > 80:
        print(f"  WARNING: One source wins {max_rec_pct:.1f}% of recommendations (>80% threshold)")
    else:
        print(f"  OK: No source dominates (>80% threshold). Max = {max_rec_pct:.1f}%")

    # Write report
    report_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "docs", "04-ML-Data-Science", "calibration_municipality_report.md"
    )
    report_path = os.path.abspath(report_path)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        f.write("# Municipality-Level Calibration Report\n\n")
        f.write(f"**Municipalities tested:** {len(results)}\n\n")
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
        f.write("\n## Per-Municipality Results\n\n")
        f.write("| Municipality | Solar Score | Wind Score | Hydro Score | Solar kWh | Wind kWh | Hydro kWh | Recommended | Suit. Rec. | Catchment | Feasibility |\n")
        f.write("|--------------|------------|------------|-------------|-----------|----------|-----------|-------------|------------|-----------|-------------|\n")
        for r in results:
            f.write(
                f"| {r['name']} | {r['solar_score']:.1f} | {r['wind_score']:.1f} | "
                f"{r['hydro_score']:.1f} | {r['solar_out']:.1f} | {r['wind_out']:.1f} | "
                f"{r['hydro_out']:.1f} | {r['rec']} | {r['suit_rec']} | {r['catchment']} | {r['feas']} |\n"
            )
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
