# Phase 7: paired query-level evaluation

The model now exports hashed query keys, observed-positive counts, and paired hits for five ranking methods. Query keys can be deduplicated across overlapping seeded samples. A bootstrap should resample unique query organizations and recompute the pooled difference in observed-positive Recall@10. This interval is conditional on the single CORDIS network and does not establish generalization or eliminate retrospective information leakage.

Do not report significance from three overlapping seed averages. Do not interpret unobserved collaborations as confirmed negatives.
