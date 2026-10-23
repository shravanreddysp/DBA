# Phase 5 — outcome-independent candidate exploration

The initial real-data evaluation selected only organizations with observed future
collaborations and then chose the first 250 sorted IDs. That was not a valid
representative query cohort. The updated `scalable_baselines.py` corrects
this by selecting a deterministic pseudo-random sample from **all organizations
known by the training cutoff**, before consulting future outcomes.

Candidate generation now adds 250 source-specific hash-selected exploratory
organizations to the graph-derived two-hop and high-degree candidates.
This can discover some links outside the existing collaboration neighborhood.
Results report candidate coverage, mean candidate count, and observed-positive
Recall@10. All unobserved pairs remain **unlabeled**.

The fixed 2023 known-organization population is the evaluation frame for both
2024 and 2025; no newly arriving organizations are included. This is a
warm-start benchmark. Query sampling is independent of outcomes, but the
measured cohort remains small (250 organizations) and uncertain. Repeated
seeds and larger cohorts are needed for confidence intervals and robustness.

Run locally after downloading the CORDIS archive:

```bash
python -m unittest -v test_scalable_baselines.py
python scalable_baselines.py --k 10 --max-queries 250 --max-twohop 2000 --random-candidates 250 --seed 2026
```

The GitHub real-data workflow runs this script and uploads
`scalable_baseline_results.json` as an artifact. Results from previous
versions are **not directly comparable**, because query selection and
candidate generation changed.

**Important:** This is still a graph-heuristic baseline, not a novel KG AI
model. A fully point-in-time-valid study requires timestamped public release
snapshots. Organization entity resolution, selection bias from project-size
filtering, and future label incompleteness must be audited before publication.
