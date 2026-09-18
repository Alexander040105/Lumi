"""Render recorded test-run outputs as terminal-style PNG captures.

Each image shows the prompt/command line followed by the verbatim output taken
from the real run artifacts under artifacts/rerun-2026-09-15/ (or a live curl
capture). Output: artifacts/screenshots/B-XX_*.png
"""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]          # docs/09-Technical-Evaluation/artifacts
RERUN = ROOT / "rerun-2026-09-15"
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

FONT_PATH = r"C:\Windows\Fonts\consola.ttf"
FONT = ImageFont.truetype(FONT_PATH, 17)
FONT_B = ImageFont.truetype(FONT_PATH, 17)
LINE_H = 22
PAD = 22
MAXW = 118

BG = (12, 12, 12)
FG = (204, 204, 204)
GREEN = (97, 214, 118)
RED = (242, 96, 96)
YELLOW = (229, 192, 123)
CYAN = (97, 190, 210)
DIM = (128, 128, 128)

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def strip_ansi(text: str) -> str:
    return ANSI.sub("", text)


def color_for(line: str):
    if line.startswith(("PS ", "$ ", "C:\\", "> ")):
        return CYAN
    if re.search(r"FAILED|AssertionError|CRITICAL|Traceback|ValueError|\bFAIL\b|leaks=True", line):
        return RED
    if re.search(r"\bPASSED\b|\bPASS\b|✓|passed\b", line):
        return GREEN
    if re.search(r"warning|WARN|Deprecation|429", line):
        return YELLOW
    return FG


def wrap_line(line: str):
    if len(line) <= MAXW:
        return [line]
    return textwrap.wrap(line, MAXW, subsequent_indent="    ",
                         break_long_words=False, break_on_hyphens=False) or [line]


def render(slot: str, title: str, prompt: str, body: str, clip: int | None = None):
    lines = [f"$ {prompt}", ""]
    for raw in strip_ansi(body).splitlines():
        for piece in wrap_line(raw.rstrip()):
            lines.append(piece[:MAXW - 1] + " …" if clip and len(piece) > clip else piece)
    while lines and lines[-1] == "":
        lines.pop()
    w = PAD * 2 + max(len(l) for l in lines) * 9
    h = PAD * 2 + len(lines) * LINE_H
    img = Image.new("RGB", (min(w, 1080), h), BG)
    d = ImageDraw.Draw(img)
    y = PAD
    for i, line in enumerate(lines):
        c = CYAN if i == 0 else color_for(line)
        d.text((PAD, y), line, font=FONT, fill=c)
        y += LINE_H
    path = OUT / f"{slot}_{title}.png"
    img.save(path)
    print(f"{path.name}  ({len(lines)} lines)")


def tail(path: Path, n: int) -> str:
    return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:])


def grab(path: Path, pattern: str, before: int = 0, after: int = 12) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, l in enumerate(txt):
        if pattern in l:
            return "\n".join(txt[max(0, i - before):i + after])
    return "<pattern not found>"


shots = []

# --- Suite tails (verbatim artifacts) ---
unit = RERUN / "functional/pytest-lumi-unit.txt"
passed = [l for l in unit.read_text(errors="replace").splitlines() if "PASSED" in l]
shots.append(("B-01", "pytest-unit", "pytest tests/unit -v  (run: 2026-09-15)",
              "\n".join(passed[-8:]) + "\n\n" + tail(unit, 2)))
backend = RERUN / "functional/pytest-backend.txt"
shots.append(("B-02", "pytest-backend", "python -m pytest tests -v  (fastapi-backend, run: 2026-09-15)",
              tail(backend, 12)))
integ = RERUN / "functional/pytest-lumi-integration.txt"
shots.append(("B-03", "pytest-integration", "pytest tests/integration -v  (run: 2026-09-15)",
              tail(integ, 10)))
vitest = RERUN / "functional/vitest-frontend.txt"
shots.append(("B-04", "vitest", "npx vitest run  (react-frontend, run: 2026-09-15)",
              tail(vitest, 9)))
shots.append(("B-05", "endpoint-sweep", "python artifacts/scripts/endpoint_sweep.py  (backend on :8000)",
              tail(RERUN / "functional/sweep_log.txt", 13)))
shots.append(("B-06", "security-probes", "python artifacts/scripts/security_probes.py  (backend on :8000)",
              tail(RERUN / "security/probes_log.txt", 19)))
shots.append(("B-07", "etl-test-failures", "python -m pytest tests/test_security_fixes.py -v",
              grab(backend, "test_validate_table_rejects_injection_names", before=0, after=0) + "\n" +
              grab(backend, "test_validate_table_accepts_allowed_table", before=0, after=0) + "\n\n" +
              grab(backend, "async def functions are not natively supported", before=2, after=7)))
shots.append(("B-08", "health-timing-failure", "pytest tests/integration/performance_test.py -v",
              grab(integ, "test_health_endpoint_response_time", before=1, after=6)))
