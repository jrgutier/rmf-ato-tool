---
interview_id: INT-023
run_id: 20261118-synthetic-01
task: P-10
persona: PER-DEV
date: 2026-11-18
topics: [installed items, versions, components, unlisted items, instances]
---
# INT-023 — P-10 — PER-DEV

### Q1 {#INT-023.Q1}
Asked of: PER-DEV · Task: P-10
**A1 {#INT-023.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#components]]
> The list in the hardware and software file is complete for production: INV-001 to INV-016.
> The five containers we build (efras-web, efras-api, efras-ingest, efras-forecast,
> efras-report) are all at release 1.5.0 and run on CMP-WEB, CMP-API, CMP-INGEST, CMP-FORECAST
> and CMP-REPORT. Every container is built on the software factory's sf-base-minimal 2026.09
> image (INV-007). The cluster is managed Kubernetes 1.33 (INV-008) with worker nodes on the
> provider's hardened node image 2026.10 (INV-009). The database is managed PostgreSQL 16.4
> (INV-010). Object storage, keys and secrets, the log service and the notebooks are provider
> services that the program configures; their versions are provider-managed.

### Q2 {#INT-023.Q2}
Asked of: PER-DEV · Task: P-10
**A2 {#INT-023.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/conops.md#limitations]]
> Two open-source libraries are tracked as their own items because they matter for risk:
> example-imagelib 2.9.1 inside efras-report (INV-015), which carries the two high-severity
> vulnerabilities waiting on the release 1.5.2 base image, and the example web framework 4.2
> runtime inside efras-api (INV-016). The other open-source dependencies are listed in each
> container's software bill of materials that the software factory pipeline produces; they are
> not separate inventory items.

### Q3 {#INT-023.Q3}
Asked of: PER-DEV · Task: P-10
**A3 {#INT-023.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#physical]] [[product/hw-sw-inventory.md#top]]
> There is no program-owned hardware or firmware in the boundary. The servers, disks and their
> firmware are the cloud provider's and are inherited from its IL4 provisional authorization.
> The ERST privileged access workstations are government-furnished equipment on the Component's
> own workstation inventory, not part of EFRAS.

### Q4 {#INT-023.Q4}
Asked of: PER-DEV · Task: P-10
**A4 {#INT-023.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#updates]]
> The quantities in the list are running instances, not separate configuration items. The
> six worker nodes are created from one node image and replaced on every monthly roll; the
> container replicas are copies of one signed image; the database standby is provider-managed.
> We control and version the image or the service configuration, so each line is one
> configuration item. The provider's console shows the current node instances if an assessor
> needs them.

### Q5 {#INT-023.Q5}
Asked of: PER-DEV · Task: P-10
**A5 {#INT-023.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#hostnames]] [[product/architecture.md#network]]
> Only the edge has a published name, efras.example.mil, reachable through the access point.
> The nodes and services use private addresses in the three subnet tiers. Each container image
> and infrastructure template carries the pipeline's signature and a software bill of materials;
> the software factory gives a secure development attestation for its pipeline, and ERST signs
> one for our own code at each release.
