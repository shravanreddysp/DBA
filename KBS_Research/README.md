# Knowledge-Based Systems research — reproducibility

**Phase 1:** Real public CORDIS Horizon Europe collaboration-data preparation added. See [DATASET.md](DATASET.md) for provenance, reuse conditions, temporal design, and limitations.

```bash
python -m unittest test_prepare_cordis.py
python prepare_cordis.py
```

The preparation script downloads an official CSV ZIP (or accepts `--zip`), constructs observed organization collaboration labels, and writes an archive-hash manifest locally. **The full official download and extraction have not yet been executed or verified in this environment.** Raw/processed records are ignored by Git.

The existing `experiment.py` is a **separate social-network feasibility benchmark**, not a trained model on CORDIS. Do not interpret its results as entrepreneurial ecosystem evidence.

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
