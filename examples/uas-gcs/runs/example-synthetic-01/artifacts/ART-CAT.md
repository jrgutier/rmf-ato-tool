---
artifact_id: ART-CAT
run_id: example-synthetic-01
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-024.A1, INT-024.A2, INT-024.A3, INT-025.A1, INT-026.A1, INT-026.A2, ART-INFOTYPES, INT-027.A1, INT-027.A2, INT-028.A1, INT-028.A2, INT-028.A3]
---
# Security categorization

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

## Impact per information type

| Information type | C | I | A | Basis |
|---|---|---|---|---|
| INF-01 Command and control data | moderate | moderate | moderate | [[INT-024.A1]] |
| INF-02 Sensor video and still images | moderate | moderate | low | [[INT-024.A2]] |
| INF-03 Mission plans and flight logs | moderate | moderate | low | [[INT-024.A2]] |
| INF-04 Map and terrain data | low | moderate | low | [[INT-024.A2]] |
| INF-05 Security management data | moderate | moderate | low | [[INT-025.A1]] |

Every owner confirmed the provisional values in ART-INFOTYPES; no value was adjusted
[[ART-INFOTYPES]].

## System categorization

Each objective takes the highest value over the five types (CNSSI 1253 §3.1.2 step 1):
confidentiality and integrity from INF-01, INF-02, INF-03 and INF-05, availability from INF-01
alone, giving the system categorization in the facts block [[INT-026.A2]]. Availability is one
level above the program's proposal in `product/profile.yaml` because losing the aircraft link
mid-mission ends the mission [[INT-024.A1]] [[INT-026.A2]]. No value was lowered to reduce the
number of controls.

## Overlays

- **Privacy Overlays (CNSSI 1253F Att. 6):** apply; INF-05 holds user names and CAC-derived
  identifiers [[INT-026.A1]] [[INT-015.A1]]. Control set by the overlay's two questions
  [[INT-028.A1]]:
  - Question 1 (PII other than audit logs or account records): no; the only PII is in the
    account and audit data, so the Low, Moderate and High sets are not required
    [[INT-015.A1]] [[INT-028.A1]].
  - Question 2 (audit logs or account records capturing user activity): yes, so the
    Accountability (ACCT) set applies, alone [[INT-028.A1]].
- **Classified information overlay (CNSSI1253E-ATT5-CLASSIFIED):** does not apply; the system
  is processed at the unclassified level [[INT-024.A3]] [[INT-026.A1]].
- **Space platform overlay (CNSSI1253F-ATT2-SPACE):** does not apply; it is a ground station
  for an aircraft [[INT-026.A1]].
- **Organization-mandated overlays:** none [[INT-026.A1]].

## Review and approval

The AODR reviewed for the AO. They checked that every type has its owner's value, that each
objective is the high-water mark, that no value was lowered for cost (availability came out
above the proposal and stayed there), and that every overlay decision has a reason; there were
no findings [[INT-027.A1]] [[INT-027.A2]]. They noted that `product/profile.yaml`'s "no PII"
was wrong and that the categorization returns for review if the pending privacy threshold
analysis changes the PII determination [[INT-027.A2]].

Re-review: the first approval recorded the Privacy Overlay without its control set, which
`rmf baseline resolve` cannot apply. The AODR raised that as a finding and had the control set
chosen by the overlay's two questions [[INT-028.A1]]. The overlay entry was corrected to the
ACCT set alone; the C, I and A values did not change. On re-check the finding was closed with
the earlier re-review condition kept [[INT-028.A2]]. The AODR approved the corrected
categorization in the facts block on behalf of the AO, replacing the first approval, with no
other condition [[INT-028.A3]].
