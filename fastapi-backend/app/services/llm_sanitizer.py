"""LLM output sanitization utilities.

Removes raw JSON wrappers, markdown fences, escaped characters,
and normalises whitespace so downstream UI receives clean plain text.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def strip_json_wrappers(text: str) -> str:
    """If the whole text is a JSON object, extract the most narrative value."""
    if not text:
        return ""
    text = text.strip()
    if text.startswith(("{", "[")) and text.endswith(("}", "]")):
        try:
            parsed = json.loads(text)
            extracted = _extract_text(parsed)
            if extracted and len(extracted) > 20:
                return extracted
        except json.JSONDecodeError:
            pass
    return text


def strip_key_value_formatting(text: str) -> str:
    """Remove lines that look like JSON keys or bullet-point key-value pairs."""
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just JSON keys like "summary": "..."
        if re.match(r'^"?\w+"?\s*:\s*"', stripped):
            # Extract the value part after the colon+quote
            match = re.search(r':\s*"(.*)"\s*,?\s*$', stripped)
            if match:
                cleaned.append(match.group(1))
            continue
        # Skip lines that are just structural JSON symbols
        if stripped in ("{", "}", "[", "]", "}", "{"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple blank lines, strip leading/trailing whitespace."""
    if not text:
        return ""
    text = text.replace("\\n", "\n").replace("\\t", "\t")
    # Remove outer quotes if the whole thing is a quoted string
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            text = text[1:-1]
    # Collapse multiple blank lines to one
    lines = text.splitlines()
    result = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return "\n".join(result).strip()


def _extract_text(obj: Any) -> str:
    """Recursively extract narrative text from parsed JSON."""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, list):
        parts = [_extract_text(item) for item in obj if item is not None]
        return "\n\n".join(p for p in parts if p)
    if isinstance(obj, dict):
        for key in (
            "observation", "interpretation", "recommendation", "reason",
            "analysis", "insight", "explanation", "response", "text",
            "content", "result", "answer", "narrative", "summary",
        ):
            if key in obj:
                return _extract_text(obj[key])
        # Fallback: concatenate all values
        parts = []
        for v in obj.values():
            extracted = _extract_text(v)
            if extracted:
                parts.append(extracted)
        return "\n\n".join(parts)
    return str(obj) if obj is not None else ""


def sanitize_llm_output(text: str) -> str:
    """Full sanitization pipeline: fences → JSON wrappers → key-value → whitespace."""
    if not text:
        return ""
    text = strip_markdown_fences(text)
    text = strip_json_wrappers(text)
    text = strip_key_value_formatting(text)
    text = normalize_whitespace(text)
    return text


def extract_prescriptive_recommendation(text: str) -> dict[str, str]:
    """Extract the 4-part prescriptive structure from LLM text.

    Returns:
        dict with keys: observation, interpretation, recommendation, reason
    """
    result = {
        "observation": "",
        "interpretation": "",
        "recommendation": "",
        "reason": "",
    }
    if not text:
        return result

    text = sanitize_llm_output(text)

    # Try to find sections by heading patterns (supports markdown ## headers)
    patterns = {
        "observation": r"(?:##?\s*)?(?:Observation|OBSERVATION|What the data shows)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Interpretation|INTERPRETATION|What this means)|$)",
        "interpretation": r"(?:##?\s*)?(?:Interpretation|INTERPRETATION|What this means)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Recommendation|RECOMMENDATION|What to consider)|$)",
        "recommendation": r"(?:##?\s*)?(?:Recommendation|RECOMMENDATION|What to consider|Suggested action)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Reason|REASON|Why|Rationale)|$)",
        "reason": r"(?:##?\s*)?(?:Reason|REASON|Why|Rationale)[\s:]*\n?(.*?)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            result[key] = match.group(1).strip()

    # Fallback: if no sections found, put everything in recommendation
    if not any(result.values()):
        result["recommendation"] = text

    return result
