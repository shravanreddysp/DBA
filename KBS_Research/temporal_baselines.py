"""Temporal graph-only CORDIS observed-collaboration retrieval baselines.

Unknown pairs are unlabeled, not verified negatives. Requires prepared CORDIS
CSV exports. No measured real-data performance is claimed by this script.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

def read_rows(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def evaluate(folder,cutoff,horizon,k=10,max_candidates=2000000):
    if not cutoff<horizon: raise ValueError("cutoff must precede horizon")
    edges=[]
    for name in ("train_edges.csv","validation_positives.csv","test_positives.csv"):
        for r in read_rows(folder/name):
            edges.append((r["org_a"],r["org_b"],date.fromisoformat(r["first_collaboration_date"])))
    nodes=sorted(r["organization_id"] for r in read_rows(folder/"known_organizations.csv"))
    if len(nodes)*(len(nodes)-1)>max_candidates:
        raise ValueError("Candidate universe too large; select a documented cohort or increase --max-candidates. No hidden candidate sampling.")
    node_set=set(nodes)
    neighbors={n:set() for n in nodes}
    future=defaultdict(set)
    for a,b,d in edges:
        if a not in node_set or b not in node_set:continue
        if d<=cutoff:
            neighbors[a].add(b);neighbors[b].add(a)
        elif d<=horizon:
            future[a].add(b);future[b].add(a)
    methods=("common_neighbors","adamic_adar","resource_allocation","preferential_attachment")
    recalls={m:[] for m in methods}
    hits={m:0 for m in methods}
    denominator=0
    for a in nodes:
        targets=future[a]
        if not targets:continue
        denominator+=len(targets)
        scored={m:[] for m in methods}
        for b in nodes:
            if b==a or b in neighbors[a]:continue
            common=neighbors[a]&neighbors[b]
            scores=(len(common),
                    sum(1/math.log(len(neighbors[z])) for z in common if len(neighbors[z])>1),
                    sum(1/len(neighbors[z]) for z in common if neighbors[z]),
                    len(neighbors[a])*len(neighbors[b]))
            for method,value in zip(methods,scores):
                scored[method].append((value,b))
        for method in methods:
            top=sorted(scored[method],key=lambda item:(-item[0],item[1]))[:k]
            count=sum(b in targets for _,b in top)
            hits[method]+=count
            recalls[method].append(count/len(targets))
    return {"cutoff":str(cutoff),"horizon":str(horizon),"k":k,
            "known_nodes":len(nodes),"evaluated_source_nodes":sum(bool(v) for v in future.values()),
            "observed_positive_source_instances":denominator,
            "metric_note":"Observed-positive Recall@K; unobserved links are unlabeled, not true negatives.",
            "results":{m:{"macro_recall_at_k":sum(recalls[m])/len(recalls[m]) if recalls[m] else None,
                           "micro_recall_at_k":hits[m]/denominator if denominator else None}
                       for m in methods}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/processed"))
    p.add_argument("--k",type=int,default=10)
    p.add_argument("--max-candidates",type=int,default=2000000)
    args=p.parse_args()
    if args.k<1:p.error("--k must be positive")
    results=[evaluate(args.data,date(2023,12,31),date(2024,12,31),args.k,args.max_candidates),
             evaluate(args.data,date(2024,12,31),date(2025,12,31),args.k,args.max_candidates)]
    (args.data/"baseline_results.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
if __name__=="__main__":main()
