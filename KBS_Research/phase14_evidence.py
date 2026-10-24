"""Phase 14 evidence synthesis: mechanically derived, no unsupported claims.

Requires regenerated Phase 10/11/12/13 outputs in data/processed.
"""
import csv
import json
import statistics
from pathlib import Path

ROOT=Path('data/processed')
def read(name):return json.loads((ROOT/name).read_text())
def main():
    integrity=read('phase13_integrity_report.json')
    if not integrity['passed']:raise ValueError('Phase 13 integrity audit did not pass')
    phase11=read('phase11_ranking_results.json')
    phase12=read('phase12_ablation.json')
    retrieval=read('retrieval_ablation.json')
    paired=read('phase11_paired_uncertainty.json')
    manifest=read('manifest.json')
    if phase11['retrieval_strategy']!=retrieval['validation_selected_strategy']:
        raise ValueError('Retrieval selection inconsistent')
    methods=phase11['test_mean_observed_positive_recall_at_10']
    rows=[{'method':k,'observed_positive_recall_at_10':v,
           'percentage':round(100*v,5)} for k,v in sorted(methods.items(),key=lambda x:-x[1])]
    cover=[{'seed':r['seed'],'coverage':r['candidate_coverage'],
            'positive_instances':r['positive_instances']} for r in phase11['test']]
    output={
        'research_scope':'Retrospective warm-start organization collaboration recommendation on CORDIS Horizon Europe.',
        'selection_protocol':'Retrieval strategy and KG-context weight selected on 2024 validation; evaluated on 2025 test.',
        'test_period':'2025',
        'selected_retrieval':phase11['retrieval_strategy'],
        'selected_kg_weight':phase11['validation_selected_kg_weight'],
        'candidate_budget':phase11['candidate_budget'],
        'ranking_table':rows,
        'candidate_coverage_by_seed':cover,
        'mean_candidate_coverage':statistics.mean(r['coverage'] for r in cover),
        'paired_query_resampling':paired,
        'phase12_ablation':phase12['experiments'],
        'phase13_integrity_passed':integrity['passed'],
        'archive_sha256':manifest['archive_sha256'],
        'claims_supported':[
            'Shared-neighbor candidate retrieval increased observed-positive candidate coverage relative to the original candidate-generation procedure.',
            'KG-context did not show a clear advantage over AA, CN, or RA under the conditional query-resampling comparisons.',
            'Greater candidate coverage did not necessarily increase observed-positive Recall@10.'],
        'claims_not_supported':[
            'Demonstrated superiority of the KG method over strong classical graph baselines.',
            'Causal effects on digital transformation, entrepreneurship, or innovation success.',
            'Point-in-time public availability of CORDIS metadata.',
            'Independent ecosystem generalization or valid precision against confirmed negative labels.',
            'Novel knowledge-graph learning algorithm demonstrated by current heuristics.'],
        'manuscript_recommendation':'Narrow title and claims to a retrospective study of collaboration recommendation and candidate retrieval in European research networks; additional evidence required for broad entrepreneurial innovation claims.',
        'limitations':integrity['limitations']}
    (ROOT/'phase14_evidence_package.json').write_text(json.dumps(output,indent=2)+'\n')
    with (ROOT/'phase14_table_ranking.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (ROOT/'phase14_figure_coverage.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(cover[0]));writer.writeheader();writer.writerows(cover)
    print(json.dumps({'methods':rows,'coverage':output['mean_candidate_coverage'],
                      'phase13_passed':True,'claims_not_supported':output['claims_not_supported']},indent=2))

if __name__=='__main__':main()
