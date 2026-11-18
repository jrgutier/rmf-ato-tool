---
interview_id: INT-105
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [personnel screening before access, termination and removal of access]
---
# INT-105 — S-4 — PER-ISSO

### Q1 {#INT-105.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ps-3
How is someone screened before getting EFRAS access, and when are they screened again?
**A1 {#INT-105.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]] [[INT-075.A2]]
> Every user holds a CAC, which the Component issues only after a favorable background
> investigation, and I provision no role until the access request shows it. The privileged
> roles (app-admin, auditor, the ERST cloud console roles) need the higher investigation the
> Component sets for privileged IT access, which the Component security office confirms before I
> provision. People are enrolled in continuous vetting, so they are rescreened continuously, and
> again before any move into a privileged role or when the security office reports adverse
> information. Everyone sees maintainer PII, so this screening happens before any PII access.
> The screening records stay with the security office and ERST, not in EFRAS.

### Q2 {#INT-105.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ps-4
What happens to a person's access, credentials and equipment when their employment ends?
**A2 {#INT-105.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#account-review]] [[INT-086.A1]] [[INT-097.A2]]
> The out-processing checklist notifies me and the account managers within 24 hours. I remove
> the person's group, which disables the EFRAS account, within one working day for a voluntary
> departure and the same day for an involuntary one; without the group the identity broker gives
> no access. The security office revokes the CAC and its certificates. If the person held a
> cloud console role, I remove it the same day; if they were a break-glass key custodian, the key
> is re-registered and resealed. The supervisor's exit briefing covers the duty to protect CUI
> and maintainer PII after leaving, the return of equipment and that no export or extract may be
> kept. ERST retrieves the privileged access workstation and any FIDO2 key. Their exports and
> reports stay in the object store and remain readable by the ISSO and the information owner.
> Behind that, accounts unused for 35 days disable themselves and my quarterly review catches
> what is left; the 2026-10-06 review removed two accounts of users who had left a pilot squadron.
