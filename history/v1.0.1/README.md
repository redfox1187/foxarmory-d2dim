# v1.0.1 — DIM-safe wishlist note serialization

**Status:** release candidate
**Date:** 2026-10-06
**Base v1.0 commit:** 08063a43baccaf360d7551ffcd51475d50a7fdc4
**Wishlist SHA-256:** bd432eb283dbe9ef30c0940fc1b84634c09e76407e081de4367271b3c844eb34

v1.0.1 is a serialization-only maintenance release. DIM's current wishlist parser stops #notes text at the first pipe character. v1.0 used pipes between metadata fields, so the UI exposed only the first field. v1.0.1 replaces note-field pipes with semicolons and updates score-model:v1.0 to score-model:v1.0.1.

Item hashes, positive/negative state, perk lists, scores, classifications, ordering, and catalog coverage are unchanged from v1.0.
