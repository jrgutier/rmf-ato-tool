---
interview_id: INT-007
run_id: agent-cold-start-resume
task: C-2
persona: PER-IO
date: 2026-10-30
topics: [INF-01 impact levels]
---
# INT-007 — C-2 — PER-IO

### Q1 {#INT-007.Q1}
Asked of: PER-IO · Task: C-2
For INF-01 (sensor telemetry and alarms), do you confirm provisional confidentiality moderate?
**A1 {#INT-007.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#information]]
> I confirm moderate. Disclosure would show where our perimeter sensing is weak, which would
> seriously help an intruder plan a route, but it does not expose the whole installation.

### Q2 {#INT-007.Q2}
Asked of: PER-IO · Task: C-2
Do you confirm provisional integrity moderate for INF-01?
**A2 {#INT-007.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#information]]
> I confirm moderate. Tampering could hide an intrusion or raise false alarms at a site. That
> is a serious adverse effect, but the SOC still has guards, cameras and other sensing, so not
> severe or catastrophic.

### Q3 {#INT-007.Q3}
Asked of: PER-IO · Task: C-2
Do you confirm availability low for INF-01?
**A3 {#INT-007.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#availability]]
> I confirm low. Losing a site's feed is a limited effect: IODS flags a silent site within five
> minutes and we cover it with guard patrols, which we can sustain for several days.

### Q4 {#INT-007.Q4}
Asked of: PER-IO · Task: C-2
Is any of your information PII or classified?
**A4 {#INT-007.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]]
> No. Telemetry carries site and sensor identifiers, not people, and none of it is classified.
