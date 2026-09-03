import pandas as pd
import numpy as np

df = pd.read_parquet('data/ucs/ucs_windows.parquet')
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print("=== ALL NUMERIC COLUMNS ===")
for i, col in enumerate(sorted(numeric_cols), 1):
    print(f"{i:3d}. {col}")

metadata_cols = {
    'window_id', 'window_start_utc', 'window_end_utc', 'source_day',
    'split', 'label_binary', 'label_attack_type', 'future_attack_label',
    'raw_label_dominant', 'has_malicious_flows', 'episode_id',
    'forecast_episode_id',
    'mask_has_traffic_volume_features', 'mask_has_flow_timing_features',
    'mask_has_packet_level_features', 'mask_has_tcp_flags',
    'mask_has_graph_topology', 'mask_has_identity_auth'
}

feature_cols_a = [c for c in numeric_cols if c not in metadata_cols]
print("\n=== FEATURE_COLS_A (BEHAVIORAL FEATURES) ===")
for i, col in enumerate(sorted(feature_cols_a), 1):
    print(f"{i:3d}. {col}")
print(f"\nTotal: {len(feature_cols_a)} behavioral columns")

time_keywords = ['hour', 'minute', 'day', 'time', 'date', 'month', 'year', 'utc', 'timestamp', 'cycl', 'sin', 'cos']
time_derived = [c for c in feature_cols_a if any(kw in c.lower() for kw in time_keywords)]
print(f"\n=== COLUMNS WITH TIME-LIKE KEYWORDS ===")
if time_derived:
    for col in sorted(time_derived):
        print(f"  {col}")
else:
    print("  NONE FOUND")
