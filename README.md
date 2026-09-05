
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
8. **Multi-Horizon Future Forecasting ($H=5$ min Primary)**: Derives target `future_attack_label` strictly by backward shifting target masks with zero future feature leakage. Primary validated horizon is $H=5$ windows (5 minutes lead time, validated through Gate 0 LOEO). Horizons $H=10$ and $H=15$ are secondary sensitivity-analysis horizons only.
9. **Temporal Leakage Protection (Purge + Embargo)**: Enforces $W = L + H = 30 + 5 = 35$ window purge/embargo zone at both Train→Val and Val→Test boundaries (dropping 140 windows total). Ensures zero future-horizon or past-lookback overlap across partitions.
10. **Boundary-Safe LSTM Sequence Construction**: Constructs input sequences of length $L=30$ windows (`src/sequence_builder.py`). Rejects any sequence crossing split boundaries.
11. **LR/LSTM Protocol Parity**: Guarantees that both tabular Logistic Regression (flat windows) and LSTM (sequences) consume the exact same purged/embargoed window sets and training-fit scaler parameters.
12. **Leakage-Free Normalization**: Fits `RobustScaler` (median & IQR) and `Log1p` transforms exclusively on the post-purge training split (2,013 windows) and applies them to validation (369 windows) and test (405 windows) partitions.

---

## 📁 Repository Structure

```
├── configs/
│   ├── pipeline_config.yaml           # Master pipeline settings, split ratios, horizons, LSTM lookback
│   ├── canonical_mapping.yaml          # Audit-ready 80-column canonical mapping
│   └── attack_timelines.yaml           # Ground truth Table 2 attack timelines
├── src/
│   ├── __init__.py
│   ├── ingestion.py                   # Stage 1: Robust CSV reader
│   ├── canonical_mapper.py            # Stage 2: Canonical schema mapper
│   ├── cleaner.py                     # Stage 3: Data cleaning & UTC normalization
│   ├── window_aggregator.py           # Stage 4: 1-min windowing & feature masks
│   ├── graph_builder.py               # Stage 5: Per-window graph topology
│   ├── labeler_and_splits.py          # Stage 6: Attack labeling, chronological splits & purge+embargo
│   ├── normalizer.py                  # Stage 7: Leakage-free RobustScaler (post-purge train fit)
│   ├── sequence_builder.py            # Stage 8: Boundary-safe LSTM sequence construction & LR parity
│   └── pipeline_runner.py             # Master pipeline runner & audit generator
├── tests/
│   └── test_pipeline.py               # Unit & regression test suite (10/10 passing)
├── data/
│   ├── raw/                           # Raw CSE-CIC-IDS2018 CSV files
│   ├── intermediate/                  # Staged cleaned parquet files per day
│   └── ucs/                           # Final Unified Cyber State (S_t) artifacts
│       ├── ucs_windows.parquet        # Flat temporal feature state S(t) (purged)
│       ├── ucs_graph_edgelists.parquet# Graph topology edge lists (unmodified)
│       ├── node_lookup.parquet        # Anonymized node ID mapping (unmodified)
│       ├── scaler_params.yaml         # Fitted normalization parameters (post-purge)
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

---

## ⚠️ Limitations

- **Contiguous Episode Granularity**: Pulsing/intermittent C2 traffic can be split into multiple single-window episodes under the strict contiguity rule; this is documented and does not affect leakage boundaries.
- **Packet-Level Feature Scope**: Raw PCAP packet extraction is currently scoped to Wednesday-14-02-2018 (`SSH-Bruteforce`); all remaining days use flow-level telemetry and have `mask_has_packet_level_features = 0.0`.

