"""Descriptive paired query-resampling intervals for Phase 11 methods.

Resamples unique query organizations, not independent ecosystems.
"""
import json
import random
from pathlib import Path

def paired(data, method, baseline, draws=2000, seed=2026):
    unique={}
    for run in data['test']:
        for q in run['per_query']:
            unique.setdefault(q['query_key'],q)
    rows=[q for q in unique.values() if q['positives']>0]
    if not rows:raise ValueError('No observed positive queries')
    def estimate(sample):
        return sum(q['hits'][method]-q['hits'][baseline] for q in sample)/sum(q['positives'] for q in sample)
    rng=random.Random(seed)
    vals=sorted(estimate(rng.choices(rows,k=len(rows))) for _ in range(draws))
    return {'method':method,'baseline':baseline,'delta_observed_positive_recall_at_10':estimate(rows),
            'query_resampling_interval_95':[vals[int(.025*draws)],vals[int(.975*draws)]],
            'unique_queries_with_positives':len(rows),'draws':draws,
            'interpretation':'Descriptive conditional query bootstrap; overlapping seed queries and a single network prevent independent ecosystem inference.'}

if __name__=='__main__':
    root=Path('data/processed')
    data=json.loads((root/'phase11_ranking_results.json').read_text())
    comparisons=[('kg',m) for m in ('aa','cn','ra','pa','bp')]
    comparisons += [('ra',m) for m in ('aa','cn','bp')]
    result=[paired(data,a,b) for a,b in comparisons]
    (root/'phase11_paired_uncertainty.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
