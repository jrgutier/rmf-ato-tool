---
artifact_id: ART-RAR
run_id: agent-skeleton
produced_by_task: R-2
touched_by: [R-2]
sources: [ART-PKG, ART-RA, ART-SAR, ART-POAM, ART-STIG, ART-ORG-CONTEXT, INT-025.A1, INT-025.A2, INT-026.A1, INT-026.A2, INT-026.A3]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Method

The AODR analyzed the authorization package as generated [[ART-PKG]]. Each open SAR finding and
open STIG finding was mapped to the threat event in the system risk assessment it enables, and
findings sharing a threat event were grouped into one risk [[ART-RA]] [[ART-SAR]] [[ART-STIG]].
Likelihood and impact were rated on the SP 800-30 five-level scale, adjusted by the assessor's
view of exploitability and the mitigations observed [[INT-025.A1]] [[INT-025.A2]], and the level
was read from SP 800-30 Table I-2. The risk records are in `artifacts/data/rar.yaml`.

## Risks

- **RSK-001 (moderate):** two fielded units ran an update bundle 63 days old with known high and
  medium vulnerabilities (FND-003, STG-001). Likelihood is moderate because an attacker needs a
  foothold on the installation network behind the enclave and host firewalls; impact is high
  because a compromised gateway could falsify or suppress alarms; Table I-2 gives moderate
  [[INT-025.A1]] [[INT-026.A1]]. The rating rests on the 2026-09-30 scan; the November rescan
  is not yet in the evidence [[ART-SAR]].
- **RSK-002 (moderate):** ten technicians share the local `fieldtech` account, so privileged
  on-site actions cannot be attributed (FND-001, FND-002, STG-004). Likelihood is moderate
  because use requires physical presence; impact is moderate because audit records still reach
  the SIEM; Table I-2 gives moderate [[INT-025.A2]] [[INT-026.A2]].

## Risk determination

The AODR determines the overall risk as moderate: the highest risk is moderate and the two risks
are independent, so they do not combine into a higher level [[INT-026.A3]]. The Component accepts
moderate residual risk at the AO's discretion, so the determination is within the organizational
risk tolerance and no Component CIO concurrence is required [[ART-ORG-CONTEXT]].

## Recommended responses

- RSK-001: mitigate through POAM-003, with out-of-cycle site visits until release 2.2 delivers
  remote update by 2026-12-31 [[INT-026.A1]] [[ART-POAM]].
- RSK-002: mitigate through POAM-001 and POAM-002, with the site-visit sign-in log as the interim
  measure until release 2.3 by 2027-03-31 [[INT-026.A2]] [[ART-POAM]].
- The AODR recommends an authorization with conditions tied to these POA&M dates, and that the
  AO review the November vulnerability rescan [[INT-026.A3]].
