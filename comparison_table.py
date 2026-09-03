import pandas as pd

# Set A (Behavior-Only) results
set_a_data = {
    'Botnet': {'F1': 0.0682, 'F1_std': 0.2261, 'Prec': 0.0909, 'Prec_std': 0.3015, 'Rec': 0.0545, 'Rec_std': 0.1809},
    'DDOS-LOIC-UDP': {'F1': 0.0123, 'F1_std': 0.0524, 'Prec': 0.0278, 'Prec_std': 0.1179, 'Rec': 0.0079, 'Rec_std': 0.0337},
    'SSH-Bruteforce': {'F1': 0.0000, 'F1_std': 0.0000, 'Prec': 0.0000, 'Prec_std': 0.0000, 'Rec': 0.0000, 'Rec_std': 0.0000},
    'OVERALL': {'F1': 0.0256, 'F1_std': 0.1260, 'Prec': 0.0395, 'Prec_std': 0.1794, 'Rec': 0.0195, 'Rec_std': 0.0994}
}

# Set B (Schedule-Only) results
set_b_data = {
    'Botnet': {'F1': 0.2342, 'F1_std': 0.4084, 'Prec': 0.2121, 'Prec_std': 0.3807, 'Rec': 0.2727, 'Rec_std': 0.4671},
    'DDOS-LOIC-UDP': {'F1': 0.2130, 'F1_std': 0.3607, 'Prec': 0.1944, 'Prec_std': 0.3489, 'Rec': 0.2619, 'Rec_std': 0.4389},
    'SSH-Bruteforce': {'F1': 0.1706, 'F1_std': 0.3321, 'Prec': 0.2407, 'Prec_std': 0.4339, 'Rec': 0.2381, 'Rec_std': 0.4345},
    'OVERALL': {'F1': 0.2091, 'F1_std': 0.3595, 'Prec': 0.2105, 'Prec_std': 0.3690, 'Rec': 0.2594, 'Rec_std': 0.4341}
}

print("\n" + "=" * 100)
print("COMPARISON: BEHAVIOR-ONLY (SET A) vs. SCHEDULE-ONLY (SET B) AT H=5")
print("Evaluation on normal, unmodified chronological test set (38-fold LOEO)")
print("=" * 100)

for metric in ['F1', 'Prec', 'Rec']:
    print(f"\n{metric}:")
    print("-" * 100)
    print(f"{'Type':<20} | {'Set A (Behavior-Only)':<30} | {'Set B (Schedule-Only)':<30} | {'Diff (A - B)':<15}")
    print("-" * 100)
    
    for atk_type in ['Botnet', 'DDOS-LOIC-UDP', 'SSH-Bruteforce', 'OVERALL']:
        a_val = set_a_data[atk_type][metric]
        a_std = set_a_data[atk_type][f'{metric}_std']
        b_val = set_b_data[atk_type][metric]
        b_std = set_b_data[atk_type][f'{metric}_std']
        diff = a_val - b_val
        
        a_str = f"{a_val:.4f} +/- {a_std:.4f}"
        b_str = f"{b_val:.4f} +/- {b_std:.4f}"
        diff_str = f"{diff:.4f}"
        
        print(f"{atk_type:<20} | {a_str:<30} | {b_str:<30} | {diff_str:<15}")

print("\n" + "=" * 100)
print("OVERALL AGGREGATE (all 38 folds)")
print("=" * 100)

comparison_rows = []
for metric, metric_col in [('F1', 'F1'), ('Precision', 'Prec'), ('Recall', 'Rec')]:
    a_val = set_a_data['OVERALL'][metric_col]
    a_std = set_a_data['OVERALL'][f'{metric_col}_std']
    b_val = set_b_data['OVERALL'][metric_col]
    b_std = set_b_data['OVERALL'][f'{metric_col}_std']
    diff = a_val - b_val
    
    comparison_rows.append({
        'Metric': metric,
        'Set A (Behavior-Only)': f"{a_val:.4f} ± {a_std:.4f}",
        'Set B (Schedule-Only)': f"{b_val:.4f} ± {b_std:.4f}",
        'Difference (A - B)': f"{diff:+.4f}"
    })

comparison_df = pd.DataFrame(comparison_rows)
print(comparison_df.to_string(index=False))

print("\n" + "=" * 100)
print("INTERPRETATION")
print("=" * 100)
print("""
Set A (Behavior-Only):
  - Verified time-free: 400 behavioral feature columns, zero time-derived columns
  - Metrics: F1=0.0256, Precision=0.0395, Recall=0.0195 (all on normal test set)
  - Performance is near zero across all attack types and metrics

Set B (Schedule-Only):
  - Baseline using only hour + source_day features
  - Metrics: F1=0.2091, Precision=0.2105, Recall=0.2594

Numerical Comparison:
  - Set A F1 is 0.1835 BELOW Set B (A: 0.0256 vs. B: 0.2091)
  - Set A Precision is 0.1710 BELOW Set B (A: 0.0395 vs. B: 0.2105)
  - Set A Recall is 0.2399 BELOW Set B (A: 0.0195 vs. B: 0.2594)

Conclusion on predictive signal:
  - Behavioral features alone do NOT exceed random/majority-class baseline
  - Schedule-only features (hour + day) outperform behavior by 7-12x in F1
  - This suggests attack onset forecasting at H=5 depends primarily on time-of-day patterns, 
    not on behavioral (traffic/flow) characteristics of pre-onset network activity
""")

print("=" * 100)
