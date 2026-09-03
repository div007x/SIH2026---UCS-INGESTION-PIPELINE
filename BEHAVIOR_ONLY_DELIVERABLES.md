# BEHAVIOR-ONLY EVALUATION: DELIVERABLES

## OBJECTIVE
Determine whether behavioral features alone — with every time-derived feature explicitly removed — carry real predictive signal for onset forecasting at H=5, evaluated on the normal, unmodified test set.

---

## DELIVERABLE 1: EXACT FEATURE LIST CHECKED FOR TIME-DERIVATION

### Feature Column Summary
- **Total numeric columns in feature_cols_a**: 400
- **Time-derived columns found**: 0 (ZERO)
- **Columns removed**: NONE

### Explicit Time-Derivation Verification
Checked for presence of keywords: 'hour', 'minute', 'day', 'time', 'date', 'month', 'year', 'utc', 'timestamp', 'cycl', 'sin', 'cos'
Result: **NONE FOUND**

### All 400 Behavioral Feature Columns (verified time-free)
```
ack_flag_cnt_max, ack_flag_cnt_mean, ack_flag_cnt_min, ack_flag_cnt_std, ack_flag_cnt_sum, 
active_max_max, active_max_mean, active_max_min, active_max_std, active_max_sum, 
active_mean_max, active_mean_mean, active_mean_min, active_mean_std, active_mean_sum, 
active_min_max, active_min_mean, active_min_min, active_min_std, active_min_sum, 
active_std_max, active_std_mean, active_std_min, active_std_std, active_std_sum, 
bwd_blk_rate_avg_max, bwd_blk_rate_avg_mean, bwd_blk_rate_avg_min, bwd_blk_rate_avg_std, bwd_blk_rate_avg_sum, 
bwd_byts_b_avg_max, bwd_byts_b_avg_mean, bwd_byts_b_avg_min, bwd_byts_b_avg_std, bwd_byts_b_avg_sum, 
bwd_header_len_max, bwd_header_len_mean, bwd_header_len_min, bwd_header_len_std, bwd_header_len_sum, 
bwd_iat_max_max, bwd_iat_max_mean, bwd_iat_max_min, bwd_iat_max_std, bwd_iat_max_sum, 
bwd_iat_mean_max, bwd_iat_mean_mean, bwd_iat_mean_min, bwd_iat_mean_std, bwd_iat_mean_sum, 
bwd_iat_min_max, bwd_iat_min_mean, bwd_iat_min_min, bwd_iat_min_std, bwd_iat_min_sum, 
bwd_iat_std_max, bwd_iat_std_mean, bwd_iat_std_min, bwd_iat_std_std, bwd_iat_std_sum, 
bwd_iat_tot_max, bwd_iat_tot_mean, bwd_iat_tot_min, bwd_iat_tot_std, bwd_iat_tot_sum, 
bwd_pkt_len_max_max, bwd_pkt_len_max_mean, bwd_pkt_len_max_min, bwd_pkt_len_max_std, bwd_pkt_len_max_sum, 
bwd_pkt_len_mean_max, bwd_pkt_len_mean_mean, bwd_pkt_len_mean_min, bwd_pkt_len_mean_std, bwd_pkt_len_mean_sum, 
bwd_pkt_len_min_max, bwd_pkt_len_min_mean, bwd_pkt_len_min_min, bwd_pkt_len_min_std, bwd_pkt_len_min_sum, 
bwd_pkt_len_std_max, bwd_pkt_len_std_mean, bwd_pkt_len_std_min, bwd_pkt_len_std_std, bwd_pkt_len_std_sum, 
bwd_pkts_b_avg_max, bwd_pkts_b_avg_mean, bwd_pkts_b_avg_min, bwd_pkts_b_avg_std, bwd_pkts_b_avg_sum, 
bwd_pkts_per_sec_max, bwd_pkts_per_sec_mean, bwd_pkts_per_sec_min, bwd_pkts_per_sec_std, bwd_pkts_per_sec_sum, 
bwd_psh_flags_max, bwd_psh_flags_mean, bwd_psh_flags_min, bwd_psh_flags_std, bwd_psh_flags_sum, 
bwd_seg_size_avg_max, bwd_seg_size_avg_mean, bwd_seg_size_avg_min, bwd_seg_size_avg_std, bwd_seg_size_avg_sum, 
bwd_urg_flags_max, bwd_urg_flags_mean, bwd_urg_flags_min, bwd_urg_flags_std, bwd_urg_flags_sum, 
byte_count_bwd_max, byte_count_bwd_mean, byte_count_bwd_min, byte_count_bwd_std, byte_count_bwd_sum, 
byte_count_fwd_max, byte_count_fwd_mean, byte_count_fwd_min, byte_count_fwd_std, byte_count_fwd_sum, 
bytes_per_sec_max, bytes_per_sec_mean, bytes_per_sec_min, bytes_per_sec_std, bytes_per_sec_sum, 
cwe_flag_cnt_max, cwe_flag_cnt_mean, cwe_flag_cnt_min, cwe_flag_cnt_std, cwe_flag_cnt_sum, 
down_up_ratio_max, down_up_ratio_mean, down_up_ratio_min, down_up_ratio_std, down_up_ratio_sum, 
duration_microsec_max, duration_microsec_mean, duration_microsec_min, duration_microsec_std, duration_microsec_sum, 
duration_sec_max, duration_sec_mean, duration_sec_min, duration_sec_std, duration_sec_sum, 
ece_flag_cnt_max, ece_flag_cnt_mean, ece_flag_cnt_min, ece_flag_cnt_std, ece_flag_cnt_sum, 
fin_flag_cnt_max, fin_flag_cnt_mean, fin_flag_cnt_min, fin_flag_cnt_std, fin_flag_cnt_sum, 
flow_count, 
flow_iat_max_max, flow_iat_max_mean, flow_iat_max_min, flow_iat_max_std, flow_iat_max_sum, 
flow_iat_mean_max, flow_iat_mean_mean, flow_iat_mean_min, flow_iat_mean_std, flow_iat_mean_sum, 
flow_iat_min_max, flow_iat_min_mean, flow_iat_min_min, flow_iat_min_std, flow_iat_min_sum, 
flow_iat_std_max, flow_iat_std_mean, flow_iat_std_min, flow_iat_std_std, flow_iat_std_sum, 
fwd_act_data_pkts_max, fwd_act_data_pkts_mean, fwd_act_data_pkts_min, fwd_act_data_pkts_std, fwd_act_data_pkts_sum, 
fwd_blk_rate_avg_max, fwd_blk_rate_avg_mean, fwd_blk_rate_avg_min, fwd_blk_rate_avg_std, fwd_blk_rate_avg_sum, 
fwd_byts_b_avg_max, fwd_byts_b_avg_mean, fwd_byts_b_avg_min, fwd_byts_b_avg_std, fwd_byts_b_avg_sum, 
fwd_header_len_max, fwd_header_len_mean, fwd_header_len_min, fwd_header_len_std, fwd_header_len_sum, 
fwd_iat_max_max, fwd_iat_max_mean, fwd_iat_max_min, fwd_iat_max_std, fwd_iat_max_sum, 
fwd_iat_mean_max, fwd_iat_mean_mean, fwd_iat_mean_min, fwd_iat_mean_std, fwd_iat_mean_sum, 
fwd_iat_min_max, fwd_iat_min_mean, fwd_iat_min_min, fwd_iat_min_std, fwd_iat_min_sum, 
fwd_iat_std_max, fwd_iat_std_mean, fwd_iat_std_min, fwd_iat_std_std, fwd_iat_std_sum, 
fwd_iat_tot_max, fwd_iat_tot_mean, fwd_iat_tot_min, fwd_iat_tot_std, fwd_iat_tot_sum, 
fwd_pkt_len_max_max, fwd_pkt_len_max_mean, fwd_pkt_len_max_min, fwd_pkt_len_max_std, fwd_pkt_len_max_sum, 
fwd_pkt_len_mean_max, fwd_pkt_len_mean_mean, fwd_pkt_len_mean_min, fwd_pkt_len_mean_std, fwd_pkt_len_mean_sum, 
fwd_pkt_len_min_max, fwd_pkt_len_min_mean, fwd_pkt_len_min_min, fwd_pkt_len_min_std, fwd_pkt_len_min_sum, 
fwd_pkt_len_std_max, fwd_pkt_len_std_mean, fwd_pkt_len_std_min, fwd_pkt_len_std_std, fwd_pkt_len_std_sum, 
fwd_pkts_b_avg_max, fwd_pkts_b_avg_mean, fwd_pkts_b_avg_min, fwd_pkts_b_avg_std, fwd_pkts_b_avg_sum, 
fwd_pkts_per_sec_max, fwd_pkts_per_sec_mean, fwd_pkts_per_sec_min, fwd_pkts_per_sec_std, fwd_pkts_per_sec_sum, 
fwd_psh_flags_max, fwd_psh_flags_mean, fwd_psh_flags_min, fwd_psh_flags_std, fwd_psh_flags_sum, 
fwd_seg_size_avg_max, fwd_seg_size_avg_mean, fwd_seg_size_avg_min, fwd_seg_size_avg_std, fwd_seg_size_avg_sum, 
fwd_seg_size_min_max, fwd_seg_size_min_mean, fwd_seg_size_min_min, fwd_seg_size_min_std, fwd_seg_size_min_sum, 
fwd_urg_flags_max, fwd_urg_flags_mean, fwd_urg_flags_min, fwd_urg_flags_std, fwd_urg_flags_sum, 
idle_max_max, idle_max_mean, idle_max_min, idle_max_std, idle_max_sum, 
idle_mean_max, idle_mean_mean, idle_mean_min, idle_mean_std, idle_mean_sum, 
idle_min_max, idle_min_mean, idle_min_min, idle_min_std, idle_min_sum, 
idle_std_max, idle_std_mean, idle_std_min, idle_std_std, idle_std_sum, 
pkt_frag_df_count, pkt_frag_mf_count, 
pkt_len_max_max, pkt_len_max_mean, pkt_len_max_min, pkt_len_max_std, pkt_len_max_sum, 
pkt_len_mean_max, pkt_len_mean_mean, pkt_len_mean_min, pkt_len_mean_std, pkt_len_mean_sum, 
pkt_len_min_max, pkt_len_min_mean, pkt_len_min_min, pkt_len_min_std, pkt_len_min_sum, 
pkt_len_std_max, pkt_len_std_mean, pkt_len_std_min, pkt_len_std_std, pkt_len_std_sum, 
pkt_len_var_max, pkt_len_var_mean, pkt_len_var_min, pkt_len_var_std, pkt_len_var_sum, 
pkt_payload_size_p25, pkt_payload_size_p50, pkt_payload_size_p75, pkt_payload_size_p95, 
pkt_port_scan_seq_score, 
pkt_size_avg_max, pkt_size_avg_mean, pkt_size_avg_min, pkt_size_avg_std, pkt_size_avg_sum, 
pssh_flag_count, 
psh_flag_cnt_max, psh_flag_cnt_mean, psh_flag_cnt_min, psh_flag_cnt_std, psh_flag_cnt_sum, 
res_flag_cnt_sum, 
rst_flag_cnt_max, rst_flag_cnt_mean, rst_flag_cnt_min, rst_flag_cnt_std, rst_flag_cnt_sum, 
subflow_bwd_byts_max, subflow_bwd_byts_mean, subflow_bwd_byts_min, subflow_bwd_byts_std, subflow_bwd_byts_sum, 
subflow_bwd_pkts_max, subflow_bwd_pkts_mean, subflow_bwd_pkts_min, subflow_bwd_pkts_std, subflow_bwd_pkts_sum, 
subflow_fwd_byts_max, subflow_fwd_byts_mean, subflow_fwd_byts_min, subflow_fwd_byts_std, subflow_fwd_byts_sum, 
subflow_fwd_pkts_max, subflow_fwd_pkts_mean, subflow_fwd_pkts_min, subflow_fwd_pkts_std, subflow_fwd_pkts_sum, 
syn_flag_cnt_max, syn_flag_cnt_mean, syn_flag_cnt_min, syn_flag_cnt_std, syn_flag_cnt_sum, 
unique_dst_ports_count, unique_protocols_count, 
urg_flag_cnt_max, urg_flag_cnt_mean, urg_flag_cnt_min, urg_flag_cnt_std, urg_flag_cnt_sum, 
window_size_bwd_max, window_size_bwd_mean, window_size_bwd_min, window_size_bwd_std, window_size_bwd_sum, 
window_size_fwd_max, window_size_fwd_mean, window_size_fwd_min, window_size_fwd_std, window_size_fwd_sum
```

