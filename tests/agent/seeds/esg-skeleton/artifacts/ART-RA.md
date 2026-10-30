---
artifact_id: ART-RA
run_id: esg-skeleton
produced_by_task: P-14
touched_by: [P-14]
sources: [product/conops.md#environment, product/conops.md#limitations]
---
# System risk assessment — ESG

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Seeded for the walking-skeleton scenario (P-14 is out of scope). R-2 updates this
     assessment with the assessment results. Ratings use the SP 800-30 five-level scale. -->

## Threat sources and events

| ID | Threat event | Source | Likelihood | Impact | Initial risk |
|---|---|---|---|---|---|
| TE-1 | Insider or contractor misuses privileged console access without being identified | adversarial, insider | moderate | moderate | moderate |
| TE-2 | Attacker exploits a known vulnerability on a gateway that is behind on updates | adversarial, outsider on the installation network | moderate | high | moderate |
| TE-3 | Intruder tampers with a gateway in a remote shelter to suppress alarms | adversarial, physical | low | high | low |
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
