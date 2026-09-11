# etl/pipeline.py
"""ETL pipeline orchestrator.

It sequentially runs extraction, validation, transformation, and loading while
maintaining statistics and logging progress. Errors in validation are collected
and reported at the end. Fatal database errors abort the current entity but the
pipeline continues with remaining entities.
"""

from dataclasses import dataclass, field
from typing import Dict, List
import sys

import pandas as pd
from loguru import logger

from .extract import extract
from .validate import validate_entity, detect_duplicates
from .transform import transform
from .load import load
from .config import CONFIG


@dataclass
class PipelineStats:
    extracted: int = 0
    rejected: int = 0
    transformed: int = 0
    loaded: int = 0
    entity_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)

    def add_entity_stats(self, entity: str, extracted: int, rejected: int, transformed: int, loaded: int):
        self.entity_counts[entity] = {
            "extracted": extracted,
            "rejected": rejected,
            "transformed": transformed,
            "loaded": loaded,
        }
        self.extracted += extracted
        self.rejected += rejected
        self.transformed += transformed
        self.loaded += loaded


def _setup_logging():
    # Ensure log directory exists (handled by Config)
    logger.remove()
    logger.add(sys.stdout, level=CONFIG.log_level)
    logger.add(str(CONFIG.log_file), rotation="10 MB", level=CONFIG.log_level, serialize=True)


def run_pipeline():
    _setup_logging()
    logger.info("ETL pipeline started")
    stats = PipelineStats()

    # 1. Extraction
    raw_data: Dict[str, pd.DataFrame] = extract()
    logger.info(f"Extracted entities: {list(raw_data.keys())}")

    # 2. Validation per entity
    validated_data: Dict[str, pd.DataFrame] = {}
    for entity, df in raw_data.items():
        logger.info(f"Validating {entity} (rows: {len(df)})")
        # Detect duplicates based on natural keys (defined in load.NATURAL_KEYS)
        key_cols = []
        if entity in load.NATURAL_KEYS:
            key_cols = load.NATURAL_KEYS[entity]
        dup_errors = detect_duplicates(df, key_cols) if key_cols else []
        # Run generic validation (required fields, date parsing)
        clean_df, val_errors = validate_entity(df, entity)
        # Combine errors
        errors = dup_errors + val_errors
        if errors:
            stats.validation_errors.extend(errors)
            # Drop rows that were flagged as duplicate (optional – we keep them for now)
            # For simplicity, we drop rows that appear in duplicate list
            if key_cols:
                clean_df = clean_df.drop_duplicates(subset=key_cols, keep='first')
        rejected = len(df) - len(clean_df)
        extracted = len(df)
        stats.add_entity_stats(entity, extracted, rejected, 0, 0)
        validated_data[entity] = clean_df
        logger.info(f"{entity}: extracted={extracted}, rejected={rejected}, valid={len(clean_df)}")

    # 3. Transformation
    transformed_data = transform(validated_data)
    for entity, df in transformed_data.items():
        stats.entity_counts[entity]["transformed"] = len(df)
        stats.transformed += len(df)
        logger.info(f"{entity}: transformed rows={len(df)}")

    # 4. Loading
    try:
        load_results = load(transformed_data)
        for entity, rows_loaded in load_results.items():
            stats.entity_counts[entity]["loaded"] = rows_loaded
            stats.loaded += rows_loaded
            logger.info(f"{entity}: loaded rows={rows_loaded}")
    except RuntimeError as e:
        logger.error(str(e))
        # Continue with remaining entities already handled; fatal errors per entity are already raised.

    # 5. Summary logging
    logger.info("ETL pipeline completed")
    logger.info(f"Total extracted: {stats.extracted}, rejected: {stats.rejected}, transformed: {stats.transformed}, loaded: {stats.loaded}")
    if stats.validation_errors:
        logger.warning(f"Validation errors encountered ({len(stats.validation_errors)}):")
        for err in stats.validation_errors:
            logger.warning(err)
    return stats

if __name__ == "__main__":
    run_pipeline()
