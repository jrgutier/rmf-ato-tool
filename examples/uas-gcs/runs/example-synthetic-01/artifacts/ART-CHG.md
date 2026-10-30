---
artifact_id: ART-CHG
run_id: example-synthetic-01
produced_by_task: M-1
touched_by: [M-1]
sources: [INT-107.A1, INT-107.A2, INT-108.A1, INT-108.A2, ART-CONMON, ART-CMP, product/architecture.md#updates, product/test-results.md#vuln-scan, product/conops.md#limitations]
---
# Change log and security impact analyses

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## Monitoring scope and sources

This log covers the first simulated continuous monitoring cycle after the authorization of
2026-10-29, run under the strategy in ART-CONMON: changes reach the stations only through the
configuration control board and the integrator's signed quarterly bundles [[ART-CONMON]]
[[ART-CMP]] [[product/architecture.md#updates]]. Sources were the open change requests, the
2026-09-15 vulnerability scan that the bundles answer, and the board's decisions
[[INT-107.A1]] [[INT-108.A1]] [[product/test-results.md#vuln-scan]].

## Change log

| Change request | Date | Change | Requested by | Security impact result | Board decision | Referred to the AO |
|---|---|---|---|---|---|---|
| CR-2026-10 | 2026-10 | quarterly bundle: operating-system and router patches for the 3 medium scan findings | integrator (PER-DEV) | positive; not significant | approved for the six test stations, signature check at install and scan before next mission upload | no |
| CR-2026-12 | 2026-12 (planned) | bundle with GDT firmware 5.2.1 (INV-007) | integrator (PER-DEV) | positive; not significant | approved for regression testing only; installation decided on the test report | no |

Both rows rest on [[INT-107.A1]] and [[INT-108.A1]]. No change was installed outside these
requests [[INT-107.A1]].

## Security impact analyses

- **CR-2026-10.** Patches existing workstation and router items; no boundary, interface or
  data-flow change. It reduces the three medium findings; the risk it introduces is an
  untested configuration on a station, which the board controls with the signature check and
  the scan before the next mission upload. Controls affected: cm-3, cm-4, si-2, ra-5
  [[INT-107.A1]] [[INT-108.A1]] [[product/test-results.md#vuln-scan]].
- **CR-2026-12.** Replaces GDT firmware 5.1.8 with 5.2.1, which fixes the management web
  service flaw the vendor rates high. Until installed, the flaw stays mitigated only by keeping
  the service on the station internal network. Regression testing guards flight-path behavior
  before install. Controls affected: si-2, ra-5, cm-2, cm-3; the AO condition COND-02 depends
  on it [[INT-107.A1]] [[product/conops.md#limitations]].
- **Significant changes ahead.** Release 2.4 (per-maintainer accounts with offline CAC sign-in,
  planned 2027-02) changes how maintainers authenticate, and the release 3.0 planner
  replacement changes a component; both go to the AO through the ISSM before reaching a
  station, and the planner replacement re-enters the RMF at P-11 and C-1. Neither has a change
  request yet [[INT-107.A2]].

## Changes in the environment of operation

None in this cycle: no new interconnection, site or mission, and no threat change from the
enclave. The IC-1 agreement is still unsigned, and the board holds any change to that interface
until it is signed [[INT-108.A2]].

## Resulting updates

The inventory and the configuration management plan record the two requests (ART-INV and
ART-CMP, M-1 sections); `inventory.yaml` changes only when CR-2026-12 is installed. The scan
results of CR-2026-10 feed the ongoing assessment (M-2) and the POA&M (M-3). No change needs a
reauthorization decision in this cycle [[INT-107.A2]] [[INT-108.A1]].
