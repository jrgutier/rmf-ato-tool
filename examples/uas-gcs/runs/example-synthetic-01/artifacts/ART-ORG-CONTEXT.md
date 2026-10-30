---
artifact_id: ART-ORG-CONTEXT
run_id: example-synthetic-01
produced_by_task: P-1
touched_by: [P-1, P-2, P-3, P-4, P-5, P-6, P-7]
sources: [INT-001.A1, INT-002.A2, INT-003.A3, INT-004.A1, INT-005.A2, INT-006.A1, INT-007.A1, ASM-001, product/stakeholders.md#roles]
---
# Organizational risk context

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

<!-- Sections, in order: P-1 role assignments; P-2 strategy and tolerance; P-3 organization-level
     risk assessment; P-4 tailored baselines; P-5 common controls; P-6 impact-level
     prioritization; P-7 organizational continuous monitoring strategy. No organizational policy
     was supplied (ASM-001): positions below are the simulated personas' statements. -->

## RMF role assignments

| Role | Persona ID | Assigned to | Appointed by | Trace |
|---|---|---|---|---|
| Component CIO | PER-CIO | Component CIO (fictional) | Component head | [[INT-001.A1]] |
| Component CISO (senior information security officer) | PER-CISO | Component CISO (fictional) | Component CIO | [[INT-001.A1]] |
| Authorizing official | PER-AO | Army Aviation Mission Area AO (fictional) | Component CIO | [[INT-001.A1]] [[product/stakeholders.md#roles]] |
| AO designated representative | PER-AODR | AODR, Aviation Systems | AO, in writing | [[INT-001.A1]] |
| Risk executive (function) | PER-RE | Component risk executive function | Component CIO | [[INT-002.A1]] |
| Senior agency official for privacy | PER-PRIV | Component privacy officer | Component CIO | [[INT-001.A3]] |
| Security control assessor | PER-SCA | Aviation Systems SCA team, independent assessment activity (fictional) | AO, per system | [[INT-001.A2]] |
| Program manager / system owner | PER-PM | Product Manager, SUGS-PO | Program executive office | [[INT-001.A2]] |
| ISSM | PER-ISSM | SUGS-PO ISSM | Product manager, in writing | [[INT-001.A2]] |
| ISSO | PER-ISSO | ETGCS ISSO | Product manager, in writing | [[INT-001.A2]] |
| Common control provider (enclave) | PER-CCP | Brigade S6, Brigade Tactical Network Enclave | Brigade command | [[INT-001.A2]] [[product/stakeholders.md#roles]] |

Separation: the AO sits outside SUGS-PO and the brigade S6, so it neither owns the system nor
provides the controls it inherits, and the SCA reports outside the program chain [[INT-001.A4]].
No separation conflict was found.

## Risk management strategy and risk tolerance

- **Framing and method.** Frame, assess, respond, monitor per SP 800-39; risk is framed by
  mission impact and rated on the SP 800-30 five-level scale (very low to very high) for
  likelihood, impact and risk [[INT-002.A1]].
- **Risk tolerance.** The AO may accept residual risk rated low or moderate. A high residual
  risk needs Component CIO concurrence before the ATO is signed, plus a POA&M item with a dated
  mitigation. A very high residual risk is not accepted [[INT-002.A2]] [[ASM-002]].
- **Authorization period.** At most three years [[INT-002.A3]].
- **Remediation periods.** 30 days (very high), 90 days (high), 180 days (moderate), 365 days
  (low), or an approved milestone extension in the POA&M [[INT-002.A3]].
- **Priorities and constraints.** Mission availability first, then integrity of command and
  control, then confidentiality of mission products; monitoring and patching must allow for
  long disconnected periods; the privacy officer reviews every categorization [[INT-002.A4]].

## Organization-level risk assessment

| ID | Risk | Likelihood | Impact | Risk | Trace |
|---|---|---|---|---|---|
| R-ORG-1 | Loss or degradation of tactical data links (jamming, spoofing) | moderate | high | moderate | [[INT-003.A3]] |
| R-ORG-2 | Compromise of captured field equipment | moderate | moderate | moderate | [[INT-003.A3]] |
| R-ORG-3 | Malicious code via removable media during maintenance | moderate | high | moderate | [[INT-003.A3]] |
| R-ORG-4 | Supply chain compromise of commercial components or integrator software | low | high | moderate | [[INT-003.A3]] |
| R-ORG-5 | Delayed patching and monitoring during disconnected operations | high | moderate | moderate | [[INT-003.A3]] |

Common predisposing conditions are long disconnected periods, shared maintenance accounts on
field equipment and dependence on the brigade enclave [[INT-003.A2]]. The threat picture is a
generic summary, as no threat product was supplied [[ASM-003]]. The assessment is reviewed
yearly and after a major threat change; last updated in the third quarter of fiscal year 2026
[[INT-003.A4]].

## Organizationally tailored baselines and profiles

The organization has approved no tailored baseline or CSF profile of its own; systems start
from the CNSSI 1253 baselines with DoD assignment values [[INT-004.A1]]. CNSSI 1253 overlays
apply by their applicability questions (the Privacy Overlay where a system holds PII), decided
in the system's categorization and selection tasks [[INT-004.A2]].

## Common controls available for inheritance

| Provider | Persona ID | Controls offered | Full or partial | Provider authorization | Trace |
|---|---|---|---|---|---|
| Brigade Tactical Network Enclave (brigade S6) | PER-CCP | sc-7, si-4, ac-2, ia-2, au-6, au-9, ir-4, ir-6 | partial (hybrid): the system keeps its own boundary device, local accounts and local logs | ATO 2025-05-30 (fictional) | [[INT-005.A1]] [[INT-005.A2]] [[product/architecture.md#leveraged]] |
| Component cybersecurity program (Component CISO) | PER-CISO | pm family; policy and procedure parts of each family's first control | full | Component program, not a system authorization | [[INT-005.A3]] [[ASM-004]] |

The Component privacy program provides the privacy program controls; a system without PII
needs no further privacy common controls [[INT-005.A3]].

## Impact-level prioritization

The organization does not use impact sub-categories; within an impact level it orders
resources by mission priority, with fielded tactical aviation systems ahead of test and
garrison systems [[INT-006.A1]].

## Organizational continuous monitoring strategy

- **Frequencies.** Set by control volatility: vulnerability scans and STIG checks at least
  monthly when connected and on reconnection; account reviews quarterly; a third of the other
  controls assessed each year, so all are assessed within the authorization period
  [[INT-007.A1]] [[ASM-005]].
- **Metrics.** POA&M items past due, critical and high vulnerabilities older than the
  remediation period, STIG compliance percentage, days since logs last reached the enclave
  collector [[INT-007.A2]].
- **Reporting and triggers.** The ISSM reports to the AO quarterly and to the risk executive
  twice a year, with scan and log data from the CSSP and the enclave provider. A significant
  change, an unmitigated new critical vulnerability or a missed high-risk remediation date
  triggers an AO review [[INT-007.A3]].
