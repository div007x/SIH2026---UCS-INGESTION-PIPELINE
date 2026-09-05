import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
import numpy as np
from src.window_aggregator import create_1min_windows
from src.labeler_and_splits import assign_window_labels

def main():
    inter_parquet = "data/intermediate/cleaned_Friday-02-03-2018_TrafficForML_CICFlowMeter.parquet"
    df_cleaned = pd.read_parquet(inter_parquet)
    if not pd.api.types.is_datetime64_any_dtype(df_cleaned["timestamp_utc"]):
        df_cleaned["timestamp_utc"] = pd.to_datetime(df_cleaned["timestamp_utc"], utc=True)

    print(f"Cleaned flows count: {len(df_cleaned)}")
    print("Flow label distribution:")
    print(df_cleaned["raw_label"].value_counts())

    window_df, win_audit = create_1min_windows(df_cleaned, interval_sec=60)
    print(f"Windows generated: {len(window_df)}")
    print(f"Window start min: {window_df['window_start_utc'].min()}, max: {window_df['window_start_utc'].max()}")

    window_df, label_audit = assign_window_labels(window_df)
    print("\nPre-purge window label distribution:")
    print(window_df["label_attack_type"].value_counts())

    # Contiguous runs methodology
    # Exact definition: unbroken sequence of attack-labeled windows = one episode
    window_df = window_df.sort_values("window_start_utc").reset_index(drop=True)
    
    # Let's inspect contiguous Botnet runs
    botnet_mask = (window_df["label_attack_type"] == "Botnet").astype(int)
    
    # Identify run starts and ends
    # A run starts when botnet_mask is 1 and previous is 0 (or start of df)
    # A run ends when botnet_mask is 1 and next is 0 (or end of df)
    
    # We can also use diff or cumsum grouping
    run_starts = (botnet_mask == 1) & (botnet_mask.shift(1, fill_value=0) == 0)
    run_ids = run_starts.cumsum() * botnet_mask
    
    print("\n--- PRE-PURGE BOTNET EPISODES TABLE ---")
    episodes = []
    for r_id in range(1, run_ids.max() + 1):
        ep_df = window_df[run_ids == r_id]
        if len(ep_df) == 0:
            continue
        start_idx = ep_df.index[0]
        end_idx = ep_df.index[-1]
        start_win = ep_df["window_id"].iloc[0]
        end_win = ep_df["window_id"].iloc[-1]
        start_ts = ep_df["window_start_utc"].iloc[0]
        end_ts = ep_df["window_start_utc"].iloc[-1]
        win_count = len(ep_df)
        episodes.append({
            "episode_num": len(episodes) + 1,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "start_window_id": start_win,
            "end_window_id": end_win,
            "start_timestamp_utc": str(start_ts),
            "end_timestamp_utc": str(end_ts),
            "window_count": win_count
        })
    
    ep_df_summary = pd.DataFrame(episodes)
    print(f"Total RAW Pre-Purge Botnet Episodes Found: {len(ep_df_summary)}")
    print(ep_df_summary.to_string(index=False))

if __name__ == "__main__":
    main()
