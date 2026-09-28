# M4 Wave 5 — App Source Evidence

Wave 5 intentionally integrates only two app repositories whose current main exposes reproducible source surfaces:

```text
synergy_app ────────→ Meta-OS
sinergy_super_app ──→ Meta-OS
```

The contracts prove source/configuration state only. They do **not** claim that an APK/AAB/IPA was built, store moderation passed, or a release was deployed.

`synergy_messenger` is deliberately excluded from this wave: its current package.json references script/test paths absent from the current main while RELEASE-MANIFEST.json claims a completed 249/249 test gate. That evidence mismatch must be repaired before federation promotion.
