import pandas as pd

# Read the behavior-only results CSV
df = pd.read_csv('data/ucs/loeo_fold_results_behavior_only.csv')

print("=" * 100)
print("BEHAVIOR-ONLY FOLD RESULTS: loeo_fold_results_behavior_only.csv")
print("=" * 100)
print(f"\nShape: {df.shape[0]} rows (folds) × {df.shape[1]} columns")
print(f"\nColumns: {df.columns.tolist()}")

print("\n" + "=" * 100)
print("SAMPLE OUTPUT (all rows with key metrics)")
print("=" * 100)
print(df[['attack_type', 'fold', 'held_out_ep', 'held_out_day', 'test_total', 'excluded_windows', 'a_f1', 'a_prec', 'a_rec', 'a_prauc']].to_string(index=False))

print("\n" + "=" * 100)
print("PER-FOLD AGGREGATE STATISTICS")
print("=" * 100)
print(f"Total folds: {len(df)}")
print(f"\nF1 statistics:")
print(f"  Mean: {df['a_f1'].mean():.4f}")
print(f"  Std:  {df['a_f1'].std():.4f}")
print(f"  Min:  {df['a_f1'].min():.4f}")
print(f"  Max:  {df['a_f1'].max():.4f}")

print(f"\nPrecision statistics:")
print(f"  Mean: {df['a_prec'].mean():.4f}")
print(f"  Std:  {df['a_prec'].std():.4f}")

print(f"\nRecall statistics:")
print(f"  Mean: {df['a_rec'].mean():.4f}")
print(f"  Std:  {df['a_rec'].std():.4f}")

print(f"\nPR-AUC statistics:")
print(f"  Mean: {df['a_prauc'].mean():.4f}")
print(f"  Std:  {df['a_prauc'].std():.4f}")
