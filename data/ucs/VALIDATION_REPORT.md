# Validation & Audit Report: Unified Cyber State ($S_t$) Pipeline
**SIH26153 — Cyber World Model Architecture (Data Engineer Track)**
**Generated Date**: 2026-09-02 21:54:16 UTC

---

## 1. Executive Summary & Quality Gates

| Quality Gate / Check | Requirement | Result | Status |
| :--- | :--- | :--- | :--- |
| **Zero Infinities** | 0 Inf / -Inf in final output | **0** | **PASSED** |
| **Zero Feature NaNs** | 0 unexpected NaN values | **0** | **PASSED** |
| **Chronological Monotonicity** | Strict ascending order within & across splits | **True** | **PASSED** |
| **Chronological Split Discipline** | Train -> Val -> Test strict time partitions | **70% / 15% / 15%** | **PASSED** |
| **Leakage-Free Normalization** | RobustScaler fit exclusively on Train | **Fitted on Train only** | **PASSED** |
| **Future Forecast Alignment** | Target backward shift with no future feature leakage | **H=5 min horizon** | **PASSED** |

---

## 2. Dataset Processing & Row Accounting

| Source File / Day | Initial Rows | Dropped Headers / Corrupted | Exact Duplicates Dropped | Cleaned Rows | 1-Min Windows | Graph Edges |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv` | 1,048,575 | 5 | 225,628 | 822,942 | 543 | 111,003 |
| `Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv` | 1,048,575 | 0 | 17,557 | 1,031,018 | 170 | 110,651 |
| `Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv` | 331,100 | 0 | 73 | 331,027 | 570 | 79,971 |
| `Friday-02-03-2018_TrafficForML_CICFlowMeter.csv` | 1,048,575 | 0 | 5,459 | 1,043,116 | 525 | 145,510 |
| `Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv` | 1,048,575 | 9 | 3,278 | 1,045,288 | 549 | 224,077 |
| `Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv` | 613,071 | 0 | 6,089 | 606,982 | 570 | 82,859 |

---

## 3. Split Boundaries & Chronological Audit

- **Training Partition (70%)**: 2,048 windows (`2018-02-14 01:00:00+00:00` to `2018-03-01 04:35:00+00:00`)
- **Validation Partition (15%)**: 439 windows (`2018-03-01 04:36:00+00:00` to `2018-03-02 02:24:00+00:00`)
- **Testing Partition (15%)**: 440 windows (`2018-03-02 02:25:00+00:00` to `2018-03-02 12:59:00+00:00`)

---

## 4. Class Distribution & Contiguous Attack Episodes

### Window Class Distribution:
```
label_attack_type
Benign                     2610
Infiltration-Compromise      97
SSH-Bruteforce               82
Infiltration-Portscan        58
Botnet                       53
DDOS-LOIC-UDP                19
DDOS-HOIC                     8
```

### Binary Label Distribution:
- **Benign (0)**: 1,931 windows (65.97%)
- **Attack (1)**: 996 windows (34.03%)
- **Future Attack ($H=5$ min)**: 1,054 windows (36.01%)

### Independent Attack Episodes (Contiguous Attack Runs):
- **SSH-Bruteforce**: 9 independent attack episode(s)
- **DDOS-HOIC**: 1 independent attack episode(s)
- **DDOS-LOIC-UDP**: 18 independent attack episode(s)
- **Infiltration-Compromise**: 1 independent attack episode(s)
- **Infiltration-Portscan**: 1 independent attack episode(s)
- **Botnet**: 11 independent attack episode(s)

> [!NOTE]
> **Infiltration Two-Phase Segmentation Verified**: The pipeline successfully segmented March 1 Infiltration traffic into `Infiltration-Compromise` (initial malware drop & C2 connection) and `Infiltration-Portscan` (internal lateral discovery), preserving the two-phase progression required for forecasting.
