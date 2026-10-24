"""Phase 11: evaluate all six rankers on validation-selected retrieval pool.

The retrieval strategy and KG weight are chosen using 2024 validation only.
No 2025 labels influence model or retrieval selection.
"""
import argparse
import json
import statistics
import time
from datetime import date
from pathlib import Path
from kg_model import load, rank

def run(folder,archive,queries=250):
    ablation=json.loads((folder/'retrieval_ablation.json').read_text())
    strategy=ablation['validation_selected_strategy']
    budget=ablation['budget']
    seeds=tuple(ablation['seeds'])
    known,events,projects,memberships=load(folder,archive)
    weights=(0.,.25,.5,1.)
    val={}
    for weight in weights:
        val[weight]=[rank(seed,known,events,projects,memberships,date(2023,12,31),
                          date(2024,12,31),query_count=queries,candidate_budget=budget,
                          weight=weight,retrieval_strategy=strategy) for seed in seeds]
    def score(weight):
        return statistics.mean(r['recall_at_k']['kg'] for r in val[weight])
    chosen=sorted(weights,key=lambda w:(-score(w),w))[0]
    started=time.perf_counter()
    test=[rank(seed,known,events,projects,memberships,date(2024,12,31),
               date(2025,12,31),query_count=queries,candidate_budget=budget,
               weight=chosen,retrieval_strategy=strategy) for seed in seeds]
    elapsed=time.perf_counter()-started
    return {'phase':'11','retrieval_strategy':strategy,'candidate_budget':budget,
            'validation_selected_kg_weight':chosen,
            'validation_kg_weight_scores':{str(w):score(w) for w in weights},
            'validation':val[chosen],'test':test,
            'test_runtime_seconds_total':elapsed,
            'test_mean_observed_positive_recall_at_10':{
                m:statistics.mean(r['recall_at_k'][m] for r in test)
                for m in test[0]['recall_at_k']},
            'limitations':['Retrospective CORDIS metadata cannot establish point-in-time public availability.',
                           'Observed-positive Recall@10 is not precision.',
                           'Seed queries overlap and are not independent ecosystem samples.',
                           'Runtime is environment-dependent and not a controlled speed benchmark.']}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=Path('data/processed'))
    p.add_argument('--zip',type=Path,default=Path('data/raw/cordis-HORIZONprojects-csv.zip'))
    p.add_argument('--queries',type=int,default=250)
    args=p.parse_args()
    result=run(args.data,args.zip,queries=args.queries)
    (args.data/'phase11_ranking_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'retrieval_strategy':result['retrieval_strategy'],
                      'validation_selected_kg_weight':result['validation_selected_kg_weight'],
                      'test_mean_observed_positive_recall_at_10':result['test_mean_observed_positive_recall_at_10'],
                      'test_runtime_seconds_total':result['test_runtime_seconds_total']},indent=2))
