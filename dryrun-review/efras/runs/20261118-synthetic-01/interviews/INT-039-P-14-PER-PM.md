---
interview_id: INT-039
run_id: 20261118-synthetic-01
task: P-14
persona: PER-PM
date: 2026-11-18
topics: [criticality analysis record, trusted systems and networks practices, focal point threat analysis]
---
# INT-039 — P-14 — PER-PM

### Q1 {#INT-039.Q1}
Asked of: PER-PM · Task: P-14
The C-SCRM record must name at least one function in its criticality analysis, while the BIA
rates no function mission-critical. Which function would you record, and on which items?
**A1 {#INT-039.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-BIA]] [[product/architecture.md#components]]
> My answer has not changed: EFRAS performs no mission-critical function. If the record needs an
> entry, the function that matters most is the nightly ingest of the EMIS and supply extracts and
> the integrity of the readiness data it loads. Everything downstream depends on it. The items
> that perform it are the ingest worker (INV-004), the managed Kubernetes service it runs on
> (INV-008) and the managed database it writes to (INV-010). Their suppliers are ERST and the
> cloud provider. Record it as our most important function. Do not call it mission-critical in
> any prose, because the BIA does not support that.

### Q2 {#INT-039.Q2}
Asked of: PER-PM · Task: P-14
Once that entry exists, trusted systems and networks practices and a focal point threat analysis
are owed for its suppliers. What do you do?
**A2 {#INT-039.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ASM-010]]
> We treat ERST and the cloud provider as critical suppliers for the record. On 2026-11-18 I sent
> a threat analysis request for both to the Component trusted systems and networks focal point,
> which forwards it to the DIA SCRM threat analysis center. No report has come back yet. Its
> interim guidance is to keep the factory gates and signed images, to rely on the provider's
> authorization for its hardware and data center supply chain, and to flag any change of
> ownership of either supplier. Hardware assurance and anti-counterfeit measures for the physical
> platform are the cloud provider's, and we inherit them through its IL4 provisional
> authorization. We own no hardware. Software assurance for the ingest worker is the factory
> pipeline: static and dependency scans, an SBOM, signed images and the ERST secure development
> attestation.

### Q3 {#INT-039.Q3}
Asked of: PER-PM · Task: P-14
What does this change cost the program?
**A3 {#INT-039.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-BIA]]
> Two supplier risk assessments that a moderate-tolerance business system would not otherwise do
> before Milestone decisions, and a TAC request. The ISSM did the assessments with the C-SCRM
> program office. We keep the supply chain risk tolerance at moderate and change no other action.
