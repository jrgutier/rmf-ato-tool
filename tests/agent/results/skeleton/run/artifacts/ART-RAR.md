---
artifact_id: ART-RAR
run_id: agent-skeleton
produced_by_task: R-2
touched_by: [R-2]
sources: [ART-SAR, ART-POAM, ART-RA, ART-ORG-CONTEXT, INT-031.A4, INT-032.A4]
---
# Risk assessment report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Method

The AODR, acting for the AO under delegation, grouped the open SAR and STIG findings by the
threat events of the system risk assessment, then rated each risk's likelihood and impact on
the SP 800-30 five-level scale and derived the level from SP 800-30 Table I-2
[[INT-032.A1]] [[ART-RA]]. Likelihood starts from the ART-RA threat event and is adjusted by
the assessment evidence and the mitigations in place, as the SCA described them
[[INT-031.A1]] [[INT-031.A3]]; the SCA's confidence in the evidence is high for every
finding [[INT-031.A4]]. Each risk, its findings and its POA&M items are recorded in
`artifacts/data/rar.yaml` (RSK-001 to RSK-003) [[ART-POAM]].

## Risks

Three risks: two moderate (RSK-001, RSK-003) and one low (RSK-002) [[INT-032.A2]] [[INT-032.A3]].

**RSK-001, unattributable privileged on-site actions (moderate).** FND-001, FND-003 and
STG-004 share one cause, the shared fieldtech account, and one threat event, TE-1. The
assessment confirmed the gap and the interim site-visit log is not yet assessed, so it earns
no credit: likelihood moderate, impact moderate, level moderate [[INT-031.A1]]
[[INT-032.A2]]. POAM-001 and POAM-003 remediate it with release 2.3 by 2027-03-31
[[ART-POAM]].

**RSK-003, exploitation of outdated fielded gateways (moderate).** FND-004 and STG-001
confirm TE-2: two units ran a 63-day-old bundle with 4 high and 9 medium vulnerabilities, and
any unit can fall about 90 days behind [[INT-031.A3]]. The enclave and host firewalls and CSSP
monitoring hold likelihood at moderate; impact stays high, so Table I-2 gives moderate
[[INT-032.A3]]. POAM-005 and POAM-006 update the two units by 2026-11-20 and POAM-004
delivers remote update by 2027-01-31 [[ART-POAM]]. The AODR would rate this risk high if those
dates slip [[INT-032.A3]].

RSK-002 (FND-002, departed technician's credential) is low: likelihood low, impact moderate
[[INT-032.A2]].

## Risk determination

The AODR determines the overall risk of operating the system as **moderate**, the highest
single risk level; the two moderate risks are independent, so they neither lower nor compound
the overall level [[INT-032.A4]]. The Component accepts moderate residual risk at the AO's
discretion, so the determination is within the organizational risk tolerance and does not
need the Component CIO's concurrence, which a high or very high level would
[[ART-ORG-CONTEXT]] [[INT-032.A4]].

## Recommended responses

The AODR recommends **mitigate** for all three risks, through the POA&M items on their
scheduled dates, and no permanent acceptance [[INT-032.A5]]. The AODR further recommends that
any authorization carry as conditions the per-unit updates by 2026-11-20 (POAM-005,
POAM-006) and remote update by 2027-01-31 (POAM-004), with monthly POA&M reporting to the AO
[[INT-032.A5]] [[ART-POAM]].
