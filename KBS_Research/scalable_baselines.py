"""Scalable, deterministic, temporally censored observed-positive retrieval.

Candidate generation uses graph two-hop neighbors plus top-degree nodes.
It DOES NOT enumerate all organization pairs. Coverage is reported separately
from ranking recall; unobserved links are unlabeled, not true negatives.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

def read(path):
    with path.open(newline="",encoding="utf-8") as f:
        yield from csv.DictReader(f)

def evaluate(folder, cutoff, horizon, k=10, top_degree=100, max_twohop=2000, max_queries=250):
    if not cutoff<horizon:raise ValueError("cutoff must be earlier than horizon")
    nodes={r["organization_id"] for r in read(folder/"known_organizations.csv")}
    adj={n:set() for n in nodes}
    positives=defaultdict(set)
    for filename in ("train_edges.csv","validation_positives.csv","test_positives.csv"):
        for r in read(folder/filename):
            a,b=r["org_a"],r["org_b"]
            if a not in nodes or b not in nodes:continue
            when=date.fromisoformat(r["first_collaboration_date"])
            if when<=cutoff:
                adj[a].add(b);adj[b].add(a)
            elif when<=horizon:
                positives[a].add(b);positives[b].add(a)
    degree={n:len(adj[n]) for n in nodes}
    hubs=sorted(nodes,key=lambda n:(-degree[n],n))[:top_degree]
    methods=("common_neighbors","adamic_adar","resource_allocation","preferential_attachment")
    hits={m:0 for m in methods}
    covered=0;total=0;queries=0; candidate_total=0
    all_sources=sorted(positives)
    selected_sources=all_sources[:max_queries]
    for source in selected_sources:
        truth=positives[source]
        if not truth:continue
        queries+=1;total+=len(truth)
        # Deterministic cap: prioritize intermediary nodes by degree, then ID.
        via=sorted(adj[source],key=lambda n:(-degree[n],n))
        candidates=set(hubs)
        for middle in via:
            candidates.update(adj[middle])
            if len(candidates)>=max_twohop:break
        candidates.discard(source)
        candidates.difference_update(adj[source])
        # Keep deterministic bounded set if a high-degree intermediary overflows.
        if len(candidates)>max_twohop:
            candidates=set(sorted(candidates,key=lambda n:(-degree[n],n))[:max_twohop])
        candidate_total+=len(candidates)
        covered+=len(truth&candidates)
        rankings={m:[] for m in methods}
        for target in candidates:
            shared=adj[source]&adj[target]
            scores=(len(shared),
                    sum(1/math.log(degree[z]) for z in shared if degree[z]>1),
                    sum(1/degree[z] for z in shared if degree[z]),
                    degree[source]*degree[target])
            for method,score in zip(methods,scores):
                rankings[method].append((score,target))
        for method in methods:
            ranked=sorted(rankings[method],key=lambda x:(-x[0],x[1]))[:k]
            hits[method]+=sum(target in truth for _,target in ranked)
    return {"cutoff":str(cutoff),"horizon":str(horizon),"k":k,
            "known_organizations":len(nodes),"query_organizations":queries,"total_eligible_query_organizations":len(all_sources),
            "query_selection":"First organization IDs in sorted order; deterministic convenience cohort, not representative sampling.",
            "observed_positive_instances":total,
            "mean_candidates_per_query":candidate_total/queries if queries else None,
            "candidate_coverage":covered/total if total else None,
            "observed_positive_recall_at_k":{m:hits[m]/total if total else None for m in methods},
            "limitations":"Candidate-limited observed-positive retrieval; coverage is not global recall; unlabeled nonedges are not verified negatives. Retrospective archive may leak historical publication availability."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/processed"))
    p.add_argument("--k",type=int,default=10)
    p.add_argument("--top-degree",type=int,default=100)
    p.add_argument("--max-twohop",type=int,default=2000)
    p.add_argument("--max-queries",type=int,default=250)
    a=p.parse_args()
    if min(a.k,a.top_degree,a.max_twohop,a.max_queries)<1:p.error("k, top-degree and max-twohop must be positive")
    results=[evaluate(a.data,date(2023,12,31),date(2024,12,31),a.k,a.top_degree,a.max_twohop,a.max_queries),
             evaluate(a.data,date(2024,12,31),date(2025,12,31),a.k,a.top_degree,a.max_twohop)]
    output=a.data/"scalable_baseline_results.json"
    output.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))
if __name__=="__main__":main()
