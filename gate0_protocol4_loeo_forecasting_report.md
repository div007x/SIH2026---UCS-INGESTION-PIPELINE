# Gate 0 Protocol 4 (LOEO) - Forecasting Target Correction Report (Class-Weighted)

## 1. Modified Script File Diff (with Class Weighting & PR-AUC)
The script was further updated to include `class_weight='balanced'` on both classifiers, print the overall class balance of the forecasting target, and compute PR-AUC instead of relying purely on a 0.5 threshold F1.

```diff
@@ -11,6 +11,11 @@
 df = pd.read_parquet('data/ucs/ucs_windows.parquet')
 df = df.sort_values('window_start_utc').reset_index(drop=True)
 
+print("=== future_attack_label Class Balance in Full Dataset ===")
+print(df['future_attack_label'].value_counts(normalize=True))
+print(df['future_attack_label'].value_counts())
+print()
+
@@ -70,13 +75,15 @@
     X_tr_b = np.column_stack([tr_hour.values, tr_days.values])
     X_te_b = np.column_stack([te_hour.values, te_days.values])
 
-    clf_a = DecisionTreeClassifier(max_depth=4, random_state=42)
+    clf_a = DecisionTreeClassifier(max_depth=4, random_state=42, class_weight='balanced')
     clf_a.fit(X_tr_a, y_tr)
     y_pr_a = clf_a.predict(X_te_a)
+    y_prob_a = clf_a.predict_proba(X_te_a)[:, 1] if clf_a.classes_.shape[0] > 1 else np.zeros(len(y_te))
 
-    clf_b = DecisionTreeClassifier(max_depth=4, random_state=42)
+    clf_b = DecisionTreeClassifier(max_depth=4, random_state=42, class_weight='balanced')
     clf_b.fit(X_tr_b, y_tr)
     y_pr_b = clf_b.predict(X_te_b)
+    y_prob_b = clf_b.predict_proba(X_te_b)[:, 1] if clf_b.classes_.shape[0] > 1 else np.zeros(len(y_te))
```

## 2. Class Balance of `future_attack_label`
The overall target distribution is not pathologically rare; it is roughly 36% positive.
```text
=== future_attack_label Class Balance in Full Dataset ===
0    0.639904
1    0.360096
Name: proportion, dtype: float64

0    1873
1    1054
Name: count, dtype: int64
```
This indicates the F1=0 collapse was not caused by a 99/1 class imbalance, but rather by the models genuinely failing to find any feature split that separates the classes.

## 3. Fold-by-Fold Table (PR-AUC added)

### Botnet (11 folds)
```text
  Fold  0 | Ep  91 | Day 02-03-2018 | Test Original: 5 atk + 11 ben = 16 | Excl: 10 | Res Test: 6 | A: F1=0.0000 PR-AUC=0.3333 | B: F1=0.0000 PR-AUC=0.8333
  Fold  1 | Ep  93 | Day 02-03-2018 | Test Original: 10 atk + 11 ben = 21 | Excl: 14 | Res Test: 7 | A: F1=0.0000 PR-AUC=0.0000 | B: F1=0.0000 PR-AUC=0.0000
  ...
  Fold  4 | Ep 101 | Day 02-03-2018 | Test Original: 1 atk + 11 ben = 12 | Excl: 4 | Res Test: 8 | A: F1=0.0000 PR-AUC=0.1667 | B: F1=1.0000 PR-AUC=1.0000
  ...
```
*(All Set A F1 scores are 0.0000. PR-AUC stays below 0.33 in folds with positive examples, while Set B spikes to 1.0 in select tiny test sets).*

### DDOS-LOIC-UDP (18 folds)
*(All Set A F1 scores are 0.0000. PR-AUC is largely 0.0000 with a few spikes. Set B manages occasional F1s of 0.6667 and 1.0000 in folds containing a single test instance).*

### SSH-Bruteforce (9 folds)
*(All Set A F1 scores are 0.0000. PR-AUC is near zero. Set B captures occasional instances but also performs poorly).*

## 4. Per-Type Mean ± Std

| Attack Type | Folds | Set A F1 | Set A PR-AUC | Set B F1 | Set B PR-AUC |
| :--- | ---: | :--- | :--- | :--- | :--- |
| **Botnet** | 11 | 0.0000 ± 0.0000 | 0.1667 ± 0.3073 | 0.1515 ± 0.3452 | 0.2803 ± 0.4350 |
| **DDOS-LOIC-UDP** | 18 | 0.0000 ± 0.0000 | 0.1206 ± 0.2481 | 0.1667 ± 0.3284 | 0.2546 ± 0.4087 |
| **SSH-Bruteforce** | 9 | 0.0000 ± 0.0000 | 0.0778 ± 0.1247 | 0.1429 ± 0.3350 | 0.3148 ± 0.4747 |

## 5. Overall Aggregate & Verdict

| Metric | Set A (Traffic+Packet) | Set B (Schedule-Only) |
| :--- | :--- | :--- |
| **F1** | **0.0000 +/- 0.0000** | **0.1566 +/- 0.3258** |
| **PR-AUC** | **0.1238 +/- 0.2413** | **0.2763 +/- 0.4210** |
| Head-to-Head (38 folds) | **A wins 0** | B wins 8, Ties 30 |

### VERDICT: FAIL 
Even with `class_weight='balanced'`, Set A completely fails on the forecasting task (F1 = 0.0000). Set A's PR-AUC is severely depressed (0.1238), showing that the raw probabilistic scores do not separate the classes effectively.

The collapse is not an artifact of an imbalanced training set (36% positive). It indicates a genuine, honest lack of signal: the physical traffic/packet features in the H=5 pre-onset window simply do not diverge meaningfully from benign traffic. 

The two candidate explanations remain valid and require deeper probing:
(a) The H=5 window is too short; latent packet deviations aren't visible yet.
(b) The schedule signal is genuinely a stronger predictor of future onset in this dataset than any latent behavioral telemetry.
