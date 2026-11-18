---
interview_id: INT-053
run_id: 20261118-synthetic-01
task: P-17
persona: PER-ISSM
date: 2026-11-18
topics: [contract requirements, C-SCRM terms, supplier screening, contracted work roles, cloud contract clauses]
---
# INT-053 — P-17 — PER-ISSM

### Q1 {#INT-053.Q1}
Asked of: PER-ISSM · Task: P-17
Which cybersecurity and C-SCRM requirements must the contracts carry?
**A1 {#INT-053.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[ART-REQ]]
> The ERST task order carries REQ-07 and a new C-SCRM requirement, REQ-17. REQ-17 has five terms:
> - the qualifying condition: develop only on the authorized factory, with an SBOM and a secure
>   development attestation per release;
> - reporting: report any supply chain compromise or change of ownership to the ISSM within 72
>   hours;
> - response roles: ERST, the ISSM and the factory each know their role in a supply chain
>   incident;
> - revalidation: yearly, by self-attestation plus the factory's third-party pipeline
>   assessment;
> - termination: grounds to terminate if a supply chain risk cannot be mitigated.
> ERST has no subcontractors, so there is nothing to flow down. ERST staff work as system
> administrators (the cloud operations engineers) and software developers, so the order
> carries a qualification requirement (REQ-19) under DFARS 239.71. ERST keeps each person's
> qualification record, and the contracting officer's representative checks it. The cloud task
> order on the Component vehicle must carry the DTM 24-001 clauses (REQ-18):
> - the accreditation boundary and licensing;
> - incident notification to the CSSP;
> - threat-representative testing;
> - CSP data for the CSSP's defensive operations;
> - corrective action;
> - access for inspection teams;
> - delivery of reports.

### Q2 {#INT-053.Q2}
Asked of: PER-ISSM · Task: P-17
How was each supplier screened and selected?
**A2 {#INT-053.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[product/architecture.md#leveraged]]
> On 2026-11-18, with the SCRAs, I screened all five suppliers against every list: SDN, SSI,
> FSE, SAM exclusions, CAPTA, blocked persons, the BIS unverified list, NDAA section 889 and
> other federal restrictions. All were clear, and all five are selected.
> - ERST: a qualified supplier on the shared vehicle with CMMC Level 2 (fictional). It already
>   carries other agencies' DFARS 252.204-7012 and NIST SP 800-171 requirements, and has no
>   prior intrusions.
> - Cloud provider: on the DoD approved cloud offerings list with its IL4 provisional
>   authorization, which stands in for CMMC. It carries FedRAMP and DoD SRG requirements.
> - Software factory: a government shared service with its own ATO. CMMC does not apply.
> - The two open-source projects: taken only from the factory's vetted library. CMMC does not
>   apply.
> None of the five is owned by, influenced by or tied by technology to a threat actor, as far
> as the public sources show.

### Q3 {#INT-053.Q3}
Asked of: PER-ISSM · Task: P-17
How do C-SCRM considerations enter each step of the procurement life cycle?
**A3 {#INT-053.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> - Planning: the acquisition strategy names authorized providers and the factory.
> - Requirements: REQ-07 and REQ-17 go into the statement of work.
> - Market analysis: the vendor research of 2025-08-15 covered ownership and intrusions.
> - Completing the procurement: the screenings and clauses go in before award or modification.
> - Compliance: the COR checks SBOMs and attestations per release.
> - Performance: the ISSM checks the factory reports and supplier changes each month.
> We make no ICT purchases by charge card.
