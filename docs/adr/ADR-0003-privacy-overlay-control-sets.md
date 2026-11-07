# ADR-0003: The Privacy Overlay as one overlay per control set

Date: 2026-10-29 · Status: accepted · Phase: 7 · Schemas: none changed (data in `framework/baselines/cnssi-1253.yaml`; FACTS-001 behaviour)

## Context

The example synthetic run (Phase 7b) stopped at S-1. C-2 had recorded the Privacy Overlay
(`CNSSI1253F-ATT6-PRIVACY`) because the system's account and audit records hold user
names and CAC identifiers, C-3 approved it, and `rmf baseline resolve` then refused it as
untranscribed (L-0035). ADR-0002 had left the overlay untranscribed because it selects
controls by condition.

The condition is a choice among four control sets (Table 1, p11): Accountability (ACCT),
Low, Moderate and High. §4.1 (p12) picks them with two questions: PII other than audit
logs and account records takes the Low, Moderate or High set by privacy risk level; audit
logs or account records take the ACCT set. Table 2 (pp15-27) marks, per control, `+`
(select), `--` (do not select) or `*` (optional, Privacy Enhancing) in each set's column.

## Decision

- Transcribe Table 2 as four overlays, `CNSSI1253F-ATT6-PRIVACY-ACCT`, `-LOW`,
  `-MODERATE` and `-HIGH`, each `ref: CNSSI1253F-ATT6-PRIVACY`, `transcribed: true`, with
  page-cited `add` blocks like the Classified System Overlay. A set selects a control when
  its cell starts with `+`. `--` and `*` add nothing; the overlay never removes a control.
- `categorization.overlays` stays a list of IDs (no facts schema change). C-2 records the
  set IDs that apply; a system whose only PII is in audit and account records records the
  ACCT set alone. `playbooks/C/C-2.md` step 6 says so.
- The bare reference ID stays listed with `transcribed: false` (INV-3: IDs are not
  removed). `rmf baseline resolve` and FACTS-001 name the set IDs to use instead.
- FACTS-001 now also fails for any `categorization.overlays` entry that
  `rmf baseline resolve` cannot apply. It is owned by C-2 and C-3, and FACTS-001 applies
  from C-3, so the approval reopens at categorization time instead of S-1 stopping after it.
- The rows come from the text extraction, whose seven columns stay aligned in this table.
  `rmf_tool.cnssi1253.privacy_overlay` joins IDs the extraction prints on the next row or
  splits over two rows, identifies an ID-less row by its catalog name, and requires every
  printed ID to carry its catalog name. The two rows where the PDF prints a different name
  (IA-2(6) repeats IA-2(5)'s name; PT-8 says "Requirement") are listed errata, and an
  erratum that matches no row fails. Checks: the sets nest (ACCT ⊆ Low ⊆ Moderate ⊆ High).

## Consequences

- Set sizes: ACCT 92, Low 121, Moderate 169, High 174 controls. At M/M/L the ACCT set adds
  31 controls the NSS baseline does not already select (mostly the PT family, RA-8, SI-18).
- Every committed run and fixture keeps its baseline; their `baseline.json` source hash of
  the tables file changes, so they are re-resolved (no control changes without overlays).
- The Space Platform Overlay remains untranscribed; FACTS-001 now reports a run that picks
  it at C-3 rather than at S-1.

## The PIA on an NSS, and the privacy plan, 2026-11-07 (p11, I-15)

- DoDI 5400.16 Enclosure 3 1d(2) excludes national security systems from the PIA requirement
  and still asks that their privacy implications be considered; the Privacy Overlay that
  replaces the PCIL analysis on an NSS can select RA-8. A selected RA-8 makes the PIA a control
  the system implements, so PRIV-001 reads the exclusion as void once ra-8 is in the baseline,
  and accepts it otherwise only on a Privacy Overlay control set and a statement of the privacy
  implications considered (I-32).
- SP 800-37r2 lets an organization keep separate security and privacy plans, and
  `plan_structure.consolidation` may say so. This framework has one plan artifact, ART-SSP, so a
  system processing PII records its privacy plan in `ssp-records.yaml` `privacy_plan` either way
  (PRIV-008); a separate plan's own artifact (ART-PRIVPLAN) is planned under WI-02. A first cut
  refused `separate`, a choice the source permits; Fable's review of I-15 removed the refusal.
- PER-PRIV stands for the senior agency official for privacy and the system privacy officer
  until PER-SPO exists (WI-02); every system-level task names it under `raci.when:
  processes-pii`, and PRIV-009 asks its interview where it is responsible.
