---
artifact_id: ART-INFOTYPES
run_id: esg-c1-s4
produced_by_task: P-12
touched_by: [P-12]
sources: [product/conops.md#information, product/architecture.md#logging]
---
# Information types and life cycle — ESG

<!-- BEGIN rmf:facts -->
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
