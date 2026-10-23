"""Validate a locally prepared CORDIS temporal collaboration export.

Run after prepare_cordis.py; requires only Python's standard library.
This checks structural consistency, NOT the accuracy of the official source.
"""
import argparse
import csv
import json
from datetime import date
from pathlib import Path

def read_csv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def validate(root):
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    train_end=date.fromisoformat(manifest["train_end"])
    val_end=date.fromisoformat(manifest["validation_end"])
    test_end=date.fromisoformat(manifest["test_end"])
    assert train_end<val_end<test_end
    known={r["organization_id"] for r in read_csv(root/"known_organizations.csv")}
    assert len(known)==manifest["organizations_known_by_train_end"]
    paths={"train":("train_edges.csv",None,train_end),
           "validation":("validation_positives.csv",train_end,val_end),
           "test":("test_positives.csv",val_end,test_end)}
    pair_sets={}
    for split,(name,lower,upper) in paths.items():
        records=read_csv(root/name)
        pairs=set()
        for r in records:
            a,b=r["org_a"],r["org_b"]
            assert a<b,(split,a,b)
            assert a in known and b in known,(split,a,b)
            pair=(a,b)
            assert pair not in pairs,(split,pair)
            pairs.add(pair)
            d=date.fromisoformat(r["first_collaboration_date"])
            assert d<=upper and (lower is None or d>lower),(split,pair,d)
        pair_sets[split]=pairs
    assert not (pair_sets["train"]&pair_sets["validation"])
    assert not (pair_sets["train"]&pair_sets["test"])
    assert not (pair_sets["validation"]&pair_sets["test"])
    assert len(pair_sets["validation"])==manifest["validation_first_collaborations"]
    assert len(pair_sets["test"])==manifest["test_first_collaborations"]
    return {k:len(v) for k,v in pair_sets.items()}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/processed"))
    a=p.parse_args()
    print(json.dumps(validate(a.data),indent=2))
