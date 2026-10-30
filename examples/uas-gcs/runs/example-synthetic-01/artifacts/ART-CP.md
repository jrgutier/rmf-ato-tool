---
artifact_id: ART-CP
run_id: example-synthetic-01
produced_by_task: S-4
touched_by: [S-4, I-2]
sources: [product/conops.md#availability, product/conops.md#environment, product/architecture.md#network, INT-063.A2]
---
# Contingency plan

## Plan summary

The plan covers loss of a station kit in the field. The recovery objective is a replacement
station operating within 4 hours [[product/conops.md#availability]]. The strategy is to draw
a spare kit from brigade stock, restore it from the signed baseline image and the mission
data, and resume planning and flight control; the platoon tolerates a few hours' outage by
moving a spare from another platoon. When the uplink is down the station keeps flying and
recording and queues products for later transfer [[product/architecture.md#network]], and a
lost aircraft link triggers the pre-loaded lost-link route [[product/conops.md#environment]].
Training and the first test are planned before fielding.

## Update Control Implementation Information (I-2)

The full contingency plan is drafted to the as-built 2.3.0 configuration and is under the
ISSM's review, to be signed before A-2 as the S-6 conditions require [[INT-063.A2]]. The
restore source is the signed 2.3.0 baseline image recorded in the STIG summary [[ART-STIG]].
The first test, a tabletop, is scheduled for the week of 2026-11-16 and has not run, so no
test result exists yet [[INT-063.A2]].
