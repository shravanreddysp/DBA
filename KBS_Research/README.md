# KBS short-communication reproducibility package

**Status: feasibility study, not submission-ready.** The real public dataset is Zachary's observed karate-club social network distributed with NetworkX; it is **not** entrepreneurial ecosystem data. Results cannot establish entrepreneurial innovation impact or novel state-of-the-art AI.

## Reproduce

```bash
python -m pip install -r requirements.txt
python experiment.py
```

This writes `results.csv`, `summary.json`, `Figure_1.png`, and `Figure_2.png`. The Word manuscript includes exactly two editable tables and references the two figures. All 30 split seeds are deterministic. There is no data download or credential requirement.

## Experiment design

Observed karate-club graph: 34 nodes, 78 edges. For each seed, 16 true edges are removed while preserving connectivity; 16 nonedges from the original graph are sampled as negative examples. Five transparent link scores are evaluated without label tuning. The hybrid's coefficients are illustrative, not learned. Results are a limited transductive edge-discrimination benchmark. The 30 resamples share one network and are not independent populations.

## Before journal submission

Replace the proxy with independently labeled, real entrepreneurial ecosystem data; introduce a typed knowledge graph and substantively new algorithm; compare modern, tuned baselines and time-aware splits; verify all citations, authorship, conflicts, funding, and required AI declaration; obtain persistent archive DOI.
