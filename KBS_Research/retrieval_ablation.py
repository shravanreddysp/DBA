"""Controlled candidate-retrieval ablation on retrospective CORDIS labels.

No future labels are used to select candidates. All strategies have the same
maximum budget. Validation is reported separately from held-out 2025 test.
"""
import argparse
import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path
from kg_model import load, snapshot, stable

SEEDS=(11,23,37)
BUDGET=2250
QUERY_COUNT=250

def candidates(source,known,adj,degree,seed,strategy,budget=BUDGET):
    eligible=set(known)-adj[source]-{source}
    hubs=sorted(eligible,key=lambda n:(-degree[n],n))[:100]
    randoms=sorted(eligible,key=lambda n:(stable(seed,'explore',source,n),n))
    twohop=set()
    for z in adj[source]:
        twohop.update(adj[z])
    twohop &= eligible
    # Deterministic ranking; budget is applied identically to every strategy.
    by_degree=sorted(twohop,key=lambda n:(-degree[n],n))
    by_shared=sorted(twohop,key=lambda n:(-len(adj[source]&adj[n]),-degree[n],n))
    by_resource=sorted(twohop,key=lambda n:(-sum(1/degree[z] for z in adj[source]&adj[n] if degree[z]),-degree[n],n))
    def unique(seq):
        seen=set()
        for n in seq:
            if n not in seen:
                seen.add(n)
                yield n
    if strategy=='degree_twohop':
        ordering=unique(hubs+by_degree+randoms)
    elif strategy=='shared_twohop':
        ordering=unique(hubs+by_shared+randoms)
    elif strategy=='resource_twohop':
        ordering=unique(hubs+by_resource+randoms)
    elif strategy=='random':
        ordering=unique(randoms)
    elif strategy=='degree_global':
        ordering=unique(sorted(eligible,key=lambda n:(-degree[n],n)))
    else:
        raise ValueError(strategy)
    result=set()
    for n in ordering:
        result.add(n)
        if len(result)>=budget:break
    return result

def evaluate(known,events,projects,memberships,cutoff,horizon,seed,strategies,budget,queries):
    adj,_=snapshot(known,events,projects,memberships,cutoff)
    degree={n:len(adj[n]) for n in known}
    future=defaultdict(set)
    for a,b,d in events:
        if cutoff<d<=horizon:
            future[a].add(b);future[b].add(a)
    sources=sorted(known,key=lambda n:(stable(seed,'query',n),n))[:queries]
    results={s:{'hits':0,'positives':0,'candidate_count':0,'queries_with_positives':0} for s in strategies}
    for source in sources:
        truth=future[source]
        for strategy in strategies:
            row=results[strategy]
            pool=candidates(source,known,adj,degree,seed,strategy,budget)
            row['hits']+=len(pool&truth)
            row['positives']+=len(truth)
            row['candidate_count']+=len(pool)
            row['queries_with_positives']+=bool(truth)
    for row in results.values():
        row['coverage']=row['hits']/row['positives'] if row['positives'] else None
        row['mean_candidate_count']=row['candidate_count']/len(sources) if sources else 0
    return results

def run(folder,archive,seeds=SEEDS,budget=BUDGET,queries=QUERY_COUNT):
    known,events,projects,memberships=load(folder,archive)
    strategies=('degree_twohop','shared_twohop','resource_twohop','random','degree_global')
    splits={'validation':(date(2023,12,31),date(2024,12,31)),
            'test':(date(2024,12,31),date(2025,12,31))}
    output={'budget':budget,'query_count':queries,'seeds':list(seeds),
            'strategies':list(strategies),
            'evaluation':{},'limitations':[
                'Retrospective CORDIS data do not verify point-in-time public disclosure.',
                'Candidate coverage is recall of observed positives, not classification precision.',
                'Seed samples overlap; results are not independent ecosystems.',
                'Strategies use a common maximum candidate count, not identical runtime.']}
    for split,(cutoff,horizon) in splits.items():
        output['evaluation'][split]=[
            {'seed':seed,'strategies':evaluate(known,events,projects,memberships,cutoff,horizon,seed,strategies,budget,queries)}
            for seed in seeds]
    val=output['evaluation']['validation']
    output['validation_mean_coverage']={
        strategy:statistics.mean(r['strategies'][strategy]['coverage'] for r in val if r['strategies'][strategy]['coverage'] is not None)
        for strategy in strategies}
    output['validation_selected_strategy']=sorted(strategies,key=lambda s:(-output['validation_mean_coverage'][s],s))[0]
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=Path('data/processed'))
    p.add_argument('--zip',type=Path,default=Path('data/raw/cordis-HORIZONprojects-csv.zip'))
    p.add_argument('--budget',type=int,default=BUDGET)
    p.add_argument('--queries',type=int,default=QUERY_COUNT)
    args=p.parse_args()
    if args.budget<1 or args.queries<1:p.error('budget and queries must be positive')
    result=run(args.data,args.zip,budget=args.budget,queries=args.queries)
    output=args.data/'retrieval_ablation.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'validation_mean_coverage':result['validation_mean_coverage'],
                      'validation_selected_strategy':result['validation_selected_strategy'],
                      'test':result['evaluation']['test']},indent=2))
