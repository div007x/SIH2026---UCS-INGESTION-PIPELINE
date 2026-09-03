"""
Unit & Regression Tests for Unified Cyber State (S_t) Ingestion Pipeline
Executable with standard Python unittest or pytest.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timezone

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion import ingest_csv_file, extract_day_from_filename
from src.canonical_mapper import map_to_canonical_schema
from src.cleaner import clean_and_normalize_flow_data, impute_missing_flow_values
from src.window_aggregator import create_1min_windows
from src.graph_builder import GraphTopologyBuilder
from src.labeler_and_splits import assign_window_labels, generate_future_attack_labels, assign_chronological_splits
from src.normalizer import LeakageSafeRobustScaler, normalize_window_features


class TestUCSDataPipeline(unittest.TestCase):

    def setUp(self):
        """Creates synthetic flow dataframe mimicking CSE-CIC-IDS2018 raw CSV."""
        self.sample_raw_df = pd.DataFrame({
            "Dst Port": [80, 443, 22, 80, 80],
            "Protocol": [6, 6, 6, 6, 6],
            "Timestamp": [
                "14/02/2018 08:30:00",
                "14/02/2018 08:30:15",
                "14/02/2018 08:31:05",
                "14/02/2018 08:31:40",
                "14/02/2018 08:32:10",
            ],
            "Flow Duration": [1000000, 2000000, 500000, 1000000, 1500000],
            "Tot Fwd Pkts": [10, 20, 5, 10, 15],
            "Tot Bwd Pkts": [5, 10, 2, 5, 8],
            "TotLen Fwd Pkts": [1000, 2000, 500, 1000, 1500],
            "TotLen Bwd Pkts": [500, 1000, 200, 500, 800],
            "Flow Byts/s": [1500.0, np.inf, 1400.0, 1500.0, 1533.3],
            "Flow Pkts/s": [15.0, 15.0, 14.0, 15.0, 15.3],
            "Down/Up Ratio": [0, 1, 0, 0, 1],
            "Init Fwd Win Byts": [8192, 8192, 4096, 8192, 8192],
            "Init Bwd Win Byts": [255, 255, 128, 255, 255],
            "Label": ["Benign", "FTP-BruteForce", "FTP-BruteForce", "Benign", "Benign"],
            "source_file": ["Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv"] * 5,
            "source_day": ["14-02-2018"] * 5,
        })

    def test_filename_extraction(self):
        fname = "Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv"
        self.assertEqual(extract_day_from_filename(fname), "14-02-2018")

    def test_canonical_mapping(self):
        mapped_df, audit = map_to_canonical_schema(self.sample_raw_df)
        self.assertIn("destination_port", mapped_df.columns)
        self.assertIn("protocol", mapped_df.columns)
        self.assertIn("byte_count_fwd", mapped_df.columns)
        self.assertIn("window_size_fwd", mapped_df.columns)
        self.assertIn("window_size_bwd", mapped_df.columns)
        self.assertIn("down_up_ratio", mapped_df.columns)
        self.assertGreater(audit["mapped_columns_count"], 0)

    def test_cleaning_and_inf_handling(self):
        mapped_df, _ = map_to_canonical_schema(self.sample_raw_df)
        cleaned_df, audit = clean_and_normalize_flow_data(mapped_df)
        
        # Check that Inf was replaced with NaN
        self.assertFalse(np.isinf(cleaned_df["bytes_per_sec"]).any())
        self.assertEqual(audit["infinities_replaced_with_nan"]["bytes_per_sec"], 1)
        
        # Check UTC datetime conversion
        self.assertIn("timestamp_utc", cleaned_df.columns)
        self.assertEqual(str(cleaned_df["timestamp_utc"].dt.tz), "UTC")
        self.assertTrue(cleaned_df["timestamp_utc"].is_monotonic_increasing)

    def test_window_aggregation(self):
        mapped_df, _ = map_to_canonical_schema(self.sample_raw_df)
        cleaned_df, _ = clean_and_normalize_flow_data(mapped_df)
        cleaned_df, _ = impute_missing_flow_values(cleaned_df)
        window_df, audit = create_1min_windows(cleaned_df, interval_sec=60)
        
        self.assertEqual(len(window_df), 3)  # 08:30, 08:31, 08:32
        self.assertIn("window_id", window_df.columns)
        self.assertIn("mask_has_packet_level_features", window_df.columns)
        self.assertIn("mask_has_traffic_volume_features", window_df.columns)
        self.assertTrue((window_df["mask_has_packet_level_features"] == 1.0).all())
        self.assertTrue((window_df["mask_has_identity_auth"] == 0.0).all())

    def test_graph_builder(self):
        mapped_df, _ = map_to_canonical_schema(self.sample_raw_df)
        cleaned_df, _ = clean_and_normalize_flow_data(mapped_df)
        builder = GraphTopologyBuilder()
        edge_df, node_lookup_df, audit = builder.build_window_edge_lists(cleaned_df, interval_sec=60)
        
        self.assertGreater(len(edge_df), 0)
        self.assertIn("window_id", edge_df.columns)
        self.assertIn("src_node_id", edge_df.columns)
        self.assertIn("dst_node_id", edge_df.columns)
        self.assertGreater(len(node_lookup_df), 0)

    def test_future_attack_label_leakage_safety(self):
        times = pd.date_range("2018-02-14 10:00:00", periods=5, freq="1min", tz="UTC")
        df = pd.DataFrame({
            "window_start_utc": times,
            "label_binary": [0, 0, 1, 0, 0]
        })
        
        df = generate_future_attack_labels(df, horizon_windows=2, target_col="label_binary")
        self.assertEqual(df["future_attack_label"].tolist(), [1, 1, 0, 0, 0])

    def test_chronological_splits(self):
        times = pd.date_range("2018-02-14 10:00:00", periods=10, freq="1min", tz="UTC")
        df = pd.DataFrame({"window_start_utc": times})
        df, audit = assign_chronological_splits(df, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
        
        self.assertEqual((df["split"] == "train").sum(), 7)
        self.assertEqual((df["split"] == "val").sum(), 1)
        self.assertEqual((df["split"] == "test").sum(), 2)
        self.assertLess(audit["train_end"], audit["val_start"])
        self.assertLess(audit["val_end"], audit["test_start"])

    def test_leakage_safe_robust_scaler(self):
        train_data = pd.DataFrame({
            "f1": [10.0, 20.0, 30.0, 40.0, 50.0],
            "split": ["train"] * 5
        })
        val_data = pd.DataFrame({
            "f1": [100.0, 200.0],
            "split": ["val"] * 2
        })
        full_df = pd.concat([train_data, val_data], ignore_index=True)
        
        scaler = LeakageSafeRobustScaler()
        scaler.fit(train_data, ["f1"])
        transformed = scaler.transform(full_df)
        
        self.assertEqual(transformed.loc[2, "f1"], 0.0)
        self.assertEqual(transformed.loc[0, "f1"], -1.0)
        self.assertEqual(transformed.loc[4, "f1"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
