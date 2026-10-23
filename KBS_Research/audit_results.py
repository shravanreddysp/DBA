"""Descriptive audit of real CORDIS temporal KG aggregate results.
Seed ranges are NOT confidence intervals; no inferential claims.
"""
import argparse,json,statistics
from pathlib import Path

def audit(model_path,output):
    obj=json.loads(Path(model_path).read_text())
    if len(obj["validation"])<2 or len(obj["test"])<2:
        raise ValueError("At least two seeds required")
    rows=[]
    for split in ("validation","test"):
        for r in obj[split]:
            aa=r["recall_at_k"]["aa"];kg=r["recall_at_k"]["kg"]
            if not (0<=aa<=1 and 0<=kg<=1):raise ValueError("Invalid recall")
            rows.append(dict(split=split,seed=r["seed"],aa=aa,kg=kg,delta=kg-aa,
                             coverage=r["candidate_coverage"],positives=r["positive_instances"]))
    summary={}
    for split in ("validation","test"):
        group=[r for r in rows if r["split"]==split]
        summary[split]={"n_seeds":len(group),
          "mean_aa":statistics.mean(r["aa"] for r in group),
          "mean_kg":statistics.mean(r["kg"] for r in group),
          "mean_delta":statistics.mean(r["delta"] for r in group),
          "min_delta":min(r["delta"] for r in group),
          "max_delta":max(r["delta"] for r in group),
          "positive_delta_seeds":sum(r["delta"]>0 for r in group),
          "mean_candidate_coverage":statistics.mean(r["coverage"] for r in group)}
    result={"chosen_weight":obj["chosen_weight"],"summary":summary,"per_seed":rows,
      "statistical_caution":"Overlapping samples from one network; ranges are descriptive, not confidence intervals or significance tests.",
      "data_caution":"Retrospective project start dates do not establish point-in-time public availability."}
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="data/processed/kg_model_results.json")
    p.add_argument("--out",default="data/processed/audit_results.json")
    a=p.parse_args()
    print(json.dumps(audit(a.input,a.out)["summary"],indent=2))
