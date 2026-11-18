---
interview_id: INT-132
run_id: 20261118-synthetic-01
task: S-5
persona: PER-CSSP
date: 2026-11-18
topics: [continuous monitoring by the CSSP, threat monitoring, detection coverage]
---
# INT-132 — S-5 — PER-CSSP

### Q1 {#INT-132.Q1}
Asked of: PER-CSSP · Task: S-5 · Control focus: si-4, au-6, ra-5
Which monitoring do you perform continuously, which threats do you watch, and what do you report?
**A1 {#INT-132.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-118.A1]] [[INT-118.A2]] [[INT-108.A1]] [[product/architecture.md#logging]]
> Continuously, under SVA-001: correlation of the forwarded EFRAS logs with the access point's
> traffic logs in our SIEM, against our use cases and threat intelligence. Monthly: the
> non-authenticated external scan through the access point. Daily, we watch threat actor
> activity against DoD logistics and readiness data, new protective techniques and signatures,
> and the threat to the cloud region and the access point, from JFHQ-DODIN advisories, the
> Component's threat assessment, the provider's bulletins and our own feeds, and tell the ISSO
> of anything relevant within a working day. We report alerts at once, a monthly service report
> to the ISSM, and DODIN status as required. Our coverage: network traffic at the access point
> and the edge, the cloud account activity, personnel activity in the application and the
> console, and the provider's reports. We tune our use cases quarterly and after each incident
> with the ISSO to cut false positives without blinding a use case.
