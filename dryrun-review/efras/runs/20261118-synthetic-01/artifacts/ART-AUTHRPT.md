---
artifact_id: ART-AUTHRPT
run_id: 20261118-synthetic-01
produced_by_task: R-5
touched_by: [R-5]
sources: [ART-AODM, INT-199.A1, INT-199.A2, INT-200.A1, INT-200.A2, INT-201.A1]
---
# Authorization report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
<!-- END rmf:facts -->

## Decision reported

AUTH-001: an authorization to operate with conditions (AD-ATOC) by the AO on 2027-01-25,
terminating 2028-01-25, with conditions COND-01 (due 2027-02-26), COND-02 (2027-02-15), COND-03
(2027-03-05), COND-04 (2027-03-01), COND-05 (2027-03-31) and COND-06 (2027-02-28), as ART-AODM
states them [[ART-AODM]]. Reported to the officials the Component designates (the CIO, the CISO,
the privacy officer and the risk board) and to the decision authority and the user
representative [[INT-199.A1]]. The PM received the decision and acknowledged its terms on
2027-01-25 and reports on each condition through the AODR; the AO verifies the terms every 90
days [[INT-200.A1]] [[INT-200.A2]].

## Significant deficiencies reported

Under the Component's threshold (risk moderate or higher, harm to individuals, or a condition
resting on it) [[INT-199.A1]]:

- RSK-001: FND-018, FND-020; POAM-001, POAM-010.
- RSK-002: FND-019, FND-024, FND-021; POAM-002, POAM-003, POAM-017.
- RSK-003: FND-001, FND-017; POAM-004, POAM-005.
- RSK-004: FND-007, FND-013, FND-008, FND-009, STG-001, STG-002; POAM-006, POAM-007, POAM-008,
  POAM-021.
- Behind COND-03 and COND-04, though low: FND-004 (POAM-011) and FND-011 (POAM-009)
  [[INT-201.A1]].

## Operational awareness

The AODR briefed the type wing's operational commander and the Component's cyberspace
operations watch on 2027-01-26 with the decision, its conditions and the PM's notice to the
squadrons. Two risks touch operational requirements and were agreed with the commander and the
PM: unproven regional recovery against daily readiness reporting (RSK-005), and the loss of PDF
and slide exports if the report container misses COND-02 (RSK-002) [[INT-199.A2]].

## Registry annotation

The ISSM entered the decision in the Component's eMASS record on 2027-01-26: status ATO with
conditions, decided 2027-01-25, terminating 2028-01-25, the six conditions and the decision memo,
the R-5 update the registration plan names [[INT-201.A1]]. It is recorded in
`artifacts/data/registration.yaml` and ART-REG.
