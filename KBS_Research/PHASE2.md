# Phase 2 — temporal collaboration baselines

## Run

```bash
python -m unittest -v test_prepare_cordis.py test_temporal_baselines.py
python prepare_cordis.py
python validate_cordis.py
python temporal_baselines.py --k 10
```

Baseline methods: common neighbors, Adamic–Adar, resource allocation, preferential attachment. Metrics are observed-positive macro and micro Recall@K. They are NOT verified precision because missing CORDIS collaborations are unlabeled.

2024 validation uses the graph through 2023-12-31. 2025 testing uses the graph through 2024-12-31; validation-year links are censored from 2025 candidates. Only organizations known by the initial training cutoff are eligible.

**Scaling:** The script refuses candidate universes exceeding 2,000,000 directed pairs by default; no silent candidate sampling. Large CORDIS data requires a prespecified defensible cohort or scalable exact candidate generation. Do not simply increase the limit.

**Research limitations:** The monthly retrospective CORDIS archive does not establish historical public availability of records; dates are project start dates. No strict point-in-time claim is warranted without dated snapshots. Co-participation is not entrepreneurship success. These are graph-only baselines, not a typed knowledge-graph AI contribution. No real CORDIS predictive results have been produced or validated in this environment.
