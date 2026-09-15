"""Live evaluation of the LUMI AI layer (Groq-backed LLM path).

Exercises the *real* application code path end-to-end:
  build_ecosim_dashboard_response (real municipality data)
    -> _build_renewable_analysis_prompt
    -> llm_client.generate_response  (LLM_PROVIDER=groq by default)
    -> llm_sanitizer.sanitize_llm_output / extract_prescriptive_recommendation

Measured:
  - response latency per call (n = 8 real Groq calls, free tier)
  - non-empty / sanitization-survival rate
  - structural compliance (## Observation / ## Interpretation / ## Recommendation
    headers required by the prompt)
  - JSON-mode validity rate on a JSON-demanding prompt (n = 5)
  - provider-fallback path: forced Gemini failure -> Groq emergency fallback
  - timeout path: timeout=0.5 -> graceful empty-string return
  - token usage captured from one raw Groq API call (the app wrapper returns
    text only, so usage is measured at the client level)

Writes artifacts/rerun-2026-09-15/llm/llm_eval.json (+ raw snippets).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[4]
BACKEND = REPO / "fastapi-backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)  # settings/paths resolve relative to backend dir

OUT = REPO / "docs" / "09-Technical-Evaluation" / "artifacts" / "rerun-2026-09-15" / "llm"
OUT.mkdir(parents=True, exist_ok=True)

N_CALLS = 6
JSON_CALLS = 4
REQUIRED_HEADERS = ["## Observation", "## Interpretation", "## Recommendation"]


def build_real_payload() -> dict:
    from app.services.ecosim import build_ecosim_dashboard_response
    base = build_ecosim_dashboard_response(
        municipality_id=5441,
        monthly_consumption=350.0,
        monthly_bill=4200.0,
        include_ai=False,
    )
    return {
        "municipality_data": base.get("municipality_data") or [],
        "consumption_results": base.get("consumption_results"),
        "renewable_energy_results": base.get("renewable_energy_results"),
        "nearby_geothermal_plants": base.get("nearby_geothermal_plants") or [],
        "mode": "municipality",
    }


def main() -> None:
    import app.services.llm_client as llm
    from app.services.gemini_funcs import _build_renewable_analysis_prompt
    from app.services.llm_sanitizer import (
        extract_prescriptive_recommendation,
        sanitize_llm_output,
    )

    result: dict = {"provider_env": os.getenv("LLM_PROVIDER", "groq"),
                    "groq_model_default": os.getenv("GROQ_MODEL", "groq/compound-mini")}

    print("[1/6] Building real EcoSim payload (municipality_id=5441) ...")
    payload = build_real_payload()
    result["payload_keys"] = list(payload.keys())
    prompt = _build_renewable_analysis_prompt(payload)
    result["prompt_chars"] = len(prompt)
    print(f"      prompt built: {len(prompt)} chars")

    # ---- 1. Real Groq calls through the production prompt ----
    print(f"[2/6] Running {N_CALLS} real Groq calls through production prompt ...")
    runs = []
    for i in range(N_CALLS):
        t0 = time.perf_counter()
        error = None
        try:
            raw = llm.generate_response(prompt, max_output_tokens=4000, max_retries=2, timeout=60)
        except Exception as exc:
            raw, error = "", f"{type(exc).__name__}: {exc}"
        elapsed = (time.perf_counter() - t0) * 1000
        cleaned = sanitize_llm_output(raw)
        prescriptive = extract_prescriptive_recommendation(cleaned)
        headers_found = [h for h in REQUIRED_HEADERS if h in cleaned]
        runs.append({
            "run": i + 1,
            "latency_ms": round(elapsed, 1),
            "chars": len(raw or ""),
            "non_empty": bool(raw),
            "survives_sanitizer": bool(cleaned),
            "headers_found": headers_found,
            "headers_ok": len(headers_found) == len(REQUIRED_HEADERS),
            "prescriptive_extracted": bool(prescriptive),
            "error": error,
        })
        print(f"      run {i+1}: {elapsed:.0f} ms, {len(raw or '')} chars, "
              f"headers={len(headers_found)}/{len(REQUIRED_HEADERS)}"
              + (f" ERROR={error[:90]}" if error else ""))
        time.sleep(20)  # free-tier TPM is tight; keep well under the per-minute cap
    result["runs"] = runs
    lat = sorted(r["latency_ms"] for r in runs)
    result["latency"] = {
        "n": len(runs), "min_ms": lat[0], "mean_ms": round(sum(lat) / len(lat), 1),
        "p50_ms": lat[len(lat) // 2], "p95_ms": lat[max(0, int(len(lat) * 0.95) - 1)],
        "max_ms": lat[-1],
    }
    result["non_empty_rate"] = sum(r["non_empty"] for r in runs) / len(runs)
    result["sanitizer_survival_rate"] = sum(r["survives_sanitizer"] for r in runs) / len(runs)
    result["header_compliance_rate"] = sum(r["headers_ok"] for r in runs) / len(runs)
    result["prescriptive_extraction_rate"] = sum(r["prescriptive_extracted"] for r in runs) / len(runs)

    # ---- 2. JSON-mode validity ----
    print(f"[3/6] Running {JSON_CALLS} JSON-mode probes ...")
    json_prompt = (
        'Return ONLY a JSON object with keys "recommended_energy_source" (string), '
        '"cost_range" (string), "explanation" (string), "caveats" (string). '
        "No markdown, no prose. Base it on this summary: high solar irradiance, "
        "moderate wind, no hydro site, monthly bill 4200 PHP."
    )
    json_runs = []
    for i in range(JSON_CALLS):
        t0 = time.perf_counter()
        error = None
        try:
            raw = llm.generate_response(json_prompt, max_output_tokens=800, max_retries=2, timeout=60)
        except Exception as exc:
            raw, error = "", f"{type(exc).__name__}: {exc}"
        elapsed = (time.perf_counter() - t0) * 1000
        parsed = llm.parse_json_response(raw or "")
        required = {"recommended_energy_source", "cost_range", "explanation", "caveats"}
        json_runs.append({
            "run": i + 1, "latency_ms": round(elapsed, 1),
            "valid_json": bool(parsed), "schema_ok": required <= set(parsed.keys()),
            "error": error,
        })
        print(f"      json run {i+1}: {elapsed:.0f} ms, valid={bool(parsed)}"
              + (f" ERROR={error[:90]}" if error else ""))
        time.sleep(20)
    result["json_mode"] = {
        "n": len(json_runs),
        "valid_json_rate": sum(r["valid_json"] for r in json_runs) / len(json_runs),
        "schema_compliance_rate": sum(r["schema_ok"] for r in json_runs) / len(json_runs),
        "mean_latency_ms": round(sum(r["latency_ms"] for r in json_runs) / len(json_runs), 1),
    }

    # ---- 3. Forced Gemini failure -> Groq emergency fallback ----
    print("[4/6] Testing Gemini->Groq emergency fallback (forced failure) ...")
    t0 = time.perf_counter()
    fallback_ok, fallback_err = False, None
    with patch("app.services.gemini_funcs.generate_gemini_response",
               side_effect=RuntimeError("Injected Gemini outage (test)")):
        try:
            llm.LLM_PROVIDER = "gemini"  # force provider branch
            fb = llm.generate_response(json_prompt, max_output_tokens=800,
                                       max_retries=1, timeout=60)
            fallback_ok = bool(fb)
        except Exception as exc:
            fallback_err = str(exc)
        finally:
            llm.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()
    result["fallback"] = {
        "gemini_failure_injected": True,
        "groq_fallback_returned_response": fallback_ok,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        "error": fallback_err,
    }
    print(f"      fallback returned response: {fallback_ok} "
          f"({result['fallback']['elapsed_ms']} ms)")

    # ---- 4. Timeout path ----
    print("[5/6] Testing hard-timeout path (timeout=0.5s) ...")
    t0 = time.perf_counter()
    timed = llm.generate_response(prompt, max_output_tokens=4000,
                                  max_retries=1, timeout=0.5)
    result["timeout_path"] = {
        "timeout_s": 0.5,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        "returned_empty_string": timed == "",
    }
    print(f"      elapsed {result['timeout_path']['elapsed_ms']} ms, "
          f"empty={result['timeout_path']['returned_empty_string']}")

    # ---- 5. Token usage (raw client-level, one call) ----
    print("[6/6] Capturing token usage via raw Groq client call ...")
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "groq/compound-mini"),
            messages=[{"role": "user", "content": json_prompt}],
            max_tokens=800, temperature=0.3,
        )
        u = resp.usage
        result["token_usage_sample"] = {
            "model_returned": resp.model,
            "prompt_tokens": getattr(u, "prompt_tokens", None),
            "completion_tokens": getattr(u, "completion_tokens", None),
            "total_tokens": getattr(u, "total_tokens", None),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
        print(f"      tokens: {result['token_usage_sample']}")
    except Exception as exc:
        result["token_usage_sample"] = {"error": str(exc)}

    # ---- save snippets of one representative response ----
    try:
        rep = llm.generate_response(prompt, max_output_tokens=4000,
                                    max_retries=1, timeout=60)[:1200]
    except Exception as exc:
        rep = f"<call failed: {exc}>"
    snippet = {
        "prompt_first_800": prompt[:800],
        "raw_response_first_1200": rep,
    }
    (OUT / "llm_eval.json").write_text(json.dumps(result, indent=2, default=str))
    (OUT / "prompt_and_response_snippets.json").write_text(json.dumps(snippet, indent=2))
    print("\n" + json.dumps({k: v for k, v in result.items() if k != "runs"}, indent=2, default=str))
    print("\nWrote", OUT / "llm_eval.json")


if __name__ == "__main__":
    main()
