# Integrated research audit and publication gate

This project now automates real-data extraction, structural checks, typed
organization-project graph construction, bounded temporal baselines, a
validation-tuned contextual KG heuristic, and a descriptive multi-seed audit.

**Reproducibility:** Use the official CORDIS archive SHA-256 in the run
manifest. Keep downloaded records out of Git. Archive aggregate results.

**Critical limits not solved by passing CI:**
1. The retrospective archive's project start date is not proof of public
   disclosure by the model cutoff. A strict historical backtest requires
   timestamped snapshots or source records with defensible publication dates.
2. Organization ID consistency and type filtering must be audited before
   describing this as an entrepreneurial ecosystem sample. Current records
   include universities and research institutions.
3. Only three seeded 250-query samples have measured KG-context results so far.
   Seeds overlap on a single network; do not label their dispersion a confidence
   interval or report a p-value.
4. The KG-context score is an interpretable heuristic, not established AI
   novelty. More substantial typed/temporal KG models and ablations are needed.
5. Unobserved collaborations are unlabeled, not verified negatives.
6. Candidate coverage limits Recall@10 and must be shown beside model scores.
7. Do not use the 2025 test split for weight selection or repeated optimization.

**Publication gate:** A draft may be written with exactly two figures and two
editable tables, but must be explicitly marked provisional until point-in-time
availability, robustness, organization identities, and contribution novelty
have been addressed. Never invent missing performance metrics.
