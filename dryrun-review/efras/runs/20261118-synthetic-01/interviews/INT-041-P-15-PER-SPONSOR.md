---
interview_id: INT-041
run_id: 20261118-synthetic-01
task: P-15
persona: PER-SPONSOR
date: 2026-11-18
topics: [protection needs, capability needs statement, protection content, agreement]
---
# INT-041 — P-15 — PER-SPONSOR

### Q1 {#INT-041.Q1}
Asked of: PER-SPONSOR · Task: P-15
Which security protection needs does the capability carry, and how will you judge them met?
**A1 {#INT-041.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-STAKE]] [[product/conops.md#information]]
> Two needs. First, an adversary must not see aggregated fleet readiness. I judge that met when
> only authenticated DoD users reach the service, each sees only their own echelon, and nothing
> is reachable from the internet. Second, the readiness figures must match what the maintenance
> system recorded. I judge that met when every nightly load is checked against its source's
> signature and checksum, and a
> failed check stops the load instead of publishing altered data. Integrity ranks first,
> because wrong figures mislead the fleet. Confidentiality of the aggregate ranks second.

### Q2 {#INT-041.Q2}
Asked of: PER-SPONSOR · Task: P-15
Which capability document governs EFRAS, and what protection content does it hold?
**A2 {#INT-041.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/stakeholders.md#roles]] [[product/conops.md#program]]
> The capability needs statement for fleet readiness analytics, version 1.0, which the fleet
> readiness directorate validated on 2025-08-01 for the software pathway. It is not a JCIDS
> document. It asks for CUI protection and a supply chain that runs only through authorized
> providers. It cites the Component threat assessment as its threat information. It says nothing
> about export control or anti-tamper, because there is no foreign release and no hardware. It
> says nothing about counterintelligence support, and I accept that gap. The PPP covers it
> through the Component counterintelligence office.

### Q3 {#INT-041.Q3}
Asked of: PER-SPONSOR · Task: P-15
Do the requirements in the draft matrix address your needs?
**A3 {#INT-041.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]]
> Yes. I agree to the integrity requirement on the ingest (REQ-04) at priority 1, and to
> authentication, echelon-based access and ECAP-only ingress (REQ-01, REQ-02, REQ-10) for the
> aggregate. I agreed on 2026-11-18. The ingest must check both the EMIS signature and the
> checksum of every extract.
