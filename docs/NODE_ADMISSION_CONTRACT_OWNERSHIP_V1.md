# Node Admission Contract Ownership v1

`synergy.node-admission-decision/v1` is produced by `Shtenco/synergy_meta_os`.

The architecture root registers and audits the contract but does not become the producer of admission truth. `synergy_system` may inspect the artifact for federation conformance; it cannot start services, grant capabilities, or reinterpret a blocked admission as deployment approval.

Current v1 semantics are intentionally fail-closed for the Research Compute Node because the linked source build lock has no reproducibly verified build artifact digests.

Future blockchain/control-plane consumers must be registered in later overlays only after those consumers actually exist. This v1 overlay therefore lists only the architecture root as an implemented federation consumer.
