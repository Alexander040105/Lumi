"""Fixture-based assertions for the LLM sanitizer pipeline.

Run with: python -m pytest fastapi-backend/tests/test_llm_sanitizer.py -q
or: python fastapi-backend/tests/test_llm_sanitizer.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the backend package importable when run as a plain script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.llm_sanitizer import (  # noqa: E402
    clean_ai_output,
    extract_prescriptive_recommendation,
    sanitize_llm_output,
)

# Tag constants to avoid any editor/encoding ambiguity.
THINK_OPEN = "<" + "think" + ">"
THINK_CLOSE = "</" + "think" + ">"
REASON_OPEN = "<" + "reasoning" + ">"
REASON_CLOSE = "</" + "reasoning" + ">"


def _run() -> None:
    # 1. Closed thinking block (literal tag)
    raw = THINK_OPEN + "Let me analyze this." + THINK_CLOSE + " Now for the answer. ## Observation High irradiance."
    out = sanitize_llm_output(raw)
    assert "Let me analyze this" not in out, "closed thinking leaked: %r" % out
    assert "## Observation" in out, "heading lost after closed thinking: %r" % out

    # 2. HTML-escaped thinking block
    raw = "&lt;think&gt;escaped thinking&lt;/think&gt; ## Observation High irradiance."
    out = sanitize_llm_output(raw)
    assert "escaped thinking" not in out, "escaped thinking leaked: %r" % out
    assert "## Observation" in out, "heading lost after escaped thinking: %r" % out

    # 3. Unclosed thinking tag — per plan, everything from the unclosed tag
    #    to end of text is discarded (no safe way to know where thinking ends).
    raw = THINK_OPEN + "Unclosed thinking here. ## Observation High irradiance."
    out = sanitize_llm_output(raw)
    assert out == "", "unclosed thinking should consume everything: %r" % out

    # 4. <reasoning> block
    raw = REASON_OPEN + "internal reasoning here" + REASON_CLOSE + " ## Observation High irradiance."
    out = sanitize_llm_output(raw)
    assert "internal reasoning" not in out, "reasoning leaked: %r" % out
    assert "## Observation" in out, "heading lost after reasoning: %r" % out

    # 5. HTML tags + entities are stripped, narrative preserved
    sample = (
        "## Observation Solar irradiance is high at 5.8 kWh/m2/day. "
        "&lt;ol&gt;&lt;li&gt;High yield&lt;/li&gt;&lt;/ol&gt; "
        "## Interpretation This is excellent for solar PV. "
        "## Recommendation Install a 3 kWp system. "
        "## Reason Best ROI for the area."
    )
    out = sanitize_llm_output(sample)
    assert "<" not in out and ">" not in out, "angle brackets remain: %r" % out
    assert "5.8 kWh/m2/day" in out, "narrative lost after HTML strip: %r" % out
    for heading in ("## Observation", "## Interpretation", "## Recommendation", "## Reason"):
        assert heading in out, "%s heading lost: %r" % (heading, out)

    # 6. extract_prescriptive_recommendation still finds the 4 sections
    pres = extract_prescriptive_recommendation(out)
    assert all(pres.values()), "sections missing: %s" % {k: bool(v) for k, v in pres.items()}

    # 7. clean_ai_output also strips thinking + HTML and truncates cleanly
    raw = THINK_OPEN + "Let me think." + THINK_CLOSE + " ## Recommendation Install a 3 kWp system."
    cleaned = clean_ai_output(raw)
    assert "Let me think" not in cleaned, "clean_ai_output leaked thinking: %r" % cleaned
    assert cleaned.endswith("."), "clean_ai_output did not truncate to a sentence: %r" % cleaned

    print("OK: all sanitizer assertions passed")


if __name__ == "__main__":
    _run()
