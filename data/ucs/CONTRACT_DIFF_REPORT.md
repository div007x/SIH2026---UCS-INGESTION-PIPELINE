# UCSExtractor vs. ML1 Inference Contract Diff Report

**Evaluation Status**: 🔴 **FAIL**  
**Evaluated Contract Version**: `v2`  
**Timestamp (UTC)**: `2026-09-10T07:18:09.908744+00:00`  
**Feature Order Artifact**: `E:\SIH 2026 - UCS Ingestion Pipeline (Main)\scratch\ml1_repo\artifacts\lstm\inference_feature_order_v2.json`  
**Scaler Artifact**: `E:\SIH 2026 - UCS Ingestion Pipeline (Main)\scratch\ml1_repo\artifacts\lstm\inference_scaler_v2.yaml`  

> [!CAUTION]
> **CRITICAL BLOCKER — INFERENCE GATE BLOCKED**
> Positional ordering or scaler parameter divergence detected. The LSTM input layer is positional; any index mismatch will silently feed features into wrong weights.
> **Automated Action**: Automated CI / pre-commit validation has failed with exit code 1. Downstream backend integration MUST NOT invoke `predict()` with `UCSExtractor` outputs until all mismatches are resolved.

## 📌 Dimension Specification & PCAP Packet Count Clarification

This report explicitly confirms that **12 PCAP packet-level features** are included in the UCS contract (indices 394–405).
> [!NOTE]
> **Superseding Note**: Earlier preliminary exploratory leakage audit notes mentioned 9 packet features. This committed report formalizes the complete, authoritative specification of **12 PCAP packet-level features**, officially superseding the earlier partial count across all repository documentation.

### Dimension Verification Table

| Component | Expected (ML1 / Spec) | Observed (UCSExtractor) | Status |
|:---|:---:|:---:|:---:|
| Total LSTM Model Input Columns | 406 | 406 | PASS |
| Scaled Feature Columns (Flow + Packet) | 400 | 400 | PASS |
| Presence Masks (`mask_has_*`) | 6 | 6 | PASS |
| Total Extractor Output (IDs + Masks + Features) | 410 | 410 | PASS |
| Flow Aggregation Features | 388 | 388 | PASS |
| PCAP Packet-Level Features | 12 | 12 | PASS |

## 🔬 Positional Segment Breakdown

The LSTM tensor layout expects features in three strictly sequential contiguous blocks:

```
┌───────────────────────────┬──────────────────────┬────────────────────────────┐
│ Indices 0 .. 387          │ Indices 388 .. 393   │ Indices 394 .. 405         │
│ 388 Flow Features         │ 6 Presence Masks     │ 12 PCAP Packet Features    │
└───────────────────────────┴──────────────────────┴────────────────────────────┘
```

### Segment 2: 6 Presence Masks (Indices 388–393)

| Tensor Index | Mask Column Name | Status |
|:---:|:---|:---:|
| 388 | `mask_has_traffic_volume_features` | MATCH |
| 389 | `mask_has_flow_timing_features` | MATCH |
| 390 | `mask_has_packet_level_features` | MATCH |
| 391 | `mask_has_tcp_flags` | MATCH |
| 392 | `mask_has_graph_topology` | MATCH |
| 393 | `mask_has_identity_auth` | MATCH |

### Segment 3: 12 PCAP Packet Features (Indices 394–405)

| Tensor Index | Feature Column Name | Category | Status |
|:---:|:---|:---|:---:|
| 394 | `pkt_ttl_min` | IP TTL Statistics | MATCH |
| 395 | `pkt_ttl_max` | IP TTL Statistics | MATCH |
| 396 | `pkt_ttl_std` | IP TTL Statistics | MATCH |
| 397 | `pkt_ttl_mode` | IP TTL Statistics | MATCH |
| 398 | `pkt_frag_mf_count` | IP Fragmentation | MATCH |
| 399 | `pkt_frag_df_count` | IP Fragmentation | MATCH |
| 400 | `pkt_payload_size_p25` | Payload Quantiles | MATCH |
| 401 | `pkt_payload_size_p50` | Payload Quantiles | MATCH |
| 402 | `pkt_payload_size_p75` | Payload Quantiles | MATCH |
| 403 | `pkt_payload_size_p95` | Payload Quantiles | MATCH |
| 404 | `pkt_tcp_retrans_count` | TCP Anomalies | MATCH |
| 405 | `pkt_port_scan_seq_score` | Heuristic Scan Score | MATCH |

## 📋 Positional Diff Findings

✅ **Zero positional mismatches detected.** All 406 model input columns are in 100% exact identical order between `UCSExtractor.MODEL_INPUT_COLUMNS` and ML1's contract.

## ⚖️ Scaler Parameter Parity Audit

