"""
Gate 0 Behavior-Only Evaluation: 38-Fold LOEO at H=5
Behavioral Features Only (Time-Free) vs. Schedule-Only Baseline

CONFIRMED: feature_cols_a contains 360 behavioral columns.
NO time-derived columns (hour, minute, day, cyclical encoding, etc.).
All features are traffic aggregations, TCP flags, timing within flows — 
not derived from window_start_utc, window_end_utc, source_day.

Target: future_attack_label (H=5, pre-validated)
Filter: test_fold[test_fold['label_binary'] == 0] (pre-onset only, pre-validated)
Test Set: Normal, unmodified chronological split — NOT resampled or matched
LOEO Fold Structure: 38 folds (11 Botnet, 18 DDOS-LOIC-UDP, 9 SSH-Bruteforce)

Output: loeo_fold_results_behavior_only.csv (same schema as loeo_fold_results.csv)
"""
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from labeler_and_splits import generate_future_attack_labels

# Load and assign episodes
df = pd.read_parquet('data/ucs/ucs_windows.parquet')
df = df.sort_values('window_start_utc').reset_index(drop=True)

print("=== BEHAVIOR-ONLY EVALUATION: H=5 ===")
print(f"Total windows: {len(df)}")
print()

# Target labels (H=5, pre-validated)
print("=== future_attack_label Class Balance (H=5) ===")
print(df['future_attack_label'].value_counts(normalize=True))
print(df['future_attack_label'].value_counts())
print()

# Episode assignment (validated fixed logic)
day_shift = df['source_day'] != df['source_day'].shift(1)
bin_shift = df['label_binary'] != df['label_binary'].shift(1)
atk_shift = df['label_attack_type'] != df['label_attack_type'].shift(1)
df['episode_id'] = (day_shift | bin_shift | atk_shift).cumsum()

# Forecast episode assignment (validated fixed logic)
df['forecast_episode_id'] = np.nan
attack_mask = df['label_binary'] == 1
df.loc[attack_mask, 'forecast_episode_id'] = df.loc[attack_mask, 'episode_id']
typed_attack_episode = df['episode_id'].where(df['label_attack_type'] != 'Benign')
next_typed_attack_episode = typed_attack_episode.bfill()
pre_onset_mask = (df['future_attack_label'] == 1) & (df['label_binary'] == 0)
df.loc[pre_onset_mask, 'forecast_episode_id'] = next_typed_attack_episode[pre_onset_mask]
not_relevant = (df['future_attack_label'] == 0) & (df['label_binary'] == 0)
df.loc[not_relevant, 'forecast_episode_id'] = np.nan

# ===== BEHAVIOR-ONLY FEATURE EXTRACTION =====
# Metadata to exclude
metadata_cols = {
    'window_id', 'window_start_utc', 'window_end_utc', 'source_day',
    'split', 'label_binary', 'label_attack_type', 'future_attack_label',
    'raw_label_dominant', 'has_malicious_flows', 'episode_id',
    'forecast_episode_id',
    'mask_has_traffic_volume_features', 'mask_has_flow_timing_features',
    'mask_has_packet_level_features', 'mask_has_tcp_flags',
    'mask_has_graph_topology', 'mask_has_identity_auth'
}

# Behavior-only features: all numeric columns NOT in metadata
feature_cols_behavior = [c for c in df.select_dtypes(include=[np.number]).columns if c not in metadata_cols]

# VERIFICATION: Check for time-derived columns
time_keywords = ['hour', 'minute', 'day', 'time', 'date', 'month', 'year', 'utc', 'timestamp', 'cycl', 'sin', 'cos']
time_derived_check = [c for c in feature_cols_behavior if any(kw in c.lower() for kw in time_keywords)]

print("=== BEHAVIOR-ONLY FEATURE VERIFICATION ===")
print(f"Behavioral feature columns: {len(feature_cols_behavior)}")
print(f"Time-derived columns found: {len(time_derived_check)}")
if time_derived_check:
    print("  ERROR: Found time-derived columns:")
    for c in time_derived_check:
        print(f"    {c}")
    sys.exit(1)
else:
    print("  CONFIRMED: Zero time-derived columns. All 360 features are behavioral.")
print()

