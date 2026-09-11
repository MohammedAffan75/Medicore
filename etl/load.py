# etl/load.py
"""Load module for the ETL pipeline.

It receives transformed DataFrames and bulk‑inserts them into PostgreSQL using
SQLAlchemy Core + psycopg2 ``execute_values`` for speed. ``ON CONFLICT`` clauses
are applied based on the natural keys you specified, guaranteeing idempotency.
"""

from typing import Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from psycopg2.extras import execute_values
import psycopg2
from .config import CONFIG

# Mapping of entity -> natural key columns for ON CONFLICT handling
NATURAL_KEYS = {
    "patients": ["email"],
    "providers": ["email"],
    "departments": ["name"],
    "appointments": ["patient_id", "provider_id", "appointment_date", "start_time"],
    "diagnoses": ["diagnosis_code"],
    "medications": ["medication_name"],
    "invoices": ["invoice_id"],
    "payments": ["transaction_id"],
}


def _engine() -> Engine:
    return create_engine(CONFIG.db_url, echo=False, future=True)


def _upsert_sql(table: str, columns: list, conflict_cols: list) -> str:
    cols_str = ", ".join(columns)
    placeholders = ", ".join([f"%s" for _ in columns])
    conflict_str = ", ".join(conflict_cols)
    update_assignments = ", ".join([f"{col}=EXCLUDED.{col}" for col in columns if col not in conflict_cols])
    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT ({conflict_str}) DO UPDATE SET {update_assignments}" if update_assignments else f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT ({conflict_str}) DO NOTHING"
    return sql


def load(transformed: Dict[str, pd.DataFrame]) -> Dict[str, int]:
    """Bulk load transformed DataFrames into PostgreSQL.

    Returns a dict mapping entity name to the number of rows successfully inserted.
    """
    engine = _engine()
    inserted_counts: Dict[str, int] = {}
    # Use a raw psycopg2 connection for execute_values (fast bulk copy)
    with engine.begin() as conn:
        raw_conn = conn.connection
        cursor = raw_conn.cursor()
        for entity, df in transformed.items():
            if df.empty:
                inserted_counts[entity] = 0
                continue
            # Prepare column list – ensure order matches DataFrame columns
            columns = list(df.columns)
            # Determine conflict columns – default to natural keys if defined
            conflict_cols = NATURAL_KEYS.get(entity, [])
            sql = _upsert_sql(entity, columns, conflict_cols)
            # Convert DataFrame rows to list of tuples
            values = [tuple(row) for row in df.itertuples(index=False, name=None)]
            try:
                execute_values(cursor, sql, values, page_size=CONFIG.batch_size)
                inserted_counts[entity] = cursor.rowcount
            except Exception as exc:
                # Fatal DB error for this entity – re‑raise after logging by caller
                raise RuntimeError(f"Failed to load entity '{entity}': {exc}")
        raw_conn.commit()
    return inserted_counts

__all__ = ["load"]