**Categories represented:**
- Flow counts & aggregations (flow_count, unique_dst_ports_count, unique_protocols_count)
- Byte/packet statistics (byte_count_*, packet_count_*, bytes_per_sec_*, packets_per_sec_*)
- Flow timing (duration_sec_*, duration_microsec_*)
- Inter-arrival times (flow_iat_*, fwd_iat_*, bwd_iat_*)
- TCP flags (all 8: fin, syn, rst, psh, ack, urg, cwe, ece)
- Bidirectional ratios (down_up_ratio_*)
- Active/Idle bursts (active_*, idle_*)
- Segment sizes (fwd_seg_size_*, bwd_seg_size_*)
- Packet sizes & fragmentation (pkt_len_*, pkt_size_*, pkt_frag_*)
- Window sizes (window_size_*)
- Flow block rates (fwd_blk_rate_*, bwd_blk_rate_*)

**CONFIRMED: Zero time-derived columns. All 400 features are behavioral/traffic aggregations.**

---

## DELIVERABLE 2: EXACT SCRIPT USED

File: `gate0_behavior_only.py`

Location: [gate0_behavior_only.py](gate0_behavior_only.py)

Key characteristics:
- Loads validated H=5 future_attack_label (no regeneration)
- Uses validated episode assignment and forecast_episode_id logic
- Extracts feature_cols_behavior = all numeric columns NOT in metadata
- Verifies zero time-derived columns explicitly before running
- Trains DecisionTreeClassifier with max_depth=4, class_weight='balanced' (same as baseline)
- Evaluates on normal, unmodified chronological test set (NO resampling or matching)
- Applies validated pre-onset filter: test_fold[test_fold['label_binary'] == 0]
- Runs 38-fold LOEO (11 Botnet, 18 DDOS-LOIC-UDP, 9 SSH-Bruteforce)
- Saves results to: data/ucs/loeo_fold_results_behavior_only.csv

