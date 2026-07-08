"""
Unit tests for utils.py — covers all deterministic helper functions.
LLM-dependent logic (extract_field, generate_response) is not tested here
because AI responses are non-deterministic and belong in integration tests.
"""

import pytest
from utils import (
    validate_name, validate_age, validate_bio, validate_field,
    clean_text, format_profile_for_display, get_completion_percentage,
    save_json, load_json,
)


# --- validate_name ---

def test_validate_name_valid():
    assert validate_name("Alex") == (True, "Name is valid")

def test_validate_name_too_short():
    valid, msg = validate_name("A")
    assert not valid
    assert "at least" in msg

def test_validate_name_too_long():
    valid, msg = validate_name("A" * 51)
    assert not valid
    assert "less than" in msg

def test_validate_name_empty():
    valid, _ = validate_name("")
    assert not valid

def test_validate_name_none():
    valid, _ = validate_name(None)
    assert not valid


# --- validate_age ---

def test_validate_age_valid():
    assert validate_age(25) == (True, "Age is valid")

def test_validate_age_string_number():
    assert validate_age("30") == (True, "Age is valid")

def test_validate_age_too_young():
    valid, msg = validate_age(17)
    assert not valid
    assert "18" in msg

def test_validate_age_too_old():
    valid, msg = validate_age(121)
    assert not valid

def test_validate_age_not_a_number():
    valid, msg = validate_age("old")
    assert not valid
    assert "number" in msg


# --- validate_bio ---

def test_validate_bio_valid():
    assert validate_bio("I love hiking and cooking outdoors.") == (True, "Bio is valid")

def test_validate_bio_too_short():
    valid, msg = validate_bio("Hi")
    assert not valid
    assert "at least" in msg

def test_validate_bio_empty():
    valid, _ = validate_bio("")
    assert not valid


# --- validate_field dispatcher ---

def test_validate_field_name():
    assert validate_field("name", "Jordan")[0] is True

def test_validate_field_age():
    assert validate_field("age", "28")[0] is True

def test_validate_field_bio():
    assert validate_field("bio", "I enjoy long walks and good coffee.")[0] is True

def test_validate_field_unknown_non_empty():
    assert validate_field("location", "New York")[0] is True

def test_validate_field_unknown_empty():
    assert validate_field("location", "")[0] is False


# --- clean_text ---

def test_clean_text_strips_whitespace():
    assert clean_text("  hello  ") == "hello"

def test_clean_text_collapses_spaces():
    assert clean_text("hello   world") == "hello world"

def test_clean_text_empty():
    assert clean_text("") == ""

def test_clean_text_none():
    assert clean_text(None) == ""


# --- get_completion_percentage ---

def test_completion_all_filled():
    profile = {"name": "Alex", "age": "28", "created_at": "2024-01-01"}
    assert get_completion_percentage(profile) == 100.0

def test_completion_half_filled():
    profile = {"name": "Alex", "age": None, "created_at": "2024-01-01"}
    assert get_completion_percentage(profile) == 50.0

def test_completion_empty_profile():
    assert get_completion_percentage({}) == 0.0


# --- format_profile_for_display ---

def test_format_profile_contains_name():
    profile = {"name": "Alex", "age": "28", "created_at": "2024-01-01"}
    output = format_profile_for_display(profile)
    assert "Alex" in output
    assert "28" in output

def test_format_profile_skips_none():
    profile = {"name": "Alex", "age": None, "created_at": "2024-01-01"}
    output = format_profile_for_display(profile)
    assert "None" not in output


# --- save_json / load_json ---

def test_save_and_load_json(tmp_path):
    data = {"name": "Alex", "age": 28}
    filepath = str(tmp_path / "profile.json")
    assert save_json(data, filepath) is True
    loaded = load_json(filepath)
    assert loaded == data

def test_load_json_missing_file():
    assert load_json("nonexistent_file.json") is None
