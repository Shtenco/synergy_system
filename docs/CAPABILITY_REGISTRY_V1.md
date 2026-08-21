# SYNERGY capability registry v1

`synergy.capability-registry/v1` replaces hard-coded future capability expansion with an immutable architecture artifact.

The registry defines operational capabilities and service kinds only. A capability permits a node manifest to request an operational role; it does **not** grant accounting, payment, settlement, trading execution, scientific-truth, or other domain authority.

Canonical v1 digest:

`3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913`

New roles introduced by this generation include `SCIENCE_RESEARCH` / `SCIENCE_AGENT` and `MIDAS_ANALYSIS` / `MIDAS`.

`synergy.node-manifest/v1` remains preserved with its historical hard-coded taxonomy. A future Meta-OS manifest generation must pin this exact registry digest and validate capabilities/service kinds from registry bytes.

Changing the capability taxonomy requires a new registry generation. Editing v1 in place is forbidden by project policy.
