---
artifact_id: ART-BASELINE
run_id: agent-c1-s4-one-family
produced_by_task: S-1
touched_by: [S-1, S-2, S-3]
sources: [INT-011.A1, INT-011.A3, INT-012.A1, INT-012.A2, INT-007.A1, INT-007.A2, INT-007.A3, INT-008.A1, INT-008.A2, INT-009.A1, INT-009.A2, INT-009.A3, INT-010.A1, ART-CAT, ART-ORG-CONTEXT, ART-REQ]
---
# Control baseline, tailoring and allocation

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-55 | S-1 |
<!-- END rmf:facts -->

## Selection basis

The baseline was resolved by `rmf baseline resolve` with method `cnssi1253`: CNSSI 1253
per-objective selection, the union of the Appendix D controls selected at the confidentiality,
integrity and availability levels of the approved categorization in the facts block, plus the
NSS privacy control baseline, a default for all NSS [[INT-007.A1]] [[ART-CAT]]. The overlay
listed in the categorization (the Privacy Overlay ACCT control set) is applied; the ISSM
confirmed no Component additions for the AC family [[INT-007.A2]]. The run's control subset
limits the resolved baseline to the 55 AC-family controls in `baseline.json` [[INT-007.A1]].

## Common controls available for inheritance

- **Installation Network Enclave** (ATO, current): enclave-edge flow enforcement and the managed
  access point for remote management; partial, because ESG keeps its own host firewall
  [[INT-008.A1]] [[ART-ORG-CONTEXT]].
- **Installation ICAM Service** (covered by the enclave ATO): DoD PKI authentication and the
  account workflow for remote administrators and auditors; partial, because ESG maps group
  claims to its own roles and keeps local accounts [[INT-008.A1]].
- **Installation CSSP** (authorization current): SIEM correlation supporting atypical-usage and
  remote-access monitoring, plus the Component access control policy; partial, because ESG
  generates and forwards the events [[INT-008.A2]] [[ART-ORG-CONTEXT]].

## Tailoring and allocation

**Tailoring (S-2).** `artifacts/data/tailoring.yaml` holds 5 actions: 0 add, 0 remove,
0 compensating and 5 parameter values (ac-2 review frequency, ac-7 attempts, action and lock
period, ac-11 inactivity period) [[INT-009.A3]]. The Privacy Overlay ACCT set is the only
overlay and raises no conflict [[INT-009.A1]]. No control is scoped out: controls with no object
in ESG stay in the baseline for S-4 to mark not applicable, and the shared-account gap against
ac-2.9 gets no compensating control and goes to the POA&M [[INT-009.A2]]. The provider-touched
controls stay in the baseline for S-3 to allocate [[INT-010.A1]].

**Allocation (S-3).** `artifacts/data/allocation.yaml` allocates all 55 controls: 0 common,
9 hybrid and 46 system-specific [[INT-012.A1]]. The Installation ICAM Service shares ac-2,
ac-2.1, ac-2.3 and ac-2.13 (PKI authentication and the remote account workflow); the
Installation Network Enclave shares ac-4, ac-17 and ac-17.3 (enclave-edge flow enforcement and
the managed access point); the Installation Cybersecurity Service Provider shares ac-2.12 and
ac-17.1 (SIEM correlation) [[INT-012.A1]] [[INT-008.A1]] [[INT-008.A2]]. CMP-WEBUI carries the
most controls, followed by CMP-GW-OS; organizational and not-applicable controls go to the
system as a whole [[INT-011.A1]] [[INT-011.A3]]. REQ-01 and REQ-02 map to allocated controls;
REQ-03 to REQ-07 rest on families outside the control subset and are not cross-checked here
[[INT-012.A2]].

## Requirements to address in tailoring

REQ-01 and REQ-02 map to AC controls in the baseline; REQ-01 is not met on site while the shared
`fieldtech` account exists, a gap against ac-2.9 for S-4 to record, not a missing control
[[INT-007.A3]] [[ART-REQ]]. REQ-03, REQ-04 and REQ-06 rest on AU, CM and SI controls outside
this run's control subset; S-2 notes them without supplementing AC [[INT-007.A3]].
