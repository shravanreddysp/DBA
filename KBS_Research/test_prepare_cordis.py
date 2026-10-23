"""Offline contract test using a tiny *synthetic schema fixture* only.
This tests parsing/splitting; it is NOT an empirical research result.
"""
import csv
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from prepare_cordis import prepare

class CordisPipelineTest(unittest.TestCase):
    def test_first_collaboration_cutoffs(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); archive=root/"fixture.zip"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("project.csv",
                    "id,startDate\nP1,2023-02-01\nP2,2023-05-01\nP3,2024-05-01\nP4,2025-05-01\n")
                z.writestr("organization.csv",
                    "projectID,organisationID\nP1,A\nP1,B\nP2,A\nP2,C\nP3,B\nP3,C\nP4,A\nP4,D\n")
            out=root/"out"
            stats=prepare(archive,out,date(2023,12,31),date(2024,12,31),date(2025,12,31))
            self.assertEqual(stats["training_first_collaboration_edges"],2)
            self.assertEqual(stats["validation_first_collaborations"],1)
            # D is not known by the train cutoff: exclude cold-start pair A-D.
            self.assertEqual(stats["test_first_collaborations"],0)
            self.assertEqual(stats["organizations_known_by_train_end"],3)
            self.assertEqual(stats["candidate_pairs_after_train_cutoff"],1)
            with (out/"validation_positives.csv").open() as f:
                self.assertEqual(list(csv.DictReader(f))[0]["org_a"],"B")

if __name__=="__main__": unittest.main()
