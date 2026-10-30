---
artifact_id: ART-RA
run_id: agent-skeleton
produced_by_task: P-14
touched_by: [P-14, R-2]
sources: [product/conops.md#environment, product/conops.md#limitations]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
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

## Update after assessment (R-2)

| ID | Assessment result | Likelihood | Impact | Risk |
|---|---|---|---|---|
| TE-1 | confirmed by FND-001, FND-002 and STG-004 (shared `fieldtech` account); see RSK-002 | moderate | moderate | moderate |
| TE-2 | confirmed by FND-003 and STG-001 (two units 63 days behind on updates); see RSK-001 | moderate | high | moderate |
| TE-3 | not changed; physical protection was outside the assessed control subset | low | high | low |
| TE-4 | not changed; no finding bears on link loss | moderate | low | low |

The assessment confirmed the ratings of TE-1 and TE-2: the firewalls and CSSP monitoring held in
testing, which keeps likelihood at moderate, and the assessor's view of exploitability supports
the impact ratings [[INT-025.A1]] [[INT-025.A2]] [[INT-026.A1]] [[INT-026.A2]].
