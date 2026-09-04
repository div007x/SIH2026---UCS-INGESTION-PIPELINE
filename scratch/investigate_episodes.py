import os
import sys
import pandas as pd
import numpy as np

df = pd.read_parquet('data/ucs/ucs_windows.parquet')
df = df.sort_values('window_start_utc').reset_index(drop=True)

new_run = (df['source_day'] != df['source_day'].shift(1)) | (df['label_attack_type'] != df['label_attack_type'].shift(1))
df['run_id'] = new_run.cumsum()

ep_rows = []
for r, g in df.groupby('run_id'):
    ep_rows.append({
        'run_id': r,
        'source_day': g['source_day'].iloc[0],
        'attack_type': g['label_attack_type'].iloc[0],
        'start_utc': g['window_start_utc'].iloc[0],
        'end_utc': g['window_start_utc'].iloc[-1],
        'len_windows': len(g)
    })
ep_df = pd.DataFrame(ep_rows)
attack_runs = ep_df[ep_df['attack_type'] != 'Benign'].copy()

print("=================================================================")
print("HYPOTHESIS 1: GAP LENGTHS BETWEEN ADJACENT RUNS OF SAME ATTACK TYPE")
print("=================================================================")
for (day, atk), grp in attack_runs.groupby(['source_day', 'attack_type']):
    grp = grp.sort_values('start_utc').reset_index(drop=True)
    if len(grp) > 1:
        print(f"\nDay: {day} | Attack: {atk} | Total Runs: {len(grp)}")
        for i in range(len(grp) - 1):
            gap_min = (grp.loc[i+1, 'start_utc'] - grp.loc[i, 'end_utc']).total_seconds() / 60.0 - 1
            print(f"  Run {i} ({grp.loc[i, 'len_windows']} windows, {grp.loc[i, 'start_utc']} to {grp.loc[i, 'end_utc']}) "
                  f"-> Run {i+1} ({grp.loc[i+1, 'len_windows']} windows, {grp.loc[i+1, 'start_utc']} to {grp.loc[i+1, 'end_utc']}): "
                  f"Gap = {gap_min:.0f} min")

print("\n=================================================================")
print("HYPOTHESIS 2: MINIMUM-LENGTH OR PRE-ONSET HISTORY THRESHOLDS")
print("=================================================================")
print("Episode lengths (window count) per attack type:")
print(attack_runs.groupby('attack_type')['len_windows'].describe())

print("\nPre-onset benign windows available before each episode start:")
for idx, row in attack_runs.iterrows():
    # count benign windows immediately preceding row['start_utc'] on same day
    day_df = df[df['source_day'] == row['source_day']].sort_values('window_start_utc').reset_index(drop=True)
    ep_start_idx = day_df[day_df['window_start_utc'] == row['start_utc']].index[0]
    # find how many consecutive benign windows precede this
    pre_benign = 0
    k = ep_start_idx - 1
    while k >= 0 and day_df.loc[k, 'label_attack_type'] == 'Benign':
        pre_benign += 1
        k -= 1
    print(f"Episode {row['attack_type']} on {row['source_day']} at {row['start_utc']}: len={row['len_windows']}w, pre_onset_benign={pre_benign}w, total_pre_history={ep_start_idx}w")

