# Node-profile consumer boundary

`synergy.node-profile/v1` is produced by `Shtenco/synergy_system` and consumed by `Shtenco/synergy_meta_os`.

The consumer must not reinterpret the profile as a signed node identity, process execution request, financial authorization, payment authorization, or accounting fact.

Required separation:

1. verify profile bytes and digest;
2. verify signed Meta-OS node manifest independently;
3. verify manifest capabilities/services are a subset/exact match required by the selected profile;
4. preserve all profile authority fields as `NONE`;
5. only after profile conformance may Meta-OS continue its existing artifact/lifecycle readiness checks.

A valid manifest signature with forbidden capabilities is `SIGNED_BUT_PROFILE_NONCONFORMANT`.
