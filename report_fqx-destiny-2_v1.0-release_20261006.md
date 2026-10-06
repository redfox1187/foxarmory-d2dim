# Fox Armory 2026 Return — v1.0 Release Report

**Status:** full-catalog release candidate generated on `release/v1.0-full-catalog-20261006`
**Manifest:** 244213.26.06.29.2000-1-bnet.65864

## Scope

v1.0 treats current-manifest weapon definitions as a conservative superset. Manifest presence is not proof that a historical definition is currently obtainable. The release deliberately over-covers the manifest so an actually droppable weapon cannot be omitted merely because its source metadata is stale.

- Roll-bearing Legendary definitions: **1657**
- Fixed Legendary definitions: **256**
- Exotic definitions: **146**
- Low-tier weapon definitions explicitly rated: **149**

## Personalization

Favorite exact rolls remain highest-priority personal-positive rules. The general profile governs weapon-family preference, maintenance/uptime, and direct perk-pair evidence. Hunter-specific survivability/ability preferences remain buildcrafting evidence and do not indiscriminately inflate weapon scores.

Newly generated definitions use type priors plus smoothed perk and pair residuals learned from the curated positive catalogue. Fox profile adjustments are then applied. These are explicitly Estimated scores. Manifest-only inference is confidence-capped: source-indicated definitions cannot exceed 92E and availability-unverified definitions cannot exceed 86E without stronger evidence.

No community score is fabricated. Generated rules use `CPVE:NA` / `CPVP:NA`.

## Completeness

- Missing roll-bearing Legendary hashes after build: **0**
- Missing Legendary fallbacks: **0**
- Missing fixed Legendary hashes: **0**
- Missing Exotic hashes: **0**
- Missing low-tier weapon hashes: **0**

## Integrity

- Favorite failures: **0**
- Ordering failures: **0**
- Community-preservation failures: **0**
- Existing-production PvP preservation failures: **0**
- Generated community-value failures: **0**
- Malformed rules: **0**
- Duplicate exact signatures: **0**

## Version-history note

v0.6-v0.8 are pinned to their actual generator commits on archival branches. v0.9 was produced locally and is documented as a reconstruction rather than backdated. v1.0 is the first repository-native complete release candidate in this new lineage.
