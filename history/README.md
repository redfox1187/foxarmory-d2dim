# Fox Armory 2026 Return — version provenance

This directory records the 2026 Return wishlist development lineage.

The v0.6-v0.8 candidates were generated on the experimental branch during 2026-10-06 work and have been pinned to archival branches at their real generator commits. v0.9 was generated and verified locally from the same source lineage, then preserved in the FQX Destiny Cabinet; it did not exist as a Git commit at the moment it was produced, so it is documented as a reconstruction rather than backdated.

## Provenance table

| Version | Status | Generator / provenance | Cabinet artifact | Wishlist SHA-256 |
| --- | --- | --- | --- | --- |
| v0.6 | reconstructed candidate history | archive/v0.6-generation @ 0fffbf62127d1f85f704fb9fe2c2f2e056e5d74e | fqx-d2dim-v0.6-candidate_20261006.zip | ee695401f2b6059aba4f9c80ecaf307b2dcbbb968a01f87052ab35e6779611a8 |
| v0.7 | reconstructed candidate history | archive/v0.7-generation @ 50ee23224eb3e89156f28be8347acd1bce9a9007 | fqx-d2dim-v0.7-candidate_20261006.zip | 6b87964c1adf75da5a3316efcc465cdc9790743fb5f9fe610e659ad92674272a |
| v0.8 | verified candidate history | archive/v0.8-generation @ 44d76226b24e57e76259d7c3a28c31d897a50a80 | fqx-d2dim-v0.8-candidate-verified_20261006.zip | af64b603fc102da99a0267ed3801a5d1c32e5c0e0dbdf95aa07b14c115434d51 |
| v0.9 | verified local reconstruction | archive/v0.9-reconstructed @ fed6268bd173bea147eb3aeb98c284308c953c4d; no original generation commit | fqx-d2dim-v0.9-candidate-verified_20261006.zip | 6946bca3a0ff814f5467e5a4b892ae391701f1e837d947072cf7fec944e40c14 |
| v1.0 | repository-native live release | master merge edcc4f45e3b1b254d6b72438163d71ac9d526b20; generator release branch release/v1.0-20261006 | generated in-repo; release report + ledgers committed | f5777a63475477a31d681711fb27bbf2306aaa5fc81dc168d4fc0bbd13a7cb6d |

## Reconstruction policy

Historical records added after the fact must say so explicitly. Do not rewrite Git history or create fake backdated commits. Cabinet artifacts and checksums remain the authoritative byte-level provenance for candidates that were not committed at generation time.

v1.0 is the first repository-native, fully audited live release in this lineage. Its generator is pinned to the immutable v0.5.2 production baseline so reruns do not recursively consume prior generated output.
