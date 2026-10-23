# Real CORDIS data validation via GitHub Actions

The repository has a separate **KBS CORDIS real-data validation** workflow.
It downloads the official CORDIS Horizon Europe CSV ZIP, extracts organization
collaboration labels, validates exported dates and disjoint cohorts, and
publishes a SHA-256 source-archive fingerprint plus aggregate record counts in
the GitHub Actions run summary. It does **not** upload the source ZIP or
organization-level records.

## Run

In GitHub select **Actions → KBS CORDIS real-data validation → Run workflow**.
The workflow is also scheduled monthly. A green result is evidence that
the extraction and structural checks completed on a live archive. Review the
run summary and attached manifest to determine counts and exact source version.

## What a green run does NOT prove

- That the records were publicly available before their project start dates
- That entity IDs perfectly resolve real-world organizations
- That unobserved organization pairs are confirmed negative outcomes
- That the complete baseline experiment scaled or yielded strong results
- That an entrepreneurship-specific AI method is novel or validated

The graph-only baseline script has a conservative candidate-size guard.
Do not remove it merely to claim successful execution.

If the official download fails or the archive schema differs, inspect the
failed job logs, update the parser against the documented official schema, and
rerun. Never report invented data counts or performance statistics.