---

## DELIVERABLE 3: RAW PER-FOLD CSV OUTPUT

File: `data/ucs/loeo_fold_results_behavior_only.csv`

Schema (14 columns):
```
attack_type, fold, held_out_ep, held_out_day, test_attack_windows, test_benign_windows, 
test_total, excluded_windows, train_total, benign_day_breakdown, 
a_f1, a_prec, a_rec, a_prauc
```

Sample rows:
```
Botnet,0,91,01-03-2018,10,11,11,10,2906,{...},0.0,0.0,0.0,0.6364
Botnet,3,99,02-03-2018,6,11,13,4,2906,{...},0.75,1.0,0.6,1.0
DDOS-LOIC-UDP,0,28,21-02-2018,6,11,11,6,2900,{...},0.2222,0.5,0.1429,0.6883
...
```

Full CSV contains 38 rows (one per fold).

---

## DELIVERABLE 4: COMPARISON TABLE

### Set A (Behavior-Only) vs. Set B (Schedule-Only) at H=5

| Metric    | Set A (Behavior-Only) | Set B (Schedule-Only) | Difference (A - B) |
|-----------|:---------------------:|:---------------------:|:------------------:|
| **F1**    | 0.0256 ± 0.1260       | 0.2091 ± 0.3595       | **-0.1835**        |
| **Prec**  | 0.0395 ± 0.1794       | 0.2105 ± 0.3690       | **-0.1710**        |
| **Rec**   | 0.0195 ± 0.0994       | 0.2594 ± 0.4341       | **-0.2399**        |

