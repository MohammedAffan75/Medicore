# etl/config.py
"""Configuration for the ETL pipeline.
Loads environment variables from a .env file (or system environment).
Provides a singleton ``CONFIG`` instance for easy import.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from dotenv import load_dotenv

# Load .env located at project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / '.env')

@dataclass
class Config:
    # Database connection URL for SQLAlchemy
    db_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://medicore_user:medicore_password@localhost:5432/medicore",
    )
    # Directory where source CSV/JSON files are stored
    data_dir: Path = Path(os.getenv("ETL_DATA_DIR", project_root / "data" / "source"))
    # Mapping of entity name to (filename, format)
    # CSV for large tabular data; JSON for selected entities (providers, appointments)
    file_map: Dict[str, Tuple[str, str]] = {
        "patients": ("patients.csv", "csv"),
        "providers": ("providers.json", "json"),
        "departments": ("departments.csv", "csv"),
        "appointments": ("appointments.json", "json"),
        "encounters": ("encounters.csv", "csv"),
        "diagnoses": ("diagnoses.csv", "csv"),
        "medications": ("medications.csv", "csv"),
        "prescriptions": ("prescriptions.csv", "csv"),
        "invoices": ("invoices.csv", "csv"),
        "payments": ("payments.csv", "csv"),
    }
    # Batch size for bulk inserts (default 5000, configurable)
    batch_size: int = int(os.getenv("ETL_BATCH_SIZE", "5000"))
    # Logging configuration
    log_file: Path = Path(os.getenv("ETL_LOG_FILE", project_root / "logs" / "etl.log"))
    log_level: str = os.getenv("ETL_LOG_LEVEL", "INFO").upper()

    @property
    def source_path(self) -> Path:
        return self.data_dir

# Export a singleton config instance for easy import
CONFIG = Config()