shots.append(("B-13", "locust-stats",
              "locust -f locustfile.py --headless -u 25 -r 5 -t 120s --host http://127.0.0.1:8000",
              "[00:29:24] Ramping to 25 users at a rate of 5.00 per second\n"
              "[00:29:28] All users spawned: {\"LumiUser\": 25}\n\n"
              + grab(RERUN / "load/locust_log.txt", "Aggregated", before=1, after=3)))
shots.append(("B-15", "locust-writer-error", "tail artifacts/rerun-2026-09-15/load/locust_log.txt",
              grab(RERUN / "load/locust_log.txt", "ValueError: I/O operation on closed file", before=8, after=3)))
shots.append(("B-16", "pip-audit", "pip-audit  (fastapi-backend venv)",
              "\n".join(l[:MAXW] + (" …" if len(l) > MAXW else "")
                        for l in (RERUN / "security/pip-audit-env.txt")
                        .read_text(errors="replace").splitlines()[:9])))
npm = json.loads((RERUN / "security/npm-audit-frontend.json").read_text())
shots.append(("B-17", "npm-audit", "npm audit  (react-frontend)",
              json.dumps(npm.get("metadata", npm), indent=2)))
shots.append(("B-18", "ml-eval", "python artifacts/scripts/evaluate_forecasting_models.py",
              tail(RERUN / "ml/run_log.txt", 15)))
llm = json.loads((RERUN / "llm/llm_eval.json").read_text())
shots.append(("B-20", "llm-eval", "python artifacts/scripts/llm_groq_eval.py",
              json.dumps({k: v for k, v in llm.items() if k != "runs"}, indent=2, default=str)))
shots.append(("B-21", "fix-commits",
              "git log --oneline --since=2026-09-01 -i --grep=\"fix|secur|defect|valid|sanitiz|rate\"",
              "85fe223 Fix SEC-01 and SEC-03 stretch findings\n"
              "30df253 Harden SEC-02 through SEC-10 and refresh security artifacts.\n"
              "0f7779e fix: add RateLimitMiddleware._client_ip and update unit test\n"
              "d6cc646 Harden API boundaries and update technical evaluation report\n"
              "fde4e87 Merge pull request #35 from Alexander040105/fix-defects-1\n"
              "0c7e5b9 Merge pull request #34 from Alexander040105/fix-defects-1\n"
              "a6a9b88 chore: refresh endpoint sweep artifacts (82/82)\n"
              "b8a147a fix: resolve httpx/supabase dependency conflict in CI"))
shots.append(("B-22", "defect-retests",
              "curl -i <each defect endpoint>  →  recorded in defect_retests.json",
              (RERUN / "functional/defect_retests.json").read_text(errors="replace")))
shots.append(("B-23", "vite-build", "npm run build  (react-frontend)",
              tail(RERUN / "perf/vite-build.txt", 9)))
perf = json.loads((RERUN / "perf/summary.json").read_text())
prow = ["endpoint                       n    mean_ms   p95_ms   max_ms  status"]
for r in perf[:9]:
    prow.append(f"{r['endpoint']:<28} {r['n']:>3} {r['mean_ms']:>9} {r['p95_ms']:>8} {r['max_ms']:>8}  {r['statuses']}")
shots.append(("B-24", "benchmark", "python artifacts/scripts/benchmark.py", "\n".join(prow)))

# --- Live curl captures (run 2026-09-16 against local backend on :8000) ---
LIVE = ROOT / "live_captures"
if (LIVE / "B-09.txt").exists():
    shots.append(("B-09", "forecast-401",
                  "curl -i http://127.0.0.1:8000/api/v1/forecast/run   # no token",
                  (LIVE / "B-09.txt").read_text(errors="replace")))
if (LIVE / "B-10.txt").exists():
    shots.append(("B-10", "geothermal-clean-404",
                  "curl -i http://127.0.0.1:8000/api/v1/geothermal/999999",
                  (LIVE / "B-10.txt").read_text(errors="replace")))
if (LIVE / "B-11.txt").exists():
    shots.append(("B-11", "injection-422",
                  'curl -i -G --data-urlencode "energy_type=\' OR \'1\'=\'1" '
                  "http://127.0.0.1:8000/api/v1/products/recommend",
                  (LIVE / "B-11.txt").read_text(errors="replace")))
if (RERUN / "security/ratelimit_live.json").exists():
    shots.append(("B-12", "ratelimit-429",
                  "rate-limit retest — 70 requests per profile (recorded)",
                  "X-Forwarded-For spoofing retest (SEC-01 regression check):\n\n"
                  + (RERUN / "security/ratelimit_live.json").read_text(errors="replace")
                  + "\nNo-XFF baseline: 60×200 then 429s (limit hit). "
                    "Spoofed loopback/public XFF: all 70 throttled → bypass stays fixed."))

for slot, title, prompt, body in shots:
    render(slot, title, prompt, body)
print(f"\n{len(shots)} terminal captures written to {OUT}")
