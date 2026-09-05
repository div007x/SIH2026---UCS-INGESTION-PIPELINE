import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
import numpy as np
from src.pipeline_runner import load_pipeline_config
from src.window_aggregator import create_1min_windows
from src.labeler_and_splits import assign_window_labels, generate_future_attack_labels, assign_chronological_splits, apply_purge_embargo, assign_episode_ids

def main():
    config = load_pipeline_config("configs/pipeline_config.yaml")
    intermediate_dir = config["paths"]["intermediate_dir"]
    target_files = config.get("target_files", [])

    all_window_dfs = []
    for tf in target_files:
        inter_parquet = os.path.join(intermediate_dir, f"cleaned_{os.path.splitext(tf)[0]}.parquet")
        df_cleaned = pd.read_parquet(inter_parquet)
        if not pd.api.types.is_datetime64_any_dtype(df_cleaned["timestamp_utc"]):
            df_cleaned["timestamp_utc"] = pd.to_datetime(df_cleaned["timestamp_utc"], utc=True)
        window_df, win_audit = create_1min_windows(df_cleaned, interval_sec=config["windowing"]["interval_sec"])
        window_df, label_audit = assign_window_labels(window_df)
        all_window_dfs.append(window_df)

    full_windows_df = pd.concat(all_window_dfs, ignore_index=True)
    full_windows_df = full_windows_df.sort_values("window_start_utc").reset_index(drop=True)

    horizon_windows = config["forecasting"]["horizon_windows"]
    full_windows_df = generate_future_attack_labels(
        full_windows_df,
        horizon_windows=horizon_windows,
        target_col=config["forecasting"]["target_col"],
        future_col=config["forecasting"]["future_label_col"],
    )

    full_windows_df, split_audit = assign_chronological_splits(
        full_windows_df,
        train_ratio=config["splits"]["train_ratio"],
        val_ratio=config["splits"]["val_ratio"],
        test_ratio=config["splits"]["test_ratio"],
    )

    # Let's inspect the entire Friday-02-03-2018 in full_windows_df
    fri_df = full_windows_df[full_windows_df["source_day"] == "02-03-2018"].copy()
    print(f"Friday-02-03-2018 in full_windows_df has {len(fri_df)} windows")
    print(f"Friday index range in full_windows_df: {fri_df.index[0]} to {fri_df.index[-1]}")
    print("Friday splits distribution:")
    print(fri_df["split"].value_counts())

    # Check test split start and embargo zone
    test_idx = full_windows_df.index[full_windows_df["split"] == "test"]
    val_idx = full_windows_df.index[full_windows_df["split"] == "val"]
    
    print(f"Val split indices: [{val_idx[0]}..{val_idx[-1]}], timestamps: [{full_windows_df.loc[val_idx[0], 'window_start_utc']} .. {full_windows_df.loc[val_idx[-1], 'window_start_utc']}]")
    print(f"Test split indices: [{test_idx[0]}..{test_idx[-1]}], timestamps: [{full_windows_df.loc[test_idx[0], 'window_start_utc']} .. {full_windows_df.loc[test_idx[-1], 'window_start_utc']}]")

    width = 35
    val_tail_dropped = val_idx[-width:]
    test_head_dropped = test_idx[:width]

    print("\n--- Val Tail Dropped (35 windows) ---")
    print(f"Index range: [{val_tail_dropped[0]}..{val_tail_dropped[-1]}], timestamps: [{full_windows_df.loc[val_tail_dropped[0], 'window_start_utc']} .. {full_windows_df.loc[val_tail_dropped[-1], 'window_start_utc']}]")
    print("Source days in val tail dropped:", full_windows_df.loc[val_tail_dropped, "source_day"].value_counts().to_dict())
    print("Labels in val tail dropped:", full_windows_df.loc[val_tail_dropped, "label_attack_type"].value_counts().to_dict())

    print("\n--- Test Head Dropped (35 windows) ---")
    print(f"Index range: [{test_head_dropped[0]}..{test_head_dropped[-1]}], timestamps: [{full_windows_df.loc[test_head_dropped[0], 'window_start_utc']} .. {full_windows_df.loc[test_head_dropped[-1], 'window_start_utc']}]")
    print("Source days in test head dropped:", full_windows_df.loc[test_head_dropped, "source_day"].value_counts().to_dict())
    print("Labels in test head dropped:", full_windows_df.loc[test_head_dropped, "label_attack_type"].value_counts().to_dict())

    print("\nAll 35 Test Head Dropped Windows:")
    print(full_windows_df.loc[test_head_dropped, ["window_id", "window_start_utc", "source_day", "label_binary", "label_attack_type", "has_malicious_flows", "future_attack_label"]].to_string())

    # Check the first Botnet episode in raw data:
    # We found earlier in Step 1:
    # Episode 1: 2018-03-02 02:24:00+00:00 to 2018-03-02 02:28:00+00:00 (5 windows)
    # Let's find where those 5 windows are in full_windows_df!
    raw_ep1_mask = (full_windows_df["source_day"] == "02-03-2018") & (full_windows_df["window_start_utc"] >= "2018-03-02 02:24:00") & (full_windows_df["window_start_utc"] <= "2018-03-02 02:28:00")
    raw_ep1_df = full_windows_df[raw_ep1_mask]
    print("\n--- RAW BOTNET EPISODE 1 WINDOWS IN FULL_WINDOWS_DF ---")
    print(raw_ep1_df[["window_id", "window_start_utc", "source_day", "split", "label_binary", "label_attack_type", "future_attack_label"]].to_string())

    print(f"\nAre all 5 windows of RAW Episode 1 inside val_tail_dropped or test_head_dropped?")
    in_val_tail = raw_ep1_df.index.isin(val_tail_dropped)
    in_test_head = raw_ep1_df.index.isin(test_head_dropped)
    print("In val_tail_dropped:", in_val_tail.tolist())
    print("In test_head_dropped:", in_test_head.tolist())
    print("In either dropped set:", (in_val_tail | in_test_head).tolist())

if __name__ == "__main__":
    main()
