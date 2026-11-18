---
interview_id: INT-063
run_id: 20261118-synthetic-01
task: C-2
persona: PER-PM
date: 2026-11-18
topics: [impact values INF-05 INF-06, profile proposal]
---
# INT-063 — C-2 — PER-PM

### Q1 {#INT-063.Q1}
Asked of: PER-PM · Task: C-2
INF-05, audit records, which the program owns: do you confirm confidentiality moderate,
integrity moderate and availability low?
**A1 {#INT-063.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-030.A2]] [[ART-INFOTYPES]] [[product/architecture.md#logging]]
> I confirm. The records carry names and DoD ID numbers and show what each user exported, so
> disclosure is a serious effect: moderate. Altered audit records would hide misuse and break
> accountability: moderate. Losing our copy for a while is limited, because ECSSP keeps its own
> copy for a year: low.

### Q2 {#INT-063.Q2}
Asked of: PER-PM · Task: C-2
INF-06, system security information: do you confirm confidentiality moderate (raised to the
user information), integrity moderate and availability low?
**A2 {#INT-063.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-030.A3]] [[ART-INFOTYPES]]
> I confirm. Keys, secrets and security policy protect the user information, so they are held at
> its level: moderate confidentiality. A changed security group or role mapping opens the data:
> moderate integrity. The keys and configuration can be restored from the pipeline and the key
> service; a short loss is limited: low availability.

### Q3 {#INT-063.Q3}
Asked of: PER-PM · Task: C-2
The product profile proposed moderate, moderate, low and the Privacy Overlay, and also that the
system is an NSS. Do you hold to those proposals?
**A3 {#INT-063.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[INT-051.A1]]
> The profile was our proposal before the information owners and the CIO answered. The
> categorization is what the owners' values give; if that matches our proposal, fine. On NSS, I
> defer to the CIO's determination at P-16 that EFRAS is not a national security system; the
> profile line saying it is was our mistake, made because the Component tells us to use the
> CNSSI 1253 baselines.
