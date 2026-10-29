---
artifact_id: ART-RA
run_id: agent-skeleton
produced_by_task: P-14
touched_by: [P-14, R-2]
sources: [product/conops.md#environment, product/conops.md#limitations, INT-032.A1, INT-032.A2, INT-032.A3]
---
# System risk assessment — ESG

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

<!-- Seeded for the walking-skeleton scenario (P-14 is out of scope). R-2 updates this
     assessment with the assessment results. Ratings use the SP 800-30 five-level scale. -->

## Threat sources and events

| ID | Threat event | Source | Likelihood | Impact | Initial risk |
|---|---|---|---|---|---|
| TE-1 | Insider or contractor misuses privileged console access without being identified | adversarial, insider | moderate | moderate | moderate |
| TE-2 | Attacker exploits a known vulnerability on a gateway that is behind on updates | adversarial, outsider on the installation network | moderate | high | moderate |
| TE-3 | Intruder tampers with a gateway in a remote shelter to suppress alarms | adversarial, physical | low | high | moderate |
| TE-4 | Radio jamming or link loss silences a site | adversarial or environmental | moderate | low | low |

Sources: the operating environment and the program's disclosed limitations
[[product/conops.md#environment]] [[product/conops.md#limitations]].

## Vulnerabilities and predisposing conditions

- A shared local account for field technicians removes individual accountability for
  privileged on-site actions (TE-1) [[product/conops.md#limitations]].
- Fielded units are updated only during quarterly visits, so a unit can run updates up to
  about 90 days old (TE-2) [[product/architecture.md#updates]].
- Remote sites are visited quarterly; tamper seals are checked only then (TE-3)
  [[product/architecture.md#physical]].

## Mitigating conditions

The enclave firewall, the deny-by-default host firewall and the CSSP's monitoring limit who
can reach a gateway over the network; IODS flags a silent site within 5 minutes
[[product/architecture.md#network]] [[product/conops.md#environment]].

## Update after assessment (R-2)

The control assessment confirmed TE-1 and TE-2 and changed none of their ratings
[[INT-032.A1]]:

| Threat event | Assessment result | Likelihood | Impact | Risk after assessment | Risk records |
|---|---|---|---|---|---|
| TE-1 | confirmed: shared fieldtech account (FND-001, FND-003, STG-004); stale shared password (FND-002) | moderate; low for a departed technician | moderate | moderate (RSK-001); low (RSK-002) | RSK-001, RSK-002 |
| TE-2 | confirmed: two units ran a 63-day-old bundle with 4 high vulnerabilities (FND-004, STG-001) | moderate | high | moderate | RSK-003 |
| TE-3 | not assessed: no control in the scoped subset covers physical tamper | low | high | moderate as seeded (Table I-2 gives low for low/high; for the next P-14 update to reconcile) | none |
| TE-4 | not assessed: no control in the scoped subset covers link availability | moderate | low | low (unchanged) | none |

TE-1 keeps moderate likelihood because the interim site-visit log is not yet assessed; the
departed-technician case is rated low because it needs the password and physical access to a
remote shelter within at most 90 days [[INT-032.A2]] [[INT-031.A2]]. TE-2 keeps moderate
likelihood: the firewalls and CSSP monitoring confine reachability, but the vulnerabilities
were observed, not just predicted [[INT-032.A3]] [[INT-031.A3]]. TE-3 and TE-4 keep their
initial ratings until an assessment covers them [[INT-032.A1]].