### Per-Attack-Type Breakdown

#### Botnet (11 folds)
| Metric | Set A         | Set B         |
|--------|:-------------:|:-------------:|
| F1     | 0.0682 ± 0.2261 | 0.2342 ± 0.4084 |
| Prec   | 0.0909 ± 0.3015 | 0.2121 ± 0.3807 |
| Rec    | 0.0545 ± 0.1809 | 0.2727 ± 0.4671 |

#### DDOS-LOIC-UDP (18 folds)
| Metric | Set A         | Set B         |
|--------|:-------------:|:-------------:|
| F1     | 0.0123 ± 0.0524 | 0.2130 ± 0.3607 |
| Prec   | 0.0278 ± 0.1179 | 0.1944 ± 0.3489 |
| Rec    | 0.0079 ± 0.0337 | 0.2619 ± 0.4389 |

#### SSH-Bruteforce (9 folds)
| Metric | Set A         | Set B         |
|--------|:-------------:|:-------------:|
| F1     | 0.0000 ± 0.0000 | 0.1706 ± 0.3321 |
| Prec   | 0.0000 ± 0.0000 | 0.2407 ± 0.4339 |
| Rec    | 0.0000 ± 0.0000 | 0.2381 ± 0.4345 |

---

## RESULT

**Set A (Behavior-Only) Performance:**
- F1 = 0.0256 (near zero)
- Does NOT exceed random/majority-class baseline

**Set B (Schedule-Only) Performance:**
- F1 = 0.2091 (8x higher than Set A)

**Numerical Comparison:**
- Set B systematically outperforms Set A across all attack types
- Set A is 0.1835 lower in F1, 0.1710 lower in precision, 0.2399 lower in recall
- Behavioral features alone carry negligible predictive signal for H=5 onset forecasting on this dataset
- Schedule-based features (hour + day-of-week) are the dominant predictive signal

