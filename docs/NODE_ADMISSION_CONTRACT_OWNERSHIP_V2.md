# Node Admission Contract Ownership v2

`synergy.node-admission-decision/v2` is produced only by `Shtenco/synergy_meta_os` after independently evaluating signed node-manifest v2 bytes, capability-registry bytes, the exact node profile and the pinned build-lock generation.

`Shtenco/synergy_system` is an architecture/audit consumer only. It may register and inspect admission artifacts but cannot create deployment truth, start services, grant capabilities, or reinterpret a blocked admission as approval.

The current Science Node v2 decision is fail-closed because its linked build lock contains source identity but no reproducibly verified build artifacts. Future admitted/deployable semantics require a later admission generation and must not reinterpret v2.
