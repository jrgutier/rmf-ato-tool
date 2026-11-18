---
interview_id: INT-093
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [baseline configuration, configuration settings, inventory]
---
# INT-093 — S-4 — PER-ISSE

### Q1 {#INT-093.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-2, cm-6
What is the baseline configuration, and how are secure settings set and checked on each
component?
**A1 {#INT-093.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/test-results.md#stig-scan]] [[product/test-results.md#pipeline-1-5]]
> The baseline is the version-controlled infrastructure templates plus the release manifest of
> image digests: edge and WAF settings (CMP-EDGE), node groups and workloads (CMP-K8S) and the
> database parameters (CMP-DB). Only the pipeline deploys it, and the hourly drift scan reports
> manual changes to the ISSO. We review the baseline at every release and at least annually.
> Settings come from the Kubernetes STIG on the provider's hardened node image, the factory's
> hardened base images, and the PostgreSQL STIG as far as a managed service allows. The 2026-10-22
> scan: nodes 94% compliant, the open items being provider-managed control plane checks marked
> inherited; the database 88%, six open items, four not configurable on the managed service and
> marked inherited, two ours (connection logging verbosity and password complexity for the local
> break-glass database role), fixed in release 1.5.2, planned 2026-12-10. The inherited items are
> deviations the ISSM approves in the STIG summary.

### Q2 {#INT-093.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-8
How is the component inventory kept?
**A2 {#INT-093.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[ART-INV]]
> The inventory is the INV-### list in the program's inventory record, one entry per item with
> its component, supplier, product, version, quantity and criticality, with no item counted twice
> or belonging to another system. The release pipeline flags any new image or managed service not
> in it, and the ISSO and I review it monthly and at every release.
