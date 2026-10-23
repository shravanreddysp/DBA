import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
from scalable_baselines import evaluate

class ScalableBaselineTest(unittest.TestCase):
    def test_temporal_censoring_and_candidate_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            def write(name,head,rows):
                with (p/name).open("w",newline="") as f:
                    w=csv.writer(f);w.writerow(head);w.writerows(rows)
            write("known_organizations.csv",["organization_id"],[(x,) for x in "ABCD"])
            head=("org_a","org_b","first_collaboration_date")
            write("train_edges.csv",head,[("A","B","2023-01-01"),("A","C","2023-01-01")])
            write("validation_positives.csv",head,[("B","C","2024-01-01")])
            write("test_positives.csv",head,[("B","D","2025-01-01")])
            val=evaluate(p,date(2023,12,31),date(2024,12,31),k=1,top_degree=4,max_twohop=10)
            test=evaluate(p,date(2024,12,31),date(2025,12,31),k=1,top_degree=4,max_twohop=10)
            self.assertEqual(val["observed_positive_instances"],2)
            self.assertEqual(test["observed_positive_instances"],2)
            self.assertEqual(val["candidate_coverage"],1.0)
            self.assertEqual(test["candidate_coverage"],1.0)
            self.assertEqual(val["query_organizations"],4)
            self.assertEqual(val["query_organizations_with_future_positives"],2)
            sampled=evaluate(p,date(2023,12,31),date(2024,12,31),k=1,
                             top_degree=4,max_twohop=10,max_queries=2,seed=11)
            self.assertEqual(sampled["query_organizations"],2)
            self.assertEqual(sampled["seed"],11)
            for m in val["observed_positive_recall_at_k"].values():
                self.assertGreaterEqual(m,0);self.assertLessEqual(m,1)

if __name__=="__main__":unittest.main()
