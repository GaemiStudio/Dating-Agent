"""
Tests for skills/field_extractor.py

Covers the deterministic age regex path (no LLM) and the LLM extraction
path (mocked so tests run without Ollama or Gemini).
"""

from unittest.mock import patch
from skills.field_extractor import extract_fields, _try_extract_age


# --- Deterministic age extraction ---

def test_extract_age_plain_number():
    assert _try_extract_age("I am 28 years old") == "28"

def test_extract_age_at_word_boundary():
    assert _try_extract_age("I'm 35, living in Paris") == "35"

def test_extract_age_year_not_extracted():
    """Years like 1998 should not be matched."""
    assert _try_extract_age("I was born in 1998") is None

def test_extract_age_underage_not_extracted():
    assert _try_extract_age("I am 17") is None

def test_extract_age_minimum_boundary():
    assert _try_extract_age("I just turned 18") == "18"

def test_extract_age_maximum_boundary():
    assert _try_extract_age("I am 120") == "120"

def test_extract_age_no_number():
    assert _try_extract_age("I love hiking") is None


# --- Full extract_fields (mocked LLM) ---

def test_age_extracted_without_llm_call():
    """Age from a plain number should bypass the LLM entirely."""
    with patch("skills.field_extractor.chat") as mock_chat:
        result = extract_fields("I'm 25 years old", ["age"])
        mock_chat.assert_not_called()
        assert result.get("age") == "25"

def test_non_age_field_calls_llm():
    """Fields the regex can't handle should go to the LLM."""
    with patch("skills.field_extractor.chat", return_value='{"name": "Alex"}') as mock_chat:
        result = extract_fields("My name is Alex", ["name"])
        mock_chat.assert_called_once()
        assert result.get("name") == "Alex"

def test_empty_missing_fields_returns_empty():
    """Nothing missing — should return immediately without calling LLM."""
    with patch("skills.field_extractor.chat") as mock_chat:
        result = extract_fields("I love pizza", [])
        mock_chat.assert_not_called()
        assert result == {}

def test_bad_llm_json_returns_empty():
    """If LLM returns non-JSON, should return empty dict gracefully."""
    with patch("skills.field_extractor.chat", return_value="Sure, I'd be happy to help!"):
        result = extract_fields("something", ["name"])
        assert result == {}

def test_mixed_age_and_other_fields():
    """Age handled by regex, remaining fields sent to LLM."""
    with patch("skills.field_extractor.chat", return_value='{"location": "Seattle"}') as mock_chat:
        result = extract_fields("I'm 30 and I live in Seattle", ["age", "location"])
        mock_chat.assert_called_once()
        assert result.get("age") == "30"
        assert result.get("location") == "Seattle"
