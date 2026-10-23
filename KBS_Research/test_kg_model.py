import csv
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from kg_model import load, snapshot, rank, run

class KGModelTests(unittest.TestCase):
    def test_future_projects_are_excluded(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"known_organizations.csv").write_text("organization_id\nA\nB\nC\nD\n")
            (p/"train_edges.csv").write_text("org_a,org_b,first_collaboration_date\nA,B,2023-01-01\nA,C,2023-01-01\n")
            (p/"validation_positives.csv").write_text("org_a,org_b,first_collaboration_date\nB,C,2024-01-01\n")
            (p/"test_positives.csv").write_text("org_a,org_b,first_collaboration_date\nB,D,2025-01-01\n")
            archive=p/"fixture.zip"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("project.csv","id,startDate\nP1,2023-01-01\nP2,2024-01-01\n")
                z.writestr("organization.csv","projectID,organisationID\nP1,A\nP1,B\nP2,A\nP2,C\n")
            known,events,projects,members=load(p,archive)
            adj,activity=snapshot(known,events,projects,members,date(2023,12,31))
            self.assertEqual(activity["A"],1)
            self.assertEqual(activity["C"],0)
            self.assertNotIn("C",adj["B"])
            result=run(p,archive,seeds=(1,2),weights=(0.,.5),queries=4)
            self.assertIn(result["chosen_weight"],(0.,.5))
            self.assertEqual(len(result["test"]),2)
            self.assertEqual(result["test"][0]["queries"],4)
            self.assertEqual(set(result["test"][0]["recall_at_k"]),{"aa","kg","cn","ra","pa","bp"})
            self.assertEqual(result["test"][0]["positive_instances"],2)
            self.assertEqual(result["validation"][0]["positive_instances"],2)
if __name__=="__main__":unittest.main()
