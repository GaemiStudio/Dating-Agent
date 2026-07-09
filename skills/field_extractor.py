"""
Field Extractor skill
Scans a free-form user answer for profile fields.
Tries deterministic rules first (age regex, name detection), then sends
the remaining fields to the LLM in a single call.
"""

import re
import json
import ollama

import config
from utils import validate_field

# Matches standalone ages 18–120 without picking up years like "1998"
_AGE_RE = re.compile(r'\b(1[89]|[2-9]\d|1[01]\d|120)\b')


def _try_extract_age(text: str) -> str | None:
    """Regex-based age extraction — no LLM needed for plain numbers."""
    match = _AGE_RE.search(text)
    return match.group() if match else None


def _parse_json_from_response(content: str) -> dict:
    """Best-effort JSON extraction from an LLM response string."""
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def extract_fields(user_input: str, missing_fields: list) -> dict:
    """
    Return a dict of {field: value} for any missing fields found in user_input.
    Deterministic rules run first; the LLM handles the rest in one call.
    """
    if not missing_fields:
        return {}

    extracted = {}
    needs_llm = list(missing_fields)

    # --- Deterministic extraction ---
    if "age" in needs_llm:
        age_candidate = _try_extract_age(user_input)
        if age_candidate:
            is_valid, _ = validate_field("age", age_candidate)
            if is_valid:
                extracted["age"] = age_candidate
                needs_llm.remove("age")

    # --- LLM extraction for remaining fields ---
    if needs_llm:
        prompt = f"""The user said: "{user_input}"

Extract any of these profile fields if they are clearly mentioned or strongly implied:
{', '.join(needs_llm)}

Rules:
- Only include fields you are confident about
- For "age", return just the number as a string
- For "interests", return a comma-separated string
- For "bio", return a short summary of what they said about themselves
- Return a JSON object with only the fields you found
- If nothing is extractable, return {{}}

Return ONLY valid JSON. Example: {{"name": "Alex", "location": "Seattle"}}"""

        response = ollama.chat(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        llm_result = _parse_json_from_response(response["message"]["content"])
        extracted.update(llm_result)

    return extracted
