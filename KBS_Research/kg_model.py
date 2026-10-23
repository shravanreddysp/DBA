"""Temporal KG participation-aware collaboration retrieval experiment.

Graph evidence and organization-project memberships are frozen at each cutoff.
Weights are selected on 2024 only, then frozen for 2025. Unknown pairs are
unlabeled. All outputs exploratory; public disclosure dates are unverified.
"""
import argparse
import csv
import json
import math
import hashlib
import statistics
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from prepare_cordis import field, parse_date, rows_from_zip

def stable(seed,*values):
    return hashlib.sha256("|".join(map(str,(seed,)+values)).encode()).digest()

def load(folder, archive):
    known={r["organization_id"] for r in csv.DictReader((folder/"known_organizations.csv").open())}
    events=[]
    for name in ("train_edges.csv","validation_positives.csv","test_positives.csv"):
        with (folder/name).open(newline="") as f:
            for r in csv.DictReader(f):
                if r["org_a"] in known and r["org_b"] in known:
                    events.append((r["org_a"],r["org_b"],date.fromisoformat(r["first_collaboration_date"])))
    projects={}
    with zipfile.ZipFile(archive) as z:
        for r in rows_from_zip(z,"project.csv"):
            pid=field(r,"id","projectID","projectId")
            when=parse_date(field(r,"startDate","start_date"))
            if pid and when:projects[pid]=when
        memberships=defaultdict(set)
        for r in rows_from_zip(z,"organization.csv"):
            pid=field(r,"projectID","projectId","project_id")
            org=field(r,"organisationID","organizationID","organisationId","organizationId")
            if pid in projects and org in known:memberships[pid].add(org)
    return known,events,projects,memberships

def snapshot(known,events,projects,memberships,cutoff):
    adj={n:set() for n in known}
    for a,b,d in events:
        if d<=cutoff:adj[a].add(b);adj[b].add(a)
    # Project participation graph, with project-size filter matching data prep.
    org_projects=defaultdict(set)
    project_members={}
    for pid,orgs in memberships.items():
        if projects[pid]>cutoff or not 2<=len(orgs)<=60:continue
        project_members[pid]=orgs
        for org in orgs:org_projects[org].add(pid)
    # Shared-project co-membership is already present in historical links;
    # use historical project context to weight shared collaborators.
    activity={n:len(org_projects[n]) for n in known}
    return adj,activity

def rank(seed, known, events, projects, memberships, cutoff, horizon,
         k=10, query_count=250, candidate_budget=2250, explore=250,
         weight=0.0):
    adj,activity=snapshot(known,events,projects,memberships,cutoff)
    future=defaultdict(set)
    for a,b,d in events:
        if cutoff<d<=horizon:future[a].add(b);future[b].add(a)
    degree={n:len(adj[n]) for n in known}
    hubs=sorted(known,key=lambda n:(-degree[n],n))[:100]
    sources=sorted(known,key=lambda n:(stable(seed,"query",n),n))[:query_count]
    hits={"aa":0,"kg":0,"cn":0,"ra":0,"pa":0};covered=0;total=0;query_positive=0
    for source in sources:
        truth=future[source]
        total+=len(truth)
        query_positive+=bool(truth)
        # Build candidate pool without any future-label information.
        pool=set(hubs)
        for intermediate in sorted(adj[source],key=lambda n:(-degree[n],n)):
            pool.update(adj[intermediate])
            if len(pool)>=candidate_budget-explore:break
        exploratory=sorted(known,key=lambda n:(stable(seed,"explore",source,n),n))[:explore]
        pool.update(exploratory)
        pool.discard(source);pool.difference_update(adj[source])
        if len(pool)>candidate_budget:
            priority=set(exploratory)&pool
            rest=sorted(pool-priority,key=lambda n:(-degree[n],n))
            pool=priority|set(rest[:max(0,candidate_budget-len(priority))])
        covered+=len(pool&truth)
        scores={m:[] for m in hits}
        for target in pool:
            shared=adj[source]&adj[target]
            aa=sum(1/math.log(degree[z]) for z in shared if degree[z]>1)
            # KG-derived historical project participation of common partners;
            # log transform and capped contribution to prevent hub dominance.
            contextual=sum(math.log1p(activity[z])/math.log(degree[z])
                           for z in shared if degree[z]>1)
            kg=aa+weight*contextual
            scores["aa"].append((aa,target))
            scores["kg"].append((kg,target))
            scores["cn"].append((len(shared),target))
            scores["ra"].append((sum(1/degree[z] for z in shared if degree[z]>0),target))
            scores["pa"].append((degree[source]*degree[target],target))
        for method in hits:
            top=sorted(scores[method],key=lambda t:(-t[0],t[1]))[:k]
            hits[method]+=sum(n in truth for _,n in top)
    return {"seed":seed,"cutoff":str(cutoff),"horizon":str(horizon),
            "queries":len(sources),"queries_with_observed_positives":query_positive,
            "positive_instances":total,"candidate_coverage":covered/total if total else None,
            "recall_at_k":{m:hits[m]/total if total else None for m in hits}}

def run(folder,archive,seeds=(11,23,37),weights=(0.0,0.25,0.5,1.0),queries=250):
    known,events,projects,memberships=load(folder,archive)
    validation={}
    for w in weights:
        validation[w]=[rank(seed,known,events,projects,memberships,date(2023,12,31),
                            date(2024,12,31),weight=w,query_count=queries) for seed in seeds]
    # Choose on 2024 only; deterministic tie-break favors smaller weights.
    def val_score(w):
        vals=[r["recall_at_k"]["kg"] for r in validation[w] if r["recall_at_k"]["kg"] is not None]
        return statistics.mean(vals) if vals else -1
    chosen=sorted(weights,key=lambda w:(-val_score(w),w))[0]
    testing=[rank(seed,known,events,projects,memberships,date(2024,12,31),
                  date(2025,12,31),weight=chosen,query_count=queries) for seed in seeds]
    return {"method":"KG-context weighted Adamic-Adar versus matched-pool AA, CN, RA and PA",
            "seeds":list(seeds),"query_count":queries,
            "validation_weight_scores":{str(w):val_score(w) for w in weights},
            "chosen_weight":chosen,"validation":validation[chosen],"test":testing,
            "limitations":["Project start date is not historical public-disclosure date.",
                           "KG context uses past co-participation only; no demonstrated algorithmic novelty.",
                           "Future unobserved pairs are unlabeled; observed-positive Recall@10 is not precision.",
                           "Three seed estimates are not independent samples of ecosystems."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=Path("data/processed"))
    p.add_argument("--zip",type=Path,default=Path("data/raw/cordis-HORIZONprojects-csv.zip"))
    p.add_argument("--queries",type=int,default=250)
    a=p.parse_args()
    if a.queries<1:p.error("--queries must be positive")
    result=run(a.data,a.zip,queries=a.queries)
    out=a.data/"kg_model_results.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
