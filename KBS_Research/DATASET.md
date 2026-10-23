# Phase 1 — CORDIS data provenance and temporal protocol

## Selected source

European Commission / Publications Office of the EU, CORDIS Horizon Europe project data (2021–2027), dataset DOI: https://doi.org/10.2906/112117098108/20

- Official catalog: https://data.europa.eu/data/datasets/cordis-eu-research-projects-under-horizon-europe-2021-2027
- Bulk CSV ZIP: https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip
- Source service: https://cordis.europa.eu/about/services
- Reuse notice: https://cordis.europa.eu/about/legal/en

CORDIS publishes projects and participating organizations in downloadable bulk archives. The EU-owned editorial content is generally reusable under CC BY 4.0 with attribution and notice of changes; third-party and beneficiary contributions can have separate rights. **License applicability to every field and downstream redistributed dataset must be checked before distributing raw data.** Our repository stores no raw records. Cite the EU and dataset DOI in publications.

## Research target and scope

Predict first observed **organization–organization co-participation** in an EU-funded research-and-innovation project. This is an observable collaboration proxy, **not** a measurement of startup success, technological adoption, or digital-transformation outcomes. Participants include businesses, universities, and other institutions. A future entrepreneurship-focused subset requires documented organization-type filtering.

Each undirected organization pair receives the date of the earliest *project start* at which both appear as participants. Duplicate pairs and projects are collapsed. A project with more than 60 participating organizations is excluded by default to avoid extreme pair expansion; this introduces selection bias and must be disclosed.

## Temporal evaluation design

- Training cutoff: 2023-12-31.
- Validation events: first collaboration during 2024.
- Test events: first collaboration during 2025.
- Only organizations participating by the training cutoff are eligible (warm-start task).
- The training graph contains first collaborations dated on/before the cutoff.
- For 2024 ranking, remove previously linked pairs; only information available by 2023-12-31 may be used.
- For 2025 ranking, build an updated graph as of 2024-12-31 and remove all pairs previously linked by then. **Do not treat 2024 positives as 2025 negatives.**
- Candidate pairs not observed in CORDIS are **unlabeled**, not confirmed negatives. Use appropriately qualified observed-positive retrieval or positive-unlabeled evaluation; avoid interpreting ordinary ROC AUC with assumed true negatives as definitive.
- The archive is a current retrospective snapshot. Its start dates do not establish that a project was publicly announced on its start date. **Strict point-in-time availability requires archived dated snapshots or independently timestamped disclosure records.** This limitation prevents calling the present pipeline fully leakage-free.

## Commands

```bash
python -m unittest test_prepare_cordis.py
python prepare_cordis.py
# Or use a previously downloaded official archive:
python prepare_cordis.py --zip /path/to/cordis-HORIZONprojects-csv.zip
```

Output under `data/processed/`: training edges, validation/test observed positives, known organization IDs, and a manifest containing archive SHA-256 and record counts. The script does not train a model or report predictive performance. Check the source archive schema before treating output as validated.

## Data handling

Raw CORDIS archives and derived rows remain local and are excluded from Git. For auditability, publish archive hash, extraction date, exact command, counts, schema mapping, and code version. Do not publish personal contacts, emails, or project free text. This is a research pipeline prototype pending a successful run on the official archive and manual schema validation.
