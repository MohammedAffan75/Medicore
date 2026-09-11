# etl/tests/test_validate.py
"""Unit tests for ETL validation functions."""

import pandas as pd
import pytest
from etl.validate import _check_required, detect_duplicates, validate_dates, validate_entity


def test_check_required_missing_fields():
    df = pd.DataFrame({
        "first_name": ["John", None],
        "last_name": ["Doe", "Smith"],
        "email": ["john@example.com", "jane@example.com"],
        "date_of_birth": ["1990-01-01", "1985-05-12"],
    })
    cleaned, errors = _check_required(df, "patients")
    assert len(cleaned) == 1
    assert len(errors) == 1
    assert "missing required columns" in errors[0]


def test_detect_duplicates():
    df = pd.DataFrame({
        "email": ["a@example.com", "a@example.com", "b@example.com"]
    })
    dup_errors = detect_duplicates(df, ["email"])
    assert len(dup_errors) == 2  # both duplicate rows reported


def test_validate_dates_invalid():
    df = pd.DataFrame({
        "appointment_date": ["2023-01-01", "not-a-date", "2023-03-15"]
    })
    errors = validate_dates(df, ["appointment_date"])
    assert len(errors) == 1
    assert "Invalid date" in errors[0]
    # the invalid row should have NaT and be dropped in the calling function


def test_validate_entity_combined():
    df = pd.DataFrame({
        "first_name": ["John", ""],
        "last_name": ["Doe", "Smith"],
        "email": ["john@example.com", None],
        "date_of_birth": ["1990-01-01", "invalid"]
    })
    cleaned, errors = validate_entity(df, "patients")
    # Expect one row dropped due to missing required fields, and one date error
    assert len(cleaned) == 1
    assert any("missing required columns" in e for e in errors)
    assert any("Invalid date" in e for e in errors)
