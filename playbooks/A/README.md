# Step A · Assess

Assess whether the controls are implemented correctly, operating as intended and producing
the desired outcome, using developmental and operational test events where possible. The
assessment plan is approved before the TRR so DT&E events can supply assessment evidence
(`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| A-1 | Assessor Selection | [A-1.md](A-1.md) | generated | none (interviews, journal DECISION) |
| A-2 | Assessment Plan | [A-2.md](A-2.md) | authored | ART-SAP (produces) |
| A-3 | Control Assessments | [A-3.md](A-3.md) | authored | ART-SAR (produces), ART-STIG |
| A-4 | Assessment Reports | [A-4.md](A-4.md) | authored | ART-SAR |
| A-5 | Remediation Actions | [A-5.md](A-5.md) | authored | ART-SAR, ART-SSP |
| A-6 | Plan of Action and Milestones | [A-6.md](A-6.md) | authored | ART-POAM (produces) |

## Running the step

- **The agent is the assessor.** From A-2 to A-5 the agent acts as PER-SCA: independent,
  evidence-first, never taking the SSP's claim as evidence (`personas/PER-SCA.md`).
- **Assess family by family** (`_shared/assessment-batching.md`), at most 3 families per
  session; A-3 usually takes several sessions.
- **Original results stay.** A-4 completes the report without changing a determination;
  A-5 closes findings only after reassessment and keeps the A-3 result in the record.
- **Every open weakness reaches the POA&M** at A-6: each open SAR finding
  (SAR-POAM-001) and each open CAT I STIG finding (STIG-002).

## Citations

- SP 800-37r2 §3.5 (Assess): `uv run rmf refs show SP800-37R2 --section "3.5"`.
- DoDI 8510.01 §3.2.e and Table 5:
  `uv run rmf refs show DODI8510.01 --page 17 --anchor "Assess the controls to determine whether they are being correctly implemented"`.
