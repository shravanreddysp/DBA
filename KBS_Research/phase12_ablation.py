"""Phase 12: controlled KG-context feature and retrieval-budget ablation.

This is a bounded sensitivity analysis, not an independent replication.
For each budget, weight is selected using 2024 validation only.
"""
import argparse
import json
import statistics
import time
from datetime import date
from pathlib import Path
from kg_model import load, rank

def run(folder,archive,queries=75,seeds=(11,23),budgets=(1000,2250),weights=(0.,1.)):
    ablation=json.loads((folder/'retrieval_ablation.json').read_text())
    strategy=ablation['validation_selected_strategy']
    known,events,projects,memberships=load(folder,archive)
    result={'phase':12,'strategy':strategy,'seeds':list(seeds),'queries_per_seed':queries,
            'budgets':list(budgets),'weights':list(weights),'experiments':[],
            'limitations':['Bounded sensitivity analysis using overlapping organizations from one retrospective CORDIS network.',
                           'Project metadata public availability at historical cutoffs is unverified.',
                           'Weight zero is the no-context Adamic-Adar ablation; weight one adds historical project-participation context.',
                           'Budget varies, so ranking results across budgets do not use identical candidate pools.']}
    for budget in budgets:
        start=time.perf_counter()
        validation={str(w):[rank(seed,known,events,projects,memberships,date(2023,12,31),
                               date(2024,12,31),query_count=queries,candidate_budget=budget,
                               weight=w,retrieval_strategy=strategy) for seed in seeds] for w in weights}
        def mean_kg(w):
            return statistics.mean(x['recall_at_k']['kg'] for x in validation[str(w)])
        selected=sorted(weights,key=lambda w:(-mean_kg(w),w))[0]
        # Test each feature setting for transparent ablation; selection uses validation only.
        test={str(w):[rank(seed,known,events,projects,memberships,date(2024,12,31),
                          date(2025,12,31),query_count=queries,candidate_budget=budget,
                          weight=w,retrieval_strategy=strategy) for seed in seeds] for w in weights}
        result['experiments'].append({
            'budget':budget,'selected_weight_on_validation':selected,
            'validation_mean_kg_recall_at_10':{str(w):mean_kg(w) for w in weights},
            'test_mean_kg_recall_at_10':{str(w):statistics.mean(x['recall_at_k']['kg'] for x in test[str(w)]) for w in weights},
            'test_mean_coverage':{str(w):statistics.mean(x['candidate_coverage'] for x in test[str(w)]) for w in weights},
            'test_mean_baseline_recall_at_10':{m:statistics.mean(x['recall_at_k'][m] for x in test[str(selected)])
                                              for m in ('aa','cn','ra','pa','bp')},
            'elapsed_seconds':time.perf_counter()-start})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=Path('data/processed'))
    p.add_argument('--zip',type=Path,default=Path('data/raw/cordis-HORIZONprojects-csv.zip'))
    p.add_argument('--queries',type=int,default=75)
    args=p.parse_args()
    if args.queries<1:p.error('queries must be positive')
    result=run(args.data,args.zip,queries=args.queries)
    (args.data/'phase12_ablation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
