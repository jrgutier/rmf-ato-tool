---
artifact_id: ART-BASELINE
run_id: example-synthetic-01
produced_by_task: S-1
touched_by: [S-1, S-2, S-3]
sources: [INT-029.A1, INT-029.A2, INT-029.A3, INT-030.A1, INT-030.A2, INT-031.A1, INT-031.A2, INT-031.A3, INT-031.A4, INT-032.A1, INT-033.A1, INT-033.A2, INT-033.A3, INT-033.A4, INT-034.A1, INT-035.A1, ART-ORG-CONTEXT, ART-REQ]
---
# Control baseline, tailoring and allocation

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

## Selection basis

The baseline was resolved by `rmf baseline resolve` with method `cnssi1253` (CNSSI 1253
per-objective selection): the union of the CNSSI 1253 Appendix D controls selected at the
confidentiality, integrity and availability levels of the approved categorization in the facts
block, plus the NSS privacy control baseline, which CNSSI 1253 §3.2.1 makes a default for all
NSS, then the overlay listed in the facts block (the Privacy Overlay Accountability control set
only). No classified or space overlay applies, and the organization has no tailored baseline of
its own, so nothing is added at selection [[INT-029.A1]] [[INT-028.A3]] [[ART-ORG-CONTEXT]].
The resolved set is 523 controls and enhancements, 35 of them selected only by the privacy
baseline; the ISSM confirmed the recorded baseline ID as the selected baseline [[INT-029.A1]].

## Common controls available for inheritance

| Provider | Controls offered | Full or partial | Provider authorization | Trace |
|---|---|---|---|---|
| Brigade Tactical Network Enclave (PER-CCP) | sc-7, si-4, ac-2, ia-2, au-6, au-9, ir-4, ir-6 | partial (hybrid) only; nothing covers the station while disconnected | enclave ATO 2025-05-30 (fictional), in period | [[INT-030.A1]] [[INT-030.A2]] |
| Component cybersecurity program (PER-CISO) | pm family; policy and procedure parts of each family's first control | full | Component program, not a system authorization | [[ART-ORG-CONTEXT]] [[INT-005.A3]] |

The Component privacy program provides the privacy program controls [[ART-ORG-CONTEXT]].

## Tailoring and allocation

**Tailoring (S-2).** `artifacts/data/tailoring.yaml` holds 10 actions: 1 add, 0 remove,
0 compensating, 9 parameter. Only the Privacy Overlay Accountability set applies, so there is
no overlay conflict [[INT-031.A1]]. No control was scoped out and none was given a compensating
control; controls the station cannot yet meet (for example the shared GDT management account)
stay in the baseline as `planned` for S-4 and the POA&M [[INT-031.A2]]. si-7.15 (code
authentication) was added for REQ-04, and cm-14, cp-7 and cp-2 parameters cover REQ-04 and
REQ-10 [[INT-031.A3]] [[INT-031.A4]]. The provider's eight offered controls are all in the
baseline and stay in [[INT-032.A1]]. The tailored baseline has 524 controls.

**Allocation (S-3).** `artifacts/data/allocation.yaml` allocates all 524 controls: 49 common,
8 hybrid and 467 system-specific [[INT-034.A1]]. The Component cybersecurity program provides
37 common controls (each family's policy control and the program management family); the
Component privacy program provides 12 (pt-1 and the privacy program controls of the program
management family) [[INT-034.A1]] [[ART-ORG-CONTEXT]]. The Brigade Tactical Network Enclave is
the hybrid provider for sc-7, si-4, ac-2, ia-2, au-6, au-9, ir-4 and ir-6, base controls only,
and only while the station is connected [[INT-035.A1]]. The workstation operating system
(CMP-WS-OS) carries the most system-specific controls, followed by the station router
(CMP-ROUTER) and the ground data terminal (CMP-GDT); procedural controls are allocated to the
system as a whole [[INT-033.A1]] [[INT-033.A4]]. Requirements cross-check: every ART-REQ
requirement maps to at least one control on its allocated element (REQ-02 to sc-8 and sc-13 on
CMP-GDT and CMP-AV; REQ-06 to au-6 and au-9 hybrid with CMP-BTNE; REQ-08 to sc-28 on CMP-WS-HW;
REQ-10 to cp-7 on the system); no gap was found [[INT-033.A2]] [[INT-033.A3]] [[ART-REQ]].

## Requirements to address in tailoring

No requirement in ART-REQ is left without any control [[INT-029.A3]]. Three need a deliberate
look in S-2 [[INT-029.A2]] [[ART-REQ]]:

- REQ-04 (signed bundles only): confirm the software integrity and signed-component controls are
  selected at the needed enhancement.
- REQ-07 (individual authenticators on the GDT management service): apply the identification and
  authentication controls to a device interface shipped with a shared account.
- REQ-10 (spare station within 4 hours): set the contingency plan assignment values to that
  recovery time.
