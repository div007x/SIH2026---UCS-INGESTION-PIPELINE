import os
import sys
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score

df = pd.read_parquet('data/ucs/ucs_windows.parquet')
df = df.sort_values('window_start_utc').reset_index(drop=True)

# Generate episode_id
df['run_group'] = ((df['source_day'] != df['source_day'].shift(1)) | (df['label_attack_type'] != df['label_attack_type'].shift(1))).cumsum()
run_meta = df.groupby('run_group').agg(
    source_day=('source_day', 'first'),
    label_attack_type=('label_attack_type', 'first'),
    start_time=('window_start_utc', 'first')
).reset_index()
run_meta['run_index'] = run_meta.groupby(['source_day', 'label_attack_type']).cumcount()
run_meta['episode_id'] = run_meta['source_day'] + '_' + run_meta['label_attack_type'] + '_' + run_meta['run_index'].astype(str)
run_to_ep = dict(zip(run_meta['run_group'], run_meta['episode_id']))
df['episode_id'] = df['run_group'].map(run_to_ep)

# forecast_episode_id
df['forecast_episode_id'] = np.nan
attack_mask = df['label_binary'] == 1
df.loc[attack_mask, 'forecast_episode_id'] = df.loc[attack_mask, 'episode_id']
typed_attack_episode = df['episode_id'].where(df['label_attack_type'] != 'Benign')
next_typed_attack_episode = typed_attack_episode.bfill()
pre_onset_mask = (df['future_attack_label'] == 1) & (df['label_binary'] == 0)
df.loc[pre_onset_mask, 'forecast_episode_id'] = next_typed_attack_episode[pre_onset_mask]
not_relevant = (df['future_attack_label'] == 0) & (df['label_binary'] == 0)
df.loc[not_relevant, 'forecast_episode_id'] = np.nan

# Feature cols
metadata_cols = {
    'window_id', 'window_start_utc', 'window_end_utc', 'source_day',
    'split', 'label_binary', 'label_attack_type', 'future_attack_label',
    'raw_label_dominant', 'has_malicious_flows', 'episode_id',
    'forecast_episode_id', 'run_group',
    'mask_has_traffic_volume_features', 'mask_has_flow_timing_features',
    'mask_has_packet_level_features', 'mask_has_tcp_flags',
    'mask_has_graph_topology', 'mask_has_identity_auth'
}
feature_cols_a = [c for c in df.select_dtypes(include=[np.number]).columns if c not in metadata_cols]

ep_meta = df.groupby('episode_id').agg(
    source_day=('source_day', 'first'),
    label_binary=('label_binary', 'first'),
    label_attack_type=('label_attack_type', 'first'),
    window_count=('window_id', 'count'),
    start_utc=('window_start_utc', 'first')
).reset_index().sort_values('start_utc').reset_index(drop=True)

attack_ep_meta = ep_meta[ep_meta['label_attack_type'] != 'Benign'].copy()
print("Attack episode counts by type:")
print(attack_ep_meta['label_attack_type'].value_counts())
print(f"Total attack episodes: {len(attack_ep_meta)}")

multi_ep_types = attack_ep_meta['label_attack_type'].value_counts()[lambda x: x > 1].index.tolist()
print("Multi-episode types (sum={}): {}".format(
    attack_ep_meta[attack_ep_meta['label_attack_type'].isin(multi_ep_types)].shape[0],
    multi_ep_types
))

