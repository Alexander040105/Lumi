#!/usr/bin/env python3
"""Run all LUMI tests and save results to test_results/ folder."""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

TEST_RESULTS_DIR = Path(__file__).parent / "test_results"
TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_tests():
    summary_lines = [
        "=" * 80,
        "  LUMI Testing & Evaluation Suite — Test Results Summary",
        "=" * 80,
        f"  Generated: {TIMESTAMP}",
        f"  Python: {sys.version}",
        "",
    ]

    # --- Unit Tests ---
    summary_lines.append("-" * 80)
    summary_lines.append("UNIT TESTS (tests/unit/)")
    summary_lines.append("-" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    unit_stdout = result.stdout or ""
    unit_stderr = result.stderr or ""

    summary_lines.append(unit_stdout)
    if unit_stderr.strip():
        summary_lines.append("\n[STDERR]")
        summary_lines.append(unit_stderr)

    # --- Integration Tests (API) ---
    summary_lines.append("\n" + "-" * 80)
    summary_lines.append("INTEGRATION TESTS — API (tests/integration/test_api.py)")
    summary_lines.append("-" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/test_api.py", "-v", "--tb=short", "-m", "mock"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    api_stdout = result.stdout or ""
    api_stderr = result.stderr or ""

    summary_lines.append(api_stdout)
    if api_stderr.strip():
        summary_lines.append("\n[STDERR]")
        summary_lines.append(api_stderr)

    # --- Integration Tests (Database) ---
    summary_lines.append("\n" + "-" * 80)
    summary_lines.append("INTEGRATION TESTS — DATABASE (tests/integration/test_database.py)")
    summary_lines.append("Note: Skipped if TEST_DATABASE_URL not set or psycopg2 not installed")
    summary_lines.append("-" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/test_database.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    db_stdout = result.stdout or ""
    db_stderr = result.stderr or ""

    summary_lines.append(db_stdout)
    if db_stderr.strip():
        summary_lines.append("\n[STDERR]")
        summary_lines.append(db_stderr)

    # --- Integration Tests (Pipeline) ---
    summary_lines.append("\n" + "-" * 80)
    summary_lines.append("INTEGRATION TESTS — PIPELINE (tests/integration/test_pipeline.py)")
    summary_lines.append("-" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/test_pipeline.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    pipe_stdout = result.stdout or ""
    pipe_stderr = result.stderr or ""

    summary_lines.append(pipe_stdout)
    if pipe_stderr.strip():
        summary_lines.append("\n[STDERR]")
        summary_lines.append(pipe_stderr)

    # --- Performance Tests ---
    summary_lines.append("\n" + "-" * 80)
    summary_lines.append("PERFORMANCE TESTS (tests/integration/performance_test.py)")
    summary_lines.append("-" * 80)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/performance_test.py", "-v", "--tb=short", "-m", "local"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    perf_stdout = result.stdout or ""
    perf_stderr = result.stderr or ""

    summary_lines.append(perf_stdout)
    if perf_stderr.strip():
        summary_lines.append("\n[STDERR]")
        summary_lines.append(perf_stderr)

    # --- Final summary ---
    summary_lines.append("\n" + "=" * 80)
    summary_lines.append("  END OF TEST RESULTS")
    summary_lines.append("=" * 80)

    # Write to file
    output_path = TEST_RESULTS_DIR / "lumi_test_results.txt"
    output_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"Test results saved to: {output_path}")

    # Also write individual unit test results
    unit_path = TEST_RESULTS_DIR / "unit_test_results.txt"
    unit_path.write_text(unit_stdout + ("\n" + unit_stderr if unit_stderr.strip() else ""), encoding="utf-8")
    print(f"Unit test results saved to: {unit_path}")


if __name__ == "__main__":
    run_tests()
