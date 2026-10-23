import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
from temporal_baselines import evaluate

class TemporalBaselineTests(unittest.TestCase):
    def test_temporal_cutoffs(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            def write(name,header,rows):
                with (folder/name).open("w",newline="") as f:
                    w=csv.writer(f);w.writerow(header);w.writerows(rows)
            write("known_organizations.csv",["organization_id"],[["A"],["B"],["C"],["D"]])
            header=["org_a","org_b","first_collaboration_date"]
            write("train_edges.csv",header,[["A","B","2023-01-01"],["A","C","2023-01-01"]])
            write("validation_positives.csv",header,[["B","C","2024-05-01"]])
            write("test_positives.csv",header,[["B","D","2025-03-01"]])
            val=evaluate(folder,date(2023,12,31),date(2024,12,31),k=2)
            test=evaluate(folder,date(2024,12,31),date(2025,12,31),k=2)
            self.assertEqual(val["observed_positive_source_instances"],2)
            self.assertEqual(test["observed_positive_source_instances"],2)
            for m in test["results"].values():
                self.assertGreaterEqual(m["micro_recall_at_k"],0)
                self.assertLessEqual(m["micro_recall_at_k"],1)
    def test_candidate_guard(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            (folder/"known_organizations.csv").write_text("organization_id\nA\nB\nC\n")
            for name in ("train_edges.csv","validation_positives.csv","test_positives.csv"):
                (folder/name).write_text("org_a,org_b,first_collaboration_date\n")
            with self.assertRaisesRegex(ValueError,"Candidate universe too large"):
                evaluate(folder,date(2023,12,31),date(2024,12,31),max_candidates=5)
if __name__=="__main__":unittest.main()
