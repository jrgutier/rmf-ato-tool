---
artifact_id: ART-INFOTYPES
run_id: valid-minimal
produced_by_task: P-12
touched_by: [P-12, P-13]
sources: [product/README.md]
---
# Information types and life cycle

## Information types

FDR handles sensor reports and relay configuration data [[product/architecture.md#data-flow]].

## Identification

The information owner confirmed the two information types [[INT-021.A1]].

## Life cycle

Reports are purged 30 days after forwarding; configuration backups are kept one year
[[INT-022.A1]] [[product/program.md#information-life-cycle]].
