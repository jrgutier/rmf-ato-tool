---
artifact_id: ART-IRP
run_id: example-synthetic-01
produced_by_task: S-4
touched_by: [S-4, I-2]
sources: [product/architecture.md#leveraged, product/architecture.md#logging, INT-054.A2, INT-055.A1, INT-062.A1, INT-063.A2, INT-063.A3]
---
# Incident response plan

## Plan summary

The plan covers incidents on any station kit. Detection comes from the workstation's local
alerts for malicious code, drift and integrity failures, and from the enclave intrusion
detection and log collector for forwarded workstation and router events [[INT-054.A2]]
[[INT-055.A1]]. Users report to the ISSO, who reports to the Brigade Tactical Network Enclave
CSSP, which provides incident handling support under the enclave ATO
[[product/architecture.md#leveraged]]. The platoon isolates a suspect station by pulling the
uplink and swaps in a spare kit while the ISSO preserves evidence. Planner and GDT logs stay
local and are checked by hand during an incident [[product/architecture.md#logging]]. The
full plan, training and first test are planned before fielding.

## Update Control Implementation Information (I-2)

DT-1 confirmed that workstation and router events reach the enclave collector after
reconnect, and the planner and GDT logs still are not forwarded, with no committed date yet
[[INT-062.A1]] [[INT-063.A3]]. The full plan is drafted to the as-built configuration and under
ISSM review, to be signed before A-2; an incident response tabletop with the CSSP is scheduled
for the week of 2026-11-16 and has not run [[INT-063.A2]].
