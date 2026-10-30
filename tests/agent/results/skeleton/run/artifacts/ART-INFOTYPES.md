---
artifact_id: ART-INFOTYPES
run_id: agent-skeleton
produced_by_task: P-12
touched_by: [P-12]
sources: [product/conops.md#information, product/architecture.md#logging]
---
# Information types and life cycle — ESG

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

<!-- Seeded for the walking-skeleton scenario (P-12 and P-13 are out of scope). The
     structured values, including the life-cycle stages, are in
     `artifacts/data/infotypes.yaml`. -->

## Information types

ESG handles three information types; their provisional impact levels come from SP 800-60
Vol. 2 [[product/conops.md#information]]:

| ID | Information type | SP 800-60 | C | I | A | Adjustment |
|---|---|---|---|---|---|---|
| INF-01 | Perimeter and environmental sensor telemetry and alarms | C.3.1.3 Security Management | moderate | moderate | low | none |
| INF-02 | ESG configuration and security management data | C.3.5.5 Information Security | low → **moderate** | moderate | low | C raised: private keys and firewall rules [[product/architecture.md#identity]] |
| INF-03 | ESG audit records | C.3.5.8 System and Network Monitoring | moderate | moderate | low | none |

## Privacy

None of the types contains PII beyond user names in account and audit records; the
program has asked the privacy office to confirm this [[product/conops.md#information]].

## Information owners

The installation security operations organization owns INF-01; the ESG program owns INF-02
and INF-03 [[product/conops.md#mission]].
