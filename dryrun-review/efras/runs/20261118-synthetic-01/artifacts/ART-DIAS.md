---
artifact_id: ART-DIAS
run_id: 20261118-synthetic-01
produced_by_task: R-1
touched_by: [R-1]
sources: [INT-184.A1, INT-184.A2, INT-123.A5, ART-SSP, product/architecture.md#identity]
---
# Digital Identity Acceptance Statement

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

## Assurance levels

The levels recorded in `artifacts/data/dias.yaml` are IAL3, AAL3 and FAL1. EFRAS did not choose
them through its own E-Authentication risk assessment: every user and engineer signs in with a
CAC at the enterprise identity broker, so the enterprise credential and broker set the levels,
and the ia-2 and ia-5 statements of the security plan rest on them [[INT-123.A5]]
[[INT-184.A1]] [[ART-SSP]]. Federation is stated as FAL1 because the program can show only that
the broker's assertions are signed; the encryption setting of the onboarding profile is not
recorded, and the ISSO confirms it with the broker before the decision [[INT-184.A1]].

## Processes and technologies

CAC issuance by the DoD credentialing process gives in-person proofing (IAL3); the CAC's PKI
certificate on a hardware token with a PIN gives multi-factor cryptographic authentication
(AAL3), verified by CAC sign-in for all five roles in DT-2; the broker's signed assertion carries
the DoD ID number, which the web and API tiers bind to the session and to every audit event
[[INT-184.A1]] [[product/architecture.md#identity]] [[product/test-results.md#dt-2]].
Workloads use short-lived workload identity tokens [[ART-SSP]].

## Compensating controls

One: the two break-glass console accounts use sealed FIDO2 hardware keys instead of CAC, because
the provider console cannot federate while the broker is down. Two-person unsealing, paging at
every use, full logging and a next-working-day review against the seal log compensate; the
deviation is put to the AO as POAM-020 [[INT-184.A2]] [[product/conops.md#limitations]].