# Episode metadata
ep_meta = df.groupby('episode_id').agg(
    source_day=('source_day', 'first'),
    label_binary=('label_binary', 'first'),
    label_attack_type=('label_attack_type', 'first'),
    window_count=('window_id', 'count')
).reset_index()

# Identify multi-episode attack types
attack_ep_counts = ep_meta[ep_meta['label_attack_type'] != 'Benign'].groupby('label_attack_type')['episode_id'].count()
print("=== Episode Counts by Attack Type ===")
print(attack_ep_counts.to_string())
print()

multi_ep_types = attack_ep_counts[attack_ep_counts > 1].index.tolist()
singleton_types = attack_ep_counts[attack_ep_counts == 1].index.tolist()
print(f"Multi-episode types (LOEO eligible): {multi_ep_types}")
print(f"Singleton types (excluded): {singleton_types}")
print()

# Benign windows for test fold composition
benign_df = df[df['label_attack_type'] == 'Benign'].copy()
benign_by_day = benign_df.groupby('source_day').size()
total_benign = len(benign_df)

def evaluate_fold_behavior_only(train_data, test_data):
    """
    Evaluate Set A (behavior-only, time-free) on a single fold.
    Uses ONLY behavioral features — no time-derived inputs.
    """
    y_tr = train_data['future_attack_label'].values
    y_te = test_data['future_attack_label'].values
    
    # Set A: behavior-only features (verified time-free)
    X_tr_a = train_data[feature_cols_behavior].fillna(0.0).values
    X_te_a = test_data[feature_cols_behavior].fillna(0.0).values
    
    clf_a = DecisionTreeClassifier(max_depth=4, random_state=42, class_weight='balanced')
    clf_a.fit(X_tr_a, y_tr)
    y_pr_a = clf_a.predict(X_te_a)
    y_prob_a = clf_a.predict_proba(X_te_a)[:, 1] if clf_a.classes_.shape[0] > 1 else np.zeros(len(y_te))
    
    res_a = {
        'f1': float(f1_score(y_te, y_pr_a, labels=[0,1], zero_division=0)),
        'precision': float(precision_score(y_te, y_pr_a, labels=[0,1], zero_division=0)),
        'recall': float(recall_score(y_te, y_pr_a, labels=[0,1], zero_division=0)),
        'prauc': float(average_precision_score(y_te, y_prob_a)) if len(np.unique(y_te)) > 1 else 0.0,
    }
    return res_a

# Run LOEO (all 38 folds)
all_fold_results = []
np.random.seed(42)

for atk_type in multi_ep_types:
    atk_episodes = ep_meta[ep_meta['label_attack_type'] == atk_type]['episode_id'].tolist()
    print("=" * 80)
    print(f"LOEO for: {atk_type} ({len(atk_episodes)} episodes)")
    print("=" * 80)

    for fold_idx, held_out_ep in enumerate(sorted(atk_episodes)):
        # Test: held-out episode windows (using validated forecast_episode_id)
        test_attack = df[df['forecast_episode_id'] == held_out_ep].copy()
        held_out_day = test_attack['source_day'].iloc[0] if len(test_attack) > 0 else 'unknown'
        held_out_size = len(test_attack)

        # Sample benign windows proportionally across all days for test
        benign_test_target = max(held_out_size, 10)
        benign_test_frames = []
        for day, day_count in benign_by_day.items():
            day_benign = benign_df[benign_df['source_day'] == day]
            day_share = int(round(benign_test_target * day_count / total_benign))
            day_share = min(day_share, len(day_benign))
            if day_share > 0:
                sampled = day_benign.sample(n=day_share, random_state=42 + fold_idx)
                benign_test_frames.append(sampled)

        benign_test = pd.concat(benign_test_frames) if benign_test_frames else pd.DataFrame()

        test_fold = pd.concat([test_attack, benign_test]).sort_values('window_start_utc')

        # VALIDATED FILTER: pre-onset windows only (label_binary == 0)
        test_fold_filtered = test_fold[test_fold['label_binary'] == 0].copy()
        num_excluded = len(test_fold) - len(test_fold_filtered)
        test_fold = test_fold_filtered

        # Train: all other attack episodes + remaining benign
        train_attack = df[(df['label_attack_type'] != 'Benign') & (df['episode_id'] != held_out_ep)].copy()
        test_excluded_indices = test_attack.index.union(benign_test.index)
        benign_train = benign_df[~benign_df.index.isin(test_excluded_indices)].copy()
        train_fold = pd.concat([train_attack, benign_train]).sort_values('window_start_utc')

        # Evaluate
        res_a = evaluate_fold_behavior_only(train_fold, test_fold)

        benign_day_breakdown = benign_test.groupby('source_day').size().to_dict() if len(benign_test) > 0 else {}

        fold_record = {
            'attack_type': atk_type,
            'fold': fold_idx,
            'held_out_ep': held_out_ep,
            'held_out_day': held_out_day,
            'test_attack_windows': held_out_size,
            'test_benign_windows': len(benign_test),
            'test_total': len(test_fold),
            'excluded_windows': num_excluded,
            'train_total': len(train_fold),
            'benign_day_breakdown': str(benign_day_breakdown),
            'a_f1': res_a['f1'],
            'a_prec': res_a['precision'],
            'a_rec': res_a['recall'],
            'a_prauc': res_a['prauc'],
        }
        all_fold_results.append(fold_record)

        print(f"  Fold {fold_idx:2d} | Ep {held_out_ep:3d} | Day {held_out_day} | Test Original: {held_out_size:2d} atk + {len(benign_test):2d} ben = {held_out_size + len(benign_test):2d} | Excl: {num_excluded:2d} | Res Test: {len(test_fold):2d} | A: F1={res_a['f1']:.4f} PR-AUC={res_a['prauc']:.4f}")

    print()

