# Step M · Monitor

Monitor the system and its controls on an ongoing basis, track changes, respond to risk
and report the security and privacy posture. Monitor starts with fielding and runs
through O&S to disposal (`framework/rmf-steps.yaml`).

## Tasks

| Task | Name | Playbook | Body | Outputs |
|---|---|---|---|---|
| M-1 | System and Environment Changes | [M-1.md](M-1.md) | generated | ART-CHG (produces), ART-INV, ART-CMP |
| M-2 | Ongoing Assessments | [M-2.md](M-2.md) | authored | ART-SAR, ART-CONMON |
| M-3 | Ongoing Risk Response | [M-3.md](M-3.md) | generated | ART-RA, ART-POAM |
| M-4 | Authorization Updates | [M-4.md](M-4.md) | generated | ART-SSP, ART-SAR, ART-POAM, ART-RA |
| M-5 | Security and Privacy Reporting | [M-5.md](M-5.md) | generated | ART-SECRPT (produces) |
| M-6 | Ongoing Authorization | [M-6.md](M-6.md) | generated | ART-AODM |
| M-7 | System Disposal | [M-7.md](M-7.md) | generated | ART-DISP (produces) |

## Running the step

- **Monitoring runs in cycles.** One pass M-1 → M-6 is one monitoring cycle at the run's
  `as_of` date; the strategy in `conmon.yaml` (S-5) says what is due in a cycle.
- **Assess, then respond, then update.** M-2 records new findings; M-3 gives them POA&M
  items or risk acceptance (SAR-POAM-001 reports open findings against the POA&M until
  then); M-4 brings the package artifacts up to date.
- **Ongoing authorization is the AO's.** M-6 records the AO's determination in
  `decision.yaml` (continue, AD-CATO, or denial); the triggers come from `conmon.yaml`.
- **M-7 runs once,** when the system is removed from operation.
- **Session unit:** one session per task group the prompt names; M-2 over many families
  follows `_shared/assessment-batching.md`, at most 3 families per session.

## Citations

- SP 800-37r2 §3.7 (Monitor): `uv run rmf refs show SP800-37R2 --section "3.7"`.
- DoDI 8510.01 §3.2.g and Table 7:
  `uv run rmf refs show DODI8510.01 --page 19 --anchor "Task M-1 System and Environment Changes"`.
