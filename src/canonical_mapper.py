"""
Stage 2: Canonical Field Mapping Module
Translates raw 80 CICFlowMeter column names to canonical UCS feature schema.
"""

import os
import yaml
import pandas as pd
from typing import Dict, List, Tuple, Optional


def load_canonical_mapping(config_path: str = "configs/canonical_mapping.yaml") -> Dict[str, any]:
    """Load canonical mapping yaml."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def map_to_canonical_schema(
    df: pd.DataFrame,
    mapping_config: Optional[Dict[str, any]] = None,
    config_path: str = "configs/canonical_mapping.yaml",
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Rename raw columns to canonical names and cast types where applicable.
    """
    if mapping_config is None:
        mapping_config = load_canonical_mapping(config_path)

    col_map = mapping_config.get("mapping", {})

    # Match raw columns against mapping dict (with whitespace stripping)
    rename_dict = {}
    unmapped_raw_cols = []
    
    for raw_col in df.columns:
        stripped = raw_col.strip()
        if stripped in col_map:
            rename_dict[raw_col] = col_map[stripped]
        elif raw_col in ("source_file", "source_day"):
            rename_dict[raw_col] = raw_col
        else:
            unmapped_raw_cols.append(raw_col)

    df_mapped = df.rename(columns=rename_dict).copy()

    audit = {
        "mapped_columns_count": len(rename_dict),
        "unmapped_columns": unmapped_raw_cols,
        "final_columns": list(df_mapped.columns),
    }

    return df_mapped, audit
