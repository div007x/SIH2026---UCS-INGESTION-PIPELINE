import pandas as pd
import numpy as np

# ───────────────────────────────────────────────
# TASK 2: Materialize episode_id and forecast_episode_id
# using verbatim logic from labeler_and_splits.py assign_episode_ids()
# and run_loeo_corrected.py forecast_episode_id bfill block
# ───────────────────────────────────────────────
df = pd.read_parquet('data/ucs/ucs_windows.parquet')
df = df.sort_values('window_start_utc').reset_index(drop=True)

print('Columns before materialization:')
print([c for c in df.columns if 'episode' in c.lower()])
print('Shape:', df.shape)

# ── episode_id (verbatim from labeler_and_splits.assign_episode_ids) ──
# episode_id is already materialized - confirm dtype and nulls
print()
print('episode_id dtype:', df['episode_id'].dtype)
print('episode_id nulls:', df['episode_id'].isna().sum())

# ── forecast_episode_id: verbatim from run_loeo_corrected.py lines 25-35 ──
df['forecast_episode_id'] = pd.Series(None, index=df.index, dtype='object')
attack_mask = df['label_attack_type'] != 'Benign'
df.loc[attack_mask, 'forecast_episode_id'] = df.loc[attack_mask, 'episode_id']

for day in df['source_day'].unique():
    day_idx = df[df['source_day'] == day].index
    day_eps = df.loc[day_idx, 'episode_id'].where(df.loc[day_idx, 'label_attack_type'] != 'Benign')
    next_attack_ep = day_eps.bfill()
    pre_onset_day = (df.loc[day_idx, 'future_attack_label'] == 1) & (df.loc[day_idx, 'label_binary'] == 0)
    df.loc[day_idx[pre_onset_day], 'forecast_episode_id'] = next_attack_ep[pre_onset_day]

print()
print('forecast_episode_id dtype:', df['forecast_episode_id'].dtype)
print('forecast_episode_id nulls:', df['forecast_episode_id'].isna().sum())
print('forecast_episode_id non-null sample:')
print(df[df['forecast_episode_id'].notna()][['window_start_utc','source_day','label_attack_type','episode_id','forecast_episode_id']].head(5).to_string())
print()
print('=== df.columns with episode columns ===')
print([c for c in df.columns if 'episode' in c.lower()])
print()

# Save updated parquet
df.to_parquet('data/ucs/ucs_windows.parquet', index=False)
print('Saved updated parquet with forecast_episode_id materialized.')

# Reload and verify
df2 = pd.read_parquet('data/ucs/ucs_windows.parquet')
print()
print('=== RELOAD VERIFICATION ===')
print('df.columns:', [c for c in df2.columns if 'episode' in c.lower()])
print('episode_id dtype:', df2['episode_id'].dtype, '| nulls:', df2['episode_id'].isna().sum())
print('forecast_episode_id dtype:', df2['forecast_episode_id'].dtype, '| nulls:', df2['forecast_episode_id'].isna().sum())
print()
print('=== df[episode_id, forecast_episode_id].head(20) ===')
print(df2[['episode_id','forecast_episode_id']].head(20).to_string())
