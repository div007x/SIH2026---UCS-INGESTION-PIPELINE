import pandas as pd
import numpy as np

df = pd.read_csv('data/ucs/loeo_fold_results.csv')
print('Total rows:', len(df), '| Tasks:', df['task'].value_counts().to_dict())

# Filter to multi-episode types only (37-fold subset)
multi_types = ['SSH-Bruteforce', 'DDOS-LOIC-UDP', 'Botnet']
multi = df[df['attack_type'].isin(multi_types)].copy()

print()
print('Multi-episode subset:')
print('  Total rows:', len(multi))
for task in ['detection', 'forecasting']:
    t = multi[multi['task'] == task]
    nrows = len(t)
    breakdown = t['attack_type'].value_counts().to_dict()
    print(f'  {task}: {nrows} rows | breakdown: {breakdown}')

print()
print('=' * 80)
print('37-FOLD MULTI-EPISODE RESULTS')
print('=' * 80)

for task in ['detection', 'forecasting']:
    t = multi[multi['task'] == task]
    print(f'\n--- {task.upper()} (37 folds) ---')

    # Per-type
    for atk in multi_types:
        at = t[t['attack_type'] == atk]
        n = len(at)
        for prefix, label in [('a', 'Set A'), ('b', 'Set B')]:
            f1m = at[f'{prefix}_f1'].mean()
            f1s = at[f'{prefix}_f1'].std()
            pm = at[f'{prefix}_prec'].mean()
            ps = at[f'{prefix}_prec'].std()
            rm = at[f'{prefix}_rec'].mean()
            rs = at[f'{prefix}_rec'].std()
            auc_m = at[f'{prefix}_prauc'].mean()
            auc_s = at[f'{prefix}_prauc'].std()
            print(f'  {atk} ({n} folds) {label}: F1={f1m:.4f}+/-{f1s:.4f}  Prec={pm:.4f}+/-{ps:.4f}  Rec={rm:.4f}+/-{rs:.4f}  PR-AUC={auc_m:.4f}+/-{auc_s:.4f}')

        # CI overlap check per-type
        a_lo = at['a_f1'].mean() - at['a_f1'].std()
        a_hi = at['a_f1'].mean() + at['a_f1'].std()
        b_lo = at['b_f1'].mean() - at['b_f1'].std()
        b_hi = at['b_f1'].mean() + at['b_f1'].std()
        overlap = a_lo <= b_hi and b_lo <= a_hi
        if not overlap:
            if at['a_f1'].mean() > at['b_f1'].mean():
                verdict = 'PASS (A > B, non-overlapping)'
            else:
                verdict = 'FAIL (B > A, non-overlapping)'
        else:
            verdict = 'CONDITIONAL PASS (ranges overlap)'
        print(f'    CI: A[{a_lo:.4f},{a_hi:.4f}] B[{b_lo:.4f},{b_hi:.4f}] -> {verdict}')

    # Aggregate
    print(f'\n  --- AGGREGATE ({task.upper()}, 37 folds) ---')
    for prefix, label in [('a', 'Set A'), ('b', 'Set B')]:
        f1m = t[f'{prefix}_f1'].mean()
        f1s = t[f'{prefix}_f1'].std()
        pm = t[f'{prefix}_prec'].mean()
        ps = t[f'{prefix}_prec'].std()
        rm = t[f'{prefix}_rec'].mean()
        rs = t[f'{prefix}_rec'].std()
        auc_m = t[f'{prefix}_prauc'].mean()
        auc_s = t[f'{prefix}_prauc'].std()
        print(f'    {label}: F1={f1m:.4f}+/-{f1s:.4f}  Prec={pm:.4f}+/-{ps:.4f}  Rec={rm:.4f}+/-{rs:.4f}  PR-AUC={auc_m:.4f}+/-{auc_s:.4f}')

    a_f1m = t['a_f1'].mean()
    a_f1s = t['a_f1'].std()
    b_f1m = t['b_f1'].mean()
    b_f1s = t['b_f1'].std()
    a_lo = a_f1m - a_f1s
    a_hi = a_f1m + a_f1s
    b_lo = b_f1m - b_f1s
    b_hi = b_f1m + b_f1s
    overlap = a_lo <= b_hi and b_lo <= a_hi
    a_wins = (t['a_f1'] > t['b_f1']).sum()
    b_wins = (t['b_f1'] > t['a_f1']).sum()
    ties = (t['a_f1'] == t['b_f1']).sum()
    if not overlap:
        if a_f1m > b_f1m:
            verdict = 'PASS'
        else:
            verdict = 'FAIL'
    else:
        verdict = 'CONDITIONAL PASS'
    print(f'    CI: A[{a_lo:.4f},{a_hi:.4f}] B[{b_lo:.4f},{b_hi:.4f}]')
    print(f'    Head-to-head: A wins {a_wins} / B wins {b_wins} / Ties {ties}')
    print(f'    VERDICT: {verdict}')

# Save 37-fold subset CSV
multi.to_csv('data/ucs/loeo_37fold_results.csv', index=False)
print('\nSaved 37-fold subset to data/ucs/loeo_37fold_results.csv')
