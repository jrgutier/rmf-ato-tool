---
interview_id: INT-007
run_id: agent-c1-s4-one-family
task: S-1
persona: PER-ISSM
date: 2026-10-30
topics: [baseline selection, overlays, uncovered requirements]
---
# INT-007 — S-1 — PER-ISSM

### Q1 {#INT-007.Q1}
Asked of: PER-ISSM · Task: S-1
**A1 {#INT-007.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-006.A3]]
> The categorization the AODR approved selects the CNSSI 1253 Appendix D controls per objective,
> moderate for confidentiality and integrity and low for availability, plus the NSS privacy
> baseline. The run is limited to the AC family, so the resolved baseline is the 55 AC controls
> the tool lists. I confirm that baseline as the starting point for tailoring.

### Q2 {#INT-007.Q2}
Asked of: PER-ISSM · Task: S-1
**A2 {#INT-007.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-005.A1]]
> The only overlay is the privacy overlay's ACCT control set, because user names sit in account
> and audit records. No organizational additions to the AC family come from the Component.

### Q3 {#INT-007.Q3}
Asked of: PER-ISSM · Task: S-1
**A3 {#INT-007.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/conops.md#limitations]]
> Within AC, REQ-01 and REQ-02 map to account management, privileged accounts and remote access.
> REQ-03, REQ-04 and REQ-06 rest on AU, CM and SI controls that are outside this run's control
> subset, so S-2 should note them rather than supplement AC. REQ-01 is not met on site while the
> shared `fieldtech` account exists; that is a gap against ac-2.9, not a missing control.
