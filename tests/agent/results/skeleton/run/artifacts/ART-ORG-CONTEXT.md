---
artifact_id: ART-ORG-CONTEXT
run_id: agent-skeleton
produced_by_task: P-1
touched_by: [P-1]
sources: [product/profile.yaml, product/architecture.md#components]
---
# Organizational risk context — ESG

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

<!-- Seeded for the walking-skeleton scenario: the organization-level Prepare tasks
     (P-1..P-7) are out of scope, so this artifact stands in for their output. FICTIONAL
     organization. -->

## RMF role assignments

The fictional Component that owns the installation has assigned the RMF roles for ESG as
follows [[product/conops.md#program]]:

| Role | Persona | Assigned to |
|---|---|---|
| Authorizing Official | PER-AO | the Component's AO for installation operational systems |
| AO Designated Representative | PER-AODR | appointed in writing by the AO |
| Security Control Assessor | PER-SCA | the Component CISO's assessment team (delegated SCA), independent of RSSPO |
| Program Manager / System Owner | PER-PM | RSSPO program manager |
| ISSM / ISSO | PER-ISSM / PER-ISSO | appointed by the program manager |
| Common control providers | PER-CCP | Installation Network Enclave, Installation ICAM Service, Installation CSSP |

## Risk management strategy and risk tolerance

- The Component accepts **moderate** residual risk for installation operational systems at an
  AO's discretion; residual risk rated **high** or **very high** needs the Component CIO's
  documented concurrence before an ATO is issued (DoDI 8510.01 4.3.c(7)) [[product/profile.yaml]].
- Risk is rated on the SP 800-30 five-level scale (very low to very high), combining
  likelihood and impact.
- Every weakness that is not remediated before the authorization decision is tracked in a
  POA&M with a scheduled completion date; the AO monitors POA&M execution.
- Authorization termination dates are at most 3 years after the decision; an ATO with
  conditions names each condition and its due date.

## Organizational flaw remediation and configuration standards

- Security-relevant updates are installed within **30 days** of release, or a POA&M item is
  opened [[product/architecture.md#updates]].
- Components are configured to the applicable DISA SRGs and STIGs; deviations are documented
  and approved by the configuration control board [[product/architecture.md#configuration]].

## Common controls available for inheritance

| Provider | Persona | Controls offered to ESG | Authorization |
|---|---|---|---|
| Installation Network Enclave | PER-CCP | enclave boundary protection (sc-7 at the enclave edge), network access control | enclave ATO, current |
| Installation ICAM Service | PER-CCP | DoD PKI authentication and identity assurance for organizational users (ia-2 for remote users) | covered by the enclave ATO |
| Installation Cybersecurity Service Provider (CSSP) | PER-CCP | log collection and correlation in the SIEM, monitoring, incident response support (au-2 event review with the system, au-6, ir-4) | CSSP authorization, current |

Inheritance is partial for every offer above: ESG still configures its own side (console
federation, host firewall, local event generation) [[product/architecture.md#components]].

## Organizational continuous monitoring

The Component expects system-level monitoring to feed the CSSP SIEM continuously, monthly
vulnerability scans, quarterly account reviews and an annual review of the event list
[[product/architecture.md#logging]].
