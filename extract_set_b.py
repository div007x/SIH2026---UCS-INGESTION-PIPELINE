import pandas as pd

# Read the existing LOEO results (which includes both Set A and Set B from the validated run)
df = pd.read_csv('data/ucs/loeo_fold_results.csv')

# Display column names
print("Columns in loeo_fold_results.csv:")
print(df.columns.tolist())
print()

# Show first few rows
print("First 3 rows:")
print(df.head(3).to_string())
print()

# Extract Set B results and compute aggregates
print("=" * 80)
print("SET B (SCHEDULE-ONLY) BASELINE AT H=5")
print("=" * 80)

for atk_type in ['Botnet', 'DDOS-LOIC-UDP', 'SSH-Bruteforce']:
    type_df = df[df['attack_type'] == atk_type]
    n = len(type_df)
    b_f1 = type_df['b_f1'].mean()
    b_f1_std = type_df['b_f1'].std()
    b_prec = type_df['b_prec'].mean()
    b_prec_std = type_df['b_prec'].std()
    b_rec = type_df['b_rec'].mean()
    b_rec_std = type_df['b_rec'].std()
    b_prauc = type_df['b_prauc'].mean()
    b_prauc_std = type_df['b_prauc'].std()
    
    print(f"\n{atk_type} ({n} folds):")
    print(f"  F1       = {b_f1:.4f} +/- {b_f1_std:.4f}")
    print(f"  Precision = {b_prec:.4f} +/- {b_prec_std:.4f}")
    print(f"  Recall   = {b_rec:.4f} +/- {b_rec_std:.4f}")
    print(f"  PR-AUC   = {b_prauc:.4f} +/- {b_prauc_std:.4f}")

print("\nOVERALL (all 38 folds):")
b_f1_all = df['b_f1'].mean()
b_f1_all_std = df['b_f1'].std()
b_prec_all = df['b_prec'].mean()
b_prec_all_std = df['b_prec'].std()
b_rec_all = df['b_rec'].mean()
b_rec_all_std = df['b_rec'].std()
b_prauc_all = df['b_prauc'].mean()
b_prauc_all_std = df['b_prauc'].std()

print(f"  F1       = {b_f1_all:.4f} +/- {b_f1_all_std:.4f}")
print(f"  Precision = {b_prec_all:.4f} +/- {b_prec_all_std:.4f}")
print(f"  Recall   = {b_rec_all:.4f} +/- {b_rec_all_std:.4f}")
print(f"  PR-AUC   = {b_prauc_all:.4f} +/- {b_prauc_all_std:.4f}")
