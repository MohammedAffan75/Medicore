# etl/validate.py
"""Validation utilities for the ETL pipeline.
Each function returns a tuple ``(clean_df, errors)`` where ``errors`` is a list of strings
capturing rows that were rejected and the reason.
"""
import pandas as pd
from typing import List, Tuple, Dict

# Define required columns per entity (required for the "drop if missing" rule)
REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "patients": ["first_name", "last_name", "email", "date_of_birth"],
    "providers": ["first_name", "last_name", "email", "department_id"],
    "departments": ["name"],
    "appointments": ["patient_id", "provider_id", "appointment_date", "start_time"],
    "encounters": ["appointment_id", "notes"],
    "diagnoses": ["diagnosis_code", "description"],
    "medications": ["medication_name", "dosage_form"],
    "prescriptions": ["patient_id", "provider_id", "medication_id", "prescribed_date"],
    "invoices": ["invoice_id", "patient_id", "total_amount"],
    "payments": ["transaction_id", "invoice_id", "amount", "payment_date"],
}

def _check_required(df: pd.DataFrame, entity: str) -> Tuple[pd.DataFrame, List[str]]:
    """Drop rows missing any required column values.
    Returns cleaned DataFrame and list of error messages.
    """
    required = REQUIRED_COLUMNS.get(entity, [])
    errors: List[str] = []
    mask = df[required].notnull().all(axis=1)
    dropped = df[~mask]
    for idx, row in dropped.iterrows():
        missing = [col for col in required if pd.isna(row[col])]
        errors.append(f"{entity} row {idx}: missing required columns {missing}")
    return df[mask].copy(), errors

def detect_duplicates(df: pd.DataFrame, key_cols: List[str]) -> List[str]:
    """Return a list of error messages for duplicate rows based on ``key_cols``.
    The duplicate rows are left untouched – caller can decide to drop them.
    """
    errors: List[str] = []
    dup_mask = df.duplicated(subset=key_cols, keep=False)
    dup_rows = df[dup_mask]
    for idx, row in dup_rows.iterrows():
        errors.append(f"Duplicate {key_cols} in row {idx}: {row[key_cols].to_dict()}")
    return errors

def validate_dates(df: pd.DataFrame, date_cols: List[str]) -> List[str]:
    """Validate that date columns can be parsed as pandas ``datetime`` objects.
    Invalid rows are recorded as errors and removed from the DataFrame.
    """
    errors: List[str] = []
    for col in date_cols:
        if col not in df.columns:
            continue
        parsed = pd.to_datetime(df[col], errors="coerce")
        invalid = parsed.isna()
        for idx in df[invalid].index:
            errors.append(f"Invalid date in column '{col}' at row {idx}: {df.at[idx, col]}")
        df.loc[invalid, col] = pd.NaT
    # Drop rows that now contain NaT in any of the validated date columns
    mask = df[date_cols].notna().all(axis=1)
    df.drop(df[~mask].index, inplace=True)
    return errors

def validate_entity(df: pd.DataFrame, entity: str) -> Tuple[pd.DataFrame, List[str]]:
    """Run all generic validations for a given entity.
    Returns cleaned DataFrame and accumulated error messages.
    """
    errors: List[str] = []
    # 1. Required fields
    df, req_err = _check_required(df, entity)
    errors.extend(req_err)
    # 2. Duplicate detection – callers provide natural key list via config
    # (skip here; handled in pipeline when key list known)
    # 3. Date validation – infer columns ending with '_date' or '_datetime'
    date_cols = [c for c in df.columns if c.endswith("_date") or c.endswith("_datetime")]
    date_err = validate_dates(df, date_cols)
    errors.extend(date_err)
    return df, errors

# Export symbols for import elsewhere
__all__ = ["validate_entity", "detect_duplicates", "validate_dates"]
