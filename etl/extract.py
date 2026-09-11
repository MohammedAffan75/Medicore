import os
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple

from .config import CONFIG

def _read_csv(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path)

def _read_json(file_path: Path) -> pd.DataFrame:
    return pd.read_json(file_path, orient='records')

def extract() -> Dict[str, pd.DataFrame]:
    """Extract data from source files defined in CONFIG.file_map.

    Returns:
        A dictionary mapping entity names to pandas DataFrames.
    """
    data_dir = CONFIG.source_path
    extracted: Dict[str, pd.DataFrame] = {}
    for entity, (filename, fmt) in CONFIG.file_map.items():
        file_path = data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Source file for {entity} not found: {file_path}")
        if fmt.lower() == 'csv':
            df = _read_csv(file_path)
        elif fmt.lower() == 'json':
            df = _read_json(file_path)
        else:
            raise ValueError(f"Unsupported format '{fmt}' for {entity}")
        extracted[entity] = df
    return extracted