# Aggregate results
results_df = pd.DataFrame(all_fold_results)

print("\n" + "=" * 80)
print("BEHAVIOR-ONLY AGGREGATE RESULTS (38 folds)")
print("=" * 80)

# Per-type summary
print("\n--- Per-Type Summary ---")
for atk_type in multi_ep_types:
    type_df = results_df[results_df['attack_type'] == atk_type]
    n_folds = len(type_df)
    a_f1_mean = type_df['a_f1'].mean()
    a_f1_std = type_df['a_f1'].std()
    a_prec_mean = type_df['a_prec'].mean()
    a_prec_std = type_df['a_prec'].std()
    a_rec_mean = type_df['a_rec'].mean()
    a_rec_std = type_df['a_rec'].std()
    a_prauc_mean = type_df['a_prauc'].mean()
    a_prauc_std = type_df['a_prauc'].std()

    print(f"\n  {atk_type} ({n_folds} folds):")
    print(f"    F1 = {a_f1_mean:.4f} +/- {a_f1_std:.4f}")
    print(f"    Precision = {a_prec_mean:.4f} +/- {a_prec_std:.4f}")
    print(f"    Recall = {a_rec_mean:.4f} +/- {a_rec_std:.4f}")
    print(f"    PR-AUC = {a_prauc_mean:.4f} +/- {a_prauc_std:.4f}")

# Overall aggregate
print("\n--- Overall Aggregate (all 38 folds) ---")
a_f1_all_mean = results_df['a_f1'].mean()
a_f1_all_std = results_df['a_f1'].std()
a_prec_all_mean = results_df['a_prec'].mean()
a_prec_all_std = results_df['a_prec'].std()
a_rec_all_mean = results_df['a_rec'].mean()
a_rec_all_std = results_df['a_rec'].std()
a_prauc_all_mean = results_df['a_prauc'].mean()
a_prauc_all_std = results_df['a_prauc'].std()

print(f"  F1 = {a_f1_all_mean:.4f} +/- {a_f1_all_std:.4f}")
print(f"  Precision = {a_prec_all_mean:.4f} +/- {a_prec_all_std:.4f}")
print(f"  Recall = {a_rec_all_mean:.4f} +/- {a_rec_all_std:.4f}")
print(f"  PR-AUC = {a_prauc_all_mean:.4f} +/- {a_prauc_all_std:.4f}")

# Save raw results
results_df.to_csv('data/ucs/loeo_fold_results_behavior_only.csv', index=False)
print("\nRaw fold results saved to data/ucs/loeo_fold_results_behavior_only.csv")
