"""Paired query-level bootstrap, conditional on a single CORDIS network."""
import json
import random
from pathlib import Path


def interval(data, baseline, draws=2000, seed=2026):
    unique = {}
    for run in data['test']:
        for q in run['per_query']:
            unique.setdefault(q['query_key'], q)
    rows = [q for q in unique.values() if q['positives'] > 0]
    if not rows:
        raise ValueError('No observed positives')
    def estimate(sample):
        return sum(q['hits']['kg'] - q['hits'][baseline] for q in sample) / sum(q['positives'] for q in sample)
    rng = random.Random(seed)
    values = sorted(estimate(rng.choices(rows, k=len(rows))) for _ in range(draws))
    return {'baseline': baseline, 'kg_minus_baseline': estimate(rows), 'interval_95': [values[int(.025*draws)], values[int(.975*draws)]], 'unique_queries_with_positives': len(rows), 'draws': draws, 'limitation': 'Conditional on observed positive labels and one network; not an independent-ecosystem confidence interval.'}


if __name__ == '__main__':
    data = json.loads(Path('data/processed/kg_model_results.json').read_text())
    result = [interval(data, baseline) for baseline in ('aa', 'cn', 'ra', 'pa')]
    Path('data/processed/paired_uncertainty.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
