---
interview_id: INT-024
run_id: 20261118-synthetic-01
task: P-10
persona: PER-PM
date: 2026-11-18
topics: [asset priority, planned items, asset management system, high-value asset]
---
# INT-024 — P-10 — PER-PM

### Q1 {#INT-024.Q1}
Asked of: PER-PM · Task: P-10
**A1 {#INT-024.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#priority]] [[product/conops.md#mission]] [[ART-BIA]]
> I accept the priority in our inventory list. The data path ranks highest: the readiness API,
> the ingest worker, the database, object storage and the keys hold or move the maintenance data
> and the maintainers' personal data, and the edge is the only way in. The cluster platform is
> high because everything runs on it. The web front end and forecasting are moderate: losing
> them delays reporting, which the squadrons can live with for 72 hours. Reports, the sandbox
> and the image library are low for the mission, but the image library is where our open
> vulnerabilities sit, so it gets attention out of proportion to its mission value.

### Q2 {#INT-024.Q2}
Asked of: PER-PM · Task: P-10
**A2 {#INT-024.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/architecture.md#updates]]
> Nothing new is planned for production before MVCR deployment. Release 1.5.2 (planned
> 2026-12-10) changes the base image and the image library version; release 1.6 (planned
> 2027-01-15) adds salted pseudonyms and an archive tier for audit logs, which may add a storage
> item. Those will be added when they are fielded, not before.

### Q3 {#INT-024.Q3}
Asked of: PER-PM · Task: P-10
**A3 {#INT-024.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#configuration]]
> Items supplied by other programs are the base image from the software factory and the managed
> services from the cloud provider; the program configures them and owns the configuration, so
> I am the owner of record for every item. The authoritative inventory is the Component IT
> asset management repository (fictional), where ARSPO keeps the EFRAS production record,
> EFRAS-PROD; the pipeline updates it from the infrastructure templates at each release.

### Q4 {#INT-024.Q4}
Asked of: PER-PM · Task: P-10
**A4 {#INT-024.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/conops.md#availability]] [[ART-BIA]]
> EFRAS is not a high-value asset. It is decision support only, an outage grounds no aircraft,
> squadrons fall back to EMIS reports, and the Component has not put it on its high-value asset
> list. The intangible assets I care about are the daily readiness reporting process, the trust
> commanders place in the readiness figures, and the maintainers' privacy; a breach of their
> records would hurt the program's standing with the fleet more than an outage would.
