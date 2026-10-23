import json,tempfile,unittest
from pathlib import Path
from audit_results import audit
class AuditTests(unittest.TestCase):
    def test_descriptive_deltas(self):
        r={"chosen_weight":.5,
           "validation":[{"seed":i,"recall_at_k":{"aa":.1,"kg":.2},"candidate_coverage":.5,"positive_instances":5} for i in (1,2)],
           "test":[{"seed":i,"recall_at_k":{"aa":.2,"kg":.1},"candidate_coverage":.6,"positive_instances":4} for i in (1,2)]}
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"in.json";b=Path(d)/"out.json";a.write_text(json.dumps(r))
            result=audit(a,b)
            self.assertAlmostEqual(result["summary"]["test"]["mean_delta"],-.1)
            self.assertIn("not confidence intervals",result["statistical_caution"])
if __name__=="__main__":unittest.main()
