
# CSE-CIC-IDS2018 → Unified Cyber State ($S_t$) Data Pipeline
**SIH26153 — Cyber World Model Architecture (Data Engineer Track)**

This repository provides the production data engineering pipeline that processes raw CSE-CIC-IDS2018 CICFlowMeter flow CSVs into the **Unified Cyber State ($S_t$)** — a time-windowed, leakage-safe, dual-format state representation (flat temporal feature vector + graph topology edge list) designed to feed downstream LSTM/GRU and GraphSAGE world models.

---

## 🚀 Key Features

1. **Robust Ingestion**: Latin-1 fallback encoding, automated whitespace stripping, duplicate header removal (`Label == 'Label'`), and provenance tracking (`source_day`, `source_file`).
2. **Canonical 80-to-UCS Mapping**: Maps all flow-level features, timing/IAT distributions, all 8 TCP flags, subflows, bidirectional down/up ratios, and packet-level features (`Init_Win_bytes_forward`, `Init_Win_bytes_backward`, `fwd_seg_size_min`).
3. **Data Quality & Integrity**:
   - Zero infinities: Replaces division-by-zero rate infinities with safe medians.
   - Zero corrupted timestamps: Filters out epoch 1970 artifacts.
   - Negative timing handling: Identifies and audits negative durations.
   - Deduplication: Drops exact duplicate flows and logs near-duplicate signatures.
4. **1-Minute Temporal Windows**: Aggregates statistical summaries (`mean`, `std`, `sum`, `min`, `max`) per 1-minute window.
5. **Feature-Presence Masks**: Explicit mask indicators (`mask_has_traffic_volume_features`, `mask_has_flow_timing_features`, `mask_has_packet_level_features`, `mask_has_tcp_flags`, `mask_has_graph_topology`, `mask_has_identity_auth`).
6. **Graph Construction per Window**: Directed interaction topology per window with integer node anonymization and lookup mapping (`node_lookup.parquet`).
7. **Two-Phase Infiltration Segmentation**: Distinguishes `Infiltration-Compromise` (initial malware delivery) and `Infiltration-Portscan` (internal lateral discovery) on March 1.
8. **Multi-Horizon Future Forecasting ($H=5$ min)**: Derives target `future_attack_label` strictly by backward shifting target masks with zero future feature leakage.
9. **Leakage-Free Normalization**: Fits `RobustScaler` (median & IQR) and `Log1p` transforms exclusively on the training split (70%) and applies them to validation (15%) and test (15%) partitions.

---

## 📁 Repository Structure

```
├── configs/
│   ├── pipeline_config.yaml           # Master pipeline settings, split ratios, horizons
│   ├── canonical_mapping.yaml          # Audit-ready 80-column canonical mapping
│   └── attack_timelines.yaml           # Ground truth Table 2 attack timelines
├── src/
│   ├── __init__.py
│   ├── ingestion.py                   # Stage 1: Robust CSV reader
│   ├── canonical_mapper.py            # Stage 2: Canonical schema mapper
│   ├── cleaner.py                     # Stage 3: Data cleaning & UTC normalization
│   ├── window_aggregator.py           # Stage 4: 1-min windowing & feature masks
│   ├── graph_builder.py               # Stage 5: Per-window graph topology
│   ├── labeler_and_splits.py          # Stage 6: Attack labeling & chronological splits
│   ├── normalizer.py                  # Stage 7: Leakage-free RobustScaler
│   └── pipeline_runner.py             # Master pipeline runner & audit generator
├── tests/
│   └── test_pipeline.py               # Unit & regression test suite
├── data/
│   ├── raw/                           # Raw CSE-CIC-IDS2018 CSV files
│   ├── intermediate/                  # Staged cleaned parquet files per day
│   └── ucs/                           # Final Unified Cyber State (S_t) artifacts
│       ├── ucs_windows.parquet        # Flat temporal feature state S(t)
│       ├── ucs_graph_edgelists.parquet# Graph topology edge lists
│       ├── node_lookup.parquet        # Anonymized node ID mapping
│       ├── scaler_params.yaml         # Fitted normalization parameters
│       ├── SCHEMA.md                  # Comprehensive column documentation
│       └── VALIDATION_REPORT.md       # Audit statistics & quality gates
└── README.md
```

---

## 🛠️ How to Run

### 1. Run Unit Tests
```bash
python tests/test_pipeline.py
```

### 2. Execute Full Pipeline
```bash
python src/pipeline_runner.py
```

All output datasets and audit reports are written directly to `data/ucs/`.
