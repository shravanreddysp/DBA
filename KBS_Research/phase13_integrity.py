"""Phase 13: reproducibility and statistical integrity checks.

Descriptive inference only; query organizations share one network.
"""
import hashlib
import json
import math
from pathlib import Path

METHODS=('aa','kg','cn','ra','pa','bp')

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def audit(root):
    model=json.loads((root/'phase11_ranking_results.json').read_text())
    retrieval=json.loads((root/'retrieval_ablation.json').read_text())
    paired=json.loads((root/'phase11_paired_uncertainty.json').read_text())
    manifest=json.loads((root/'manifest.json').read_text())
    checks={}
    checks['validation_selected_retrieval']=model['retrieval_strategy']==retrieval['validation_selected_strategy']
    checks['fixed_candidate_budget']=model['candidate_budget']==retrieval['budget']
    checks['expected_seeds']=sorted(x['seed'] for x in model['test'])==sorted(retrieval['seeds'])
    checks['no_missing_methods']=all(set(x['recall_at_k'])==set(METHODS) for x in model['test'])
    checks['bounded_recall_and_coverage']=all(
        all(isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<=1 for v in x['recall_at_k'].values())
        and x['candidate_coverage'] is not None and 0<=x['candidate_coverage']<=1
        for x in model['test'])
    checks['query_counts']=all(x['queries']==model['test'][0]['queries'] for x in model['test'])
    checks['per_query_counts']=all(len(x['per_query'])==x['queries'] for x in model['test'])
    checks['query_hits_not_exceed_positives']=all(
        0<=q['hits'][m]<=min(10,q['positives']) for x in model['test']
        for q in x['per_query'] for m in METHODS)
    checks['aggregate_hits_match_query_hits']=all(
        abs(sum(q['hits'][m] for q in x['per_query'])/x['positive_instances']-x['recall_at_k'][m])<1e-12
        for x in model['test'] for m in METHODS if x['positive_instances']>0)
    checks['pair_intervals_ordered']=all(
        x['query_resampling_interval_95'][0]<=x['query_resampling_interval_95'][1]
        and math.isfinite(x['delta_observed_positive_recall_at_10']) for x in paired)
    checks['paired_methods_present']=all(x['method'] in METHODS and x['baseline'] in METHODS for x in paired)
    checks['manifest_archive_hash']=len(manifest['archive_sha256'])==64
    output={'phase':13,'passed':all(checks.values()),'checks':checks,
            'retrieval_strategy':model['retrieval_strategy'],
            'validation_selected_weight':model['validation_selected_kg_weight'],
            'file_sha256':{name:digest(root/name) for name in
                           ('manifest.json','retrieval_ablation.json','phase11_ranking_results.json',
                            'phase11_paired_uncertainty.json')},
            'limitations':['These are internal consistency checks, not independent external replication.',
                           'Temporal public-disclosure evidence remains unverified.',
                           'Query bootstrap intervals are descriptive conditional on a single network.',
                           'Observed-positive labels are not verified negatives.']}
    return output

if __name__=='__main__':
    root=Path('data/processed')
    result=audit(root)
    (root/'phase13_integrity_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['passed']:raise SystemExit('Phase 13 integrity checks failed')
