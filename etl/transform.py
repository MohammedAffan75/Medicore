# etl/transform.py
"""Transformation utilities for the ETL pipeline.

The module receives raw pandas DataFrames from ``extract`` and returns cleaned
DataFrames ready for loading. It handles:

* Normalisation of strings (title‑casing names, standardising gender values,
  cleaning phone numbers).
* Resolution of foreign‑key columns by looking up the appropriate ``id``
  values from reference DataFrames (e.g. department name → department.id).
* Casting of columns to the final PostgreSQL types.
"""

import re
from typing import Dict
import pandas as pd

from .config import CONFIG

# ---------------------------------------------------------------------------
# Helper normalisation functions
# ---------------------------------------------------------------------------

def _normalize_phone(phone: str) -> str:
    """Return a phone number in the format ``+<countrycode><digits>``.
    Non‑digit characters are stripped. If the number does not start with a ``+``
    the default country code ``+1`` (US) is prefixed.
    """
    if pd.isna(phone):
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if not phone.strip().startswith("+"):
        digits = "1" + digits
    return f"+{digits}"

def _standardize_gender(gender: str) -> str:
    """Map various gender representations to ``M``, ``F`` or ``O``.
    Missing or unknown values are returned as ``None``.
    """
    if pd.isna(gender):
        return None
    g = gender.strip().lower()
    if g in {"male", "m", "man"}:
        return "M"
    if g in {"female", "f", "woman"}:
        return "F"
    if g in {"other", "o", "nonbinary", "non-binary"}:
        return "O"
    return None

def _title_case_name(name: str) -> str:
    """Return a name with each part title‑cased (e.g. ``john doe`` → ``John Doe``)."""
    if pd.isna(name):
        return None
    return " ".join(part.capitalize() for part in name.split())

# ---------------------------------------------------------------------------
# Foreign‑key resolution utilities
# ---------------------------------------------------------------------------

def _resolve_fk(df: pd.DataFrame, lookup_df: pd.DataFrame, local_col: str, lookup_key: str, lookup_id: str) -> pd.DataFrame:
    """Replace ``local_col`` values with the matching ``lookup_id``.

    Args:
        df: DataFrame that contains the column to be replaced.
        lookup_df: Reference DataFrame that contains ``lookup_key`` and ``lookup_id``.
        local_col: Column name in ``df`` that holds the foreign value (e.g. ``department_name``).
        lookup_key: Column name in ``lookup_df`` that matches ``local_col``.
        lookup_id: Primary‑key column in ``lookup_df`` that should be inserted.
    """
    mapping = lookup_df.set_index(lookup_key)[lookup_id].to_dict()
    df[local_col] = df[local_col].map(mapping)
    return df

# ---------------------------------------------------------------------------
# Main transformation function
# ---------------------------------------------------------------------------

def transform(extracted: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Apply all transformations to the raw ``extracted`` dict.

    Returns a new dictionary where each key is an entity name and the value is a
    DataFrame ready for loading.
    """
    # Create copies so we never mutate the original data frames
    transformed: Dict[str, pd.DataFrame] = {k: v.copy() for k, v in extracted.items()}

    # ---------- Patients ----------
    if "patients" in transformed:
        df = transformed["patients"]
        df["first_name"] = df["first_name"].apply(_title_case_name)
        df["last_name"] = df["last_name"].apply(_title_case_name)
        df["gender"] = df["gender"].apply(_standardize_gender)
        df["phone"] = df["phone"].apply(_normalize_phone)
        # Convert dates to ISO strings for PostgreSQL
        if "date_of_birth" in df.columns:
            df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce").dt.date
        transformed["patients"] = df

    # ---------- Departments (no complex transformation) ----------
    # Ensure name is title‑cased
    if "departments" in transformed:
        df = transformed["departments"]
        df["name"] = df["name"].apply(_title_case_name)
        transformed["departments"] = df

    # ---------- Providers ----------
    if "providers" in transformed:
        df = transformed["providers"]
        df["first_name"] = df["first_name"].apply(_title_case_name)
        df["last_name"] = df["last_name"].apply(_title_case_name)
        df["gender"] = df["gender"].apply(_standardize_gender)
        df["phone"] = df["phone"].apply(_normalize_phone)
        # Resolve department foreign key (department_name → department.id)
        if "department_name" in df.columns and "departments" in transformed:
            df = _resolve_fk(df, transformed["departments"], "department_name", "name", "id")
        transformed["providers"] = df

    # ---------- Appointments ----------
    if "appointments" in transformed:
        df = transformed["appointments"]
        # Resolve patient and provider foreign keys if they are stored as email
        if "patient_email" in df.columns and "patients" in transformed:
            df = _resolve_fk(df, transformed["patients"], "patient_email", "email", "id")
        if "provider_email" in df.columns and "providers" in transformed:
            df = _resolve_fk(df, transformed["providers"], "provider_email", "email", "id")
        # Convert appointment datetime fields
        if "appointment_date" in df.columns:
            df["appointment_date"] = pd.to_datetime(df["appointment_date"], errors="coerce").dt.date
        if "start_time" in df.columns:
            df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce").dt.time
        transformed["appointments"] = df

    # ---------- Encounters ----------
    if "encounters" in transformed:
        df = transformed["encounters"]
        # Resolve appointment foreign key if stored as a composite key – we assume
        # the raw data already contains ``appointment_id``.
        transformed["encounters"] = df

    # ---------- Diagnoses ----------
    if "diagnoses" in transformed:
        df = transformed["diagnoses"]
        df["diagnosis_code"] = df["diagnosis_code"].str.upper().str.strip()
        transformed["diagnoses"] = df

    # ---------- Medications ----------
    if "medications" in transformed:
        df = transformed["medications"]
        df["medication_name"] = df["medication_name"].apply(_title_case_name)
        transformed["medications"] = df

    # ---------- Prescriptions ----------
    if "prescriptions" in transformed:
        df = transformed["prescriptions"]
        # Resolve patient, provider and medication IDs if they are supplied as
        # natural keys (email / name).
        if "patient_email" in df.columns and "patients" in transformed:
            df = _resolve_fk(df, transformed["patients"], "patient_email", "email", "id")
        if "provider_email" in df.columns and "providers" in transformed:
            df = _resolve_fk(df, transformed["providers"], "provider_email", "email", "id")
        if "medication_name" in df.columns and "medications" in transformed:
            df = _resolve_fk(df, transformed["medications"], "medication_name", "medication_name", "id")
        # Parse prescription dates
        if "prescribed_date" in df.columns:
            df["prescribed_date"] = pd.to_datetime(df["prescribed_date"], errors="coerce").dt.date
        transformed["prescriptions"] = df

    # ---------- Invoices ----------
    if "invoices" in transformed:
        df = transformed["invoices"]
        if "patient_email" in df.columns and "patients" in transformed:
            df = _resolve_fk(df, transformed["patients"], "patient_email", "email", "id")
        # Ensure amount is decimal (PostgreSQL NUMERIC)
        if "total_amount" in df.columns:
            df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
        transformed["invoices"] = df

    # ---------- Payments ----------
    if "payments" in transformed:
        df = transformed["payments"]
        if "invoice_id" in df.columns:
            df["invoice_id"] = pd.to_numeric(df["invoice_id"], errors="coerce").astype("Int64")
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        if "payment_date" in df.columns:
            df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce").dt.date
        transformed["payments"] = df

    return transformed

__all__ = ["transform"]
