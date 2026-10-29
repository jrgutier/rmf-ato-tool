---
artifact_id: ART-CMP
run_id: valid-minimal
produced_by_task: S-4
touched_by: [S-4, I-2]
sources: [INT-007.A1, INT-033.A1]
---
# Configuration management plan

## Baseline configuration

The relay appliance and console are built from STIG-hardened images; the image definitions
are the configuration baseline [[INT-007.A1]] [[product/security.md#configuration]].

## Change control

Changes go through the program's change board; the ISSM reviews each for security impact
[[INT-007.A1]].

## As built

The developers confirmed the baseline against the build [[INT-033.A1]].
