# Research Node Build Lock v1 — review checklist

A reviewer should verify all of the following before any future promotion:

- profile digest matches the canonical RESEARCH_COMPUTE_NODE profile;
- every component repository is an allowed service repository from that profile;
- every source commit is immutable and reviewable;
- every source-tree digest matches the intended source generation;
- source-candidate status is not confused with build verification;
- `build_artifact_digest` remains null until a reproducible build actually exists;
- build verification, when introduced, is a new generation with independent evidence;
- no financial, payment, accounting or execution authority is introduced by the build lock.
