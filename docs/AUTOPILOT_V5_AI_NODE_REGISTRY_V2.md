# AUTOPILOT V5 AI Node Registry v2 — LAB execution bound

Registry v2 is an additive successor to registry v1. It replaces the former `Meta-OS pending / SynergyNet pending` view with exact cross-repository bindings and the executed LAB deployment evidence.

## Canonical candidate

- AUTOPILOT owner: `Shtenco/agi_autopilot`
- candidate commit: `c39f6f0ee0e37c08366a63ec160c580b9ae954ba`
- integration root: `a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54`
- exact NEXUS: `e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325`
- exact SynergyNet: `7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7`

## Cross-domain bindings

- SynergyNet binding: `3c8198e10863c52c0492ca422c404a1e05e6fd2f48f4c393587d9d87eee3855f`
- Meta-OS Profile v2: `6a84a2dd132823756c9f159b04584ac384dca9514316b3ff5c9f4ce06e1696d3`
- Meta-OS Admission v2: `4d3502dba28745b8a734c082ca0260cbbfd4ead11a1396537434844df9987ee3`
- LAB HostProfile: `36a9092977e360b56fd7d1e21b4504f1215ed741df6f492b3ed37b79649573bb`
- LAB SupervisorConfig: `74797e02e0bb32722bbfffb76af42bb00d495fb3a5c0ea4a5b48a4e1d4275879`
- LAB DeploymentEvidence: `8e1b05dca7e349d57e1908dca717d2c1d451ca79adde5cfe539e9e46f83d052b`
- LAB DeploymentResult: `011c3ce24cfd33dc99fbdea0ea2f5dcd344deefd927f57c1b9c1fa3e3eaa3833`

Registry v2 root: `12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d`.

## Exact state semantics

The LAB had a captured `RUNNING_VERIFIED` snapshot, then all processes were stopped gracefully. Therefore registry v2 deliberately records `current_running=false` and `STOPPED_AFTER_VERIFICATION`.

Production remains blocked by a persistent production host, production supervisor and fresh production deployment evidence. The verifier rejects attempts to relabel the LAB snapshot as current/production running or to grant NEXUS/network/financial/payment/accounting/blockchain/execution authority.
