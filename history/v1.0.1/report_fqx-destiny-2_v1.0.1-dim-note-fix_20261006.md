# Fox Armory 2026 Return — v1.0.1 DIM Note Serialization Fix

- Base v1.0 commit: 08063a43baccaf360d7551ffcd51475d50a7fdc4
- Rules audited: **11130**
- v1.0 rules whose notes contained DIM-terminating pipes: **11130**
- v1.0.1 rules whose notes still contain pipes: **0**
- Rule signature changes: **0**
- Semantic note changes beyond delimiter/model-version serialization: **0**
- Firefright full metadata visible through DIM-equivalent parser: **True**
- Candidate SHA-256: bd432eb283dbe9ef30c0940fc1b84634c09e76407e081de4367271b3c844eb34

## Fix

DIM's current wishlist parser captures #notes only until the first pipe character. v1.0 used pipes as metadata separators, causing DIM to display only the first field. v1.0.1 replaces note-field pipes with semicolon separators and bumps score-model:v1.0 to score-model:v1.0.1. Item hashes, positive/negative state, perk lists, scores, classifications, ordering, and coverage remain unchanged.