- **Features Evaluated**: 400 / 400 features
- **Maximum Parameter Deviation**: `2.63625059e+10`
- **Parameter Mismatches**: 1191

❌ **Scaler Parameter Divergences:**

| Feature Name | Parameter | ML1 Value | UCS Value | Absolute Difference |
|:---|:---:|:---:|:---:|:---:|
| `duration_microsec_mean` | `median` | `0.0` | `14770387.468899522` | 1.477039e+07 |
| `duration_microsec_mean` | `scale` | `1.0` | `7138992.385225026` | 7.138991e+06 |
| `duration_microsec_mean` | `q25` | `-0.4924353109324769` | `11254895.533936651` | 1.125490e+07 |
| `duration_microsec_mean` | `q75` | `0.5075646890675231` | `18393887.919161677` | 1.839389e+07 |
| `duration_microsec_std` | `median` | `0.0` | `33804024.98359233` | 3.380402e+07 |
| `duration_microsec_std` | `scale` | `1.0` | `8382648.308490299` | 8.382647e+06 |
| `duration_microsec_std` | `q25` | `-0.6098644024238478` | `28691746.182205617` | 2.869175e+07 |
| `duration_microsec_std` | `q75` | `0.3901355975761523` | `37074394.490695916` | 3.707439e+07 |
| `duration_microsec_sum` | `median` | `0.0` | `14877718166.0` | 1.487772e+10 |
| `duration_microsec_sum` | `scale` | `1.0` | `18859479925.0` | 1.885948e+10 |
| `duration_microsec_sum` | `q25` | `-0.3910336994088664` | `7503025962.0` | 7.503026e+09 |
| `duration_microsec_sum` | `q75` | `0.6089663005911337` | `26362505887.0` | 2.636251e+10 |
| `duration_microsec_min` | `scale` | `1.0` | `9699411.73391782` | 9.699411e+06 |
| `duration_microsec_max` | `median` | `0.0` | `119941811.0` | 1.199418e+08 |
| `duration_microsec_max` | `scale` | `1.0` | `492001.0` | 4.920000e+05 |
| `duration_microsec_max` | `q25` | `-0.8909616037365777` | `119503457.0` | 1.195035e+08 |
| `duration_microsec_max` | `q75` | `0.10903839626342222` | `119995458.0` | 1.199955e+08 |
| `packet_count_fwd_mean` | `median` | `0.0` | `1.8496654668054964` | 1.849665e+00 |
| `packet_count_fwd_mean` | `scale` | `0.459370993611396` | `0.25591390619603205` | 2.034571e-01 |
| `packet_count_fwd_mean` | `q25` | `0.0` | `1.742969305058623` | 1.742969e+00 |
| `packet_count_fwd_mean` | `q75` | `0.459370993611396` | `1.998883211254655` | 1.539512e+00 |
| `packet_count_fwd_std` | `median` | `0.0` | `2.3424951757031387` | 2.342495e+00 |
| `packet_count_fwd_std` | `scale` | `0.5389561492919074` | `1.2490326755327388` | 7.100765e-01 |
| `packet_count_fwd_std` | `q25` | `0.0` | `1.9855422982631725` | 1.985542e+00 |
| `packet_count_fwd_std` | `q75` | `0.5389561492919074` | `3.2345749737959113` | 2.695619e+00 |
| `packet_count_fwd_sum` | `median` | `0.0` | `8.768885326134862` | 8.768885e+00 |
| `packet_count_fwd_sum` | `scale` | `0.40688621724115326` | `1.1664804466221295` | 7.595942e-01 |
| `packet_count_fwd_sum` | `q25` | `0.0` | `8.188133414510478` | 8.188133e+00 |
| `packet_count_fwd_sum` | `q75` | `0.40688621724115326` | `9.354613861132608` | 8.947728e+00 |
| `packet_count_fwd_min` | `median` | `0.0` | `0.6931471805599453` | 6.931472e-01 |
| ... | *and 1161 more mismatches* | | | |

## 🚀 Backend Downstream Integration Guidance

For real-time streaming and inference consumption in Backend's `predict()` pipeline:

```python
from src.ucs_extractor import UCSExtractor

# Initialize extractor once during backend startup
extractor = UCSExtractor(schema_version="v3.0")

# Method 1: Extract direct 2D model tensor (shape: (N_windows, 406), dtype: float32)
model_tensor = extractor.extract_model_tensor(raw_df, source_type="csv")

# Method 2: Extract full 410-column DataFrame (provenance + masks + features)
ucs_df = extractor.extract(raw_df, source_type="csv")
model_tensor = ucs_df[UCSExtractor.MODEL_INPUT_COLUMNS].to_numpy(dtype=np.float32)
```

---
*Report automatically generated by `scripts/diff_ucs_ml1_contract.py` on 2026-09-10T07:18:09.908744+00:00.*