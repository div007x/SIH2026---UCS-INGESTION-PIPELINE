import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
import numpy as np
import yaml
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

    print("--- SPLIT BOUNDARIES PRE-PURGE ---")
    print(f"Total windows pre-purge: {len(full_windows_df)}")
    for s in ["train", "val", "test"]:
        sub = full_windows_df[full_windows_df["split"] == s]
        print(f"Split {s}: {len(sub)} windows, range [{sub.index[0]}..{sub.index[-1]}], "
              f"time: [{sub['window_start_utc'].min()} .. {sub['window_start_utc'].max()}]")

    # Let's check raw episodes across all days
    full_pre_purge_with_ep = assign_episode_ids(full_windows_df.copy())
    raw_episodes = full_pre_purge_with_ep[full_pre_purge_with_ep["label_attack_type"] != "Benign"].groupby(["source_day", "label_attack_type", "episode_id"]).agg(
        start_time=("window_start_utc", "min"),
        end_time=("window_start_utc", "max"),
        count=("window_start_utc", "count"),
        min_idx=("window_start_utc", lambda s: full_pre_purge_with_ep.loc[s.index].index[0]),
        max_idx=("window_start_utc", lambda s: full_pre_purge_with_ep.loc[s.index].index[-1]),
        split=("split", lambda s: list(s.unique()))
    ).reset_index()

    print(f"\n--- TOTAL RAW EPISODES PRE-PURGE (ALL ATTACK TYPES): {len(raw_episodes)} ---")
    print(raw_episodes.groupby("label_attack_type")["episode_id"].count())

    # Apply purge + embargo
    lookback_windows = config["lstm"]["lookback_windows"]
    purged_df, purge_audit = apply_purge_embargo(
        full_windows_df,
        lookback_windows=lookback_windows,
        horizon_windows=horizon_windows,
    )
    
    # Identify exactly which windows were dropped
    width = lookback_windows + horizon_windows
    train_idx = full_windows_df.index[full_windows_df["split"] == "train"]
    val_idx = full_windows_df.index[full_windows_df["split"] == "val"]
    test_idx = full_windows_df.index[full_windows_df["split"] == "test"]

    train_drop = set(train_idx[-width:]) if len(train_idx) >= width else set(train_idx)
    val_drop_front = set(val_idx[:width]) if len(val_idx) >= width else set(val_idx)
    val_drop_back = set(val_idx[-width:]) if len(val_idx) >= width else set(val_idx)
    test_drop = set(test_idx[:width]) if len(test_idx) >= width else set(test_idx)

    print("\n--- PURGE/EMBARGO ZONES DETAILS ---")
    print(f"Purge width: {width} (L={lookback_windows}, H={horizon_windows})")
    
    print("\n[Train -> Val Boundary Dropped Windows]")
    train_drop_df = full_windows_df.loc[sorted(train_drop)]
    val_front_drop_df = full_windows_df.loc[sorted(val_drop_front)]
    print(f"Train tail dropped: {len(train_drop_df)} windows, [{train_drop_df['window_start_utc'].min()} .. {train_drop_df['window_start_utc'].max()}]")
    print(f"Val head dropped: {len(val_front_drop_df)} windows, [{val_front_drop_df['window_start_utc'].min()} .. {val_front_drop_df['window_start_utc'].max()}]")

    print("\n[Val -> Test Boundary Dropped Windows]")
    val_back_drop_df = full_windows_df.loc[sorted(val_drop_back)]
    test_drop_df = full_windows_df.loc[sorted(test_drop)]
    print(f"Val tail dropped: {len(val_back_drop_df)} windows, [{val_back_drop_df['window_start_utc'].min()} .. {val_back_drop_df['window_start_utc'].max()}]")
    print(f"Test head dropped: {len(test_drop_df)} windows, [{test_drop_df['window_start_utc'].min()} .. {test_drop_df['window_start_utc'].max()}]")

    print("\n--- TEST HEAD DROPPED WINDOWS INSPECTION ---")
    print(test_drop_df[["window_id", "window_start_utc", "source_day", "label_binary", "label_attack_type", "future_attack_label"]].to_string())

    # Let's inspect post-purge episodes
    purged_df = assign_episode_ids(purged_df)
    post_episodes = purged_df[purged_df["label_attack_type"] != "Benign"].groupby(["source_day", "label_attack_type", "episode_id"]).agg(
        start_time=("window_start_utc", "min"),
        end_time=("window_start_utc", "max"),
        count=("window_start_utc", "count"),
        split=("split", lambda s: list(s.unique()))
    ).reset_index()

    print(f"\n--- POST-PURGE EPISODES (ALL ATTACK TYPES): {len(post_episodes)} ---")
    print(post_episodes.groupby("label_attack_type")["episode_id"].count())
    print("\nPost-purge episodes details:")
    print(post_episodes.to_string())

if __name__ == "__main__":
    main()
