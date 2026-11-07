---
artifact_id: ART-BIA
run_id: esg-skeleton
produced_by_task: P-8
touched_by: [P-8, C-2]
sources: [product/conops.md#mission, product/conops.md#availability]
---
# Business impact and criticality analysis

## Mission critical functions

ESG senses and forwards alarms and makes no decisions; operators act on alarms through
systems outside ESG, so it supports no mission critical function
[[product/conops.md#mission]].

## Supported processes and disruption impact

BP-01, forwarding perimeter intrusion and environmental alarms to the installation SOC, has a
moderate disruption impact: an outage removes perimeter sensing at one site, which guard
patrols cover for several days. Its recovery time requirement is 72 hours, a replacement unit
on site, and it depends on the Installation Operations Data Service and the installation
network [[product/conops.md#availability]] [[product/conops.md#mission]].

## External dependents

No external stakeholder depends on the gateway's processes [[product/conops.md#mission]].

## Reevaluations

None yet: C-2 reevaluates the disruption impact against the availability impact.
