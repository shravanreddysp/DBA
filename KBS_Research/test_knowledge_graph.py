import csv
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from build_knowledge_graph import export_graph

class KGTests(unittest.TestCase):
    def test_typed_edges_and_future_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/"source.zip"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("project.csv","id,startDate\nP1,2023-04-01\nP2,2024-01-01\n")
                z.writestr("organization.csv","projectID,organisationID\nP1,A\nP1,B\nP2,A\nP2,C\n")
            out=root/"out";result=export_graph(archive,out,date(2023,12,31))
            self.assertEqual(result["projects"],1)
            self.assertEqual(result["participation_edges"],2)
            with (out/"kg_edges.csv").open(newline="") as f:
                edges=list(csv.DictReader(f))
            self.assertEqual({r["target"] for r in edges},{"project:P1"})
            self.assertEqual({r["relation"] for r in edges},{"participates_in"})
            self.assertEqual({r["event_date"] for r in edges},{"2023-04-01"})

if __name__=="__main__":unittest.main()
