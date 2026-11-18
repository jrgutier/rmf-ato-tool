---
interview_id: INT-061
run_id: 20261118-synthetic-01
task: C-2
persona: PER-IO
date: 2026-11-18
topics: [impact values INF-01 INF-03 INF-04, consequences of compromise, PII, classification]
---
# INT-061 — C-2 — PER-IO

Respondent: the fleet maintenance data steward, information owner of INF-01, INF-03 and INF-04.

### Q1 {#INT-061.Q1}
Asked of: PER-IO · Task: C-2
INF-01, maintenance and readiness data: do you confirm confidentiality moderate, integrity
moderate and availability low?
**A1 {#INT-061.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-027.A2]] [[ART-INFOTYPES]] [[product/conops.md#information]]
> I confirm all three. Disclosure of the aggregated data shows an adversary the fleet's
> readiness trends: a serious adverse effect, so moderate. Tampering could hide degraded
> readiness or send money after the wrong parts: serious again, moderate, and integrity is my
> first concern. Loss for up to 72 hours is a limited effect, because EMIS keeps the source
> records and its reports are the fallback: low.

### Q2 {#INT-061.Q2}
Asked of: PER-IO · Task: C-2
INF-03, maintainer PII: do you confirm confidentiality moderate, integrity moderate and
availability low, the last adjusted down from the provisional moderate?
**A2 {#INT-061.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-027.A3]] [[ART-INFOTYPES]] [[product/privacy.md#pii]]
> I confirm. Disclosure of names with DoD ID numbers for 30,000 people enables phishing and
> identity misuse: serious, moderate. A wrong qualification or work-center record could put the
> wrong person on a job in our views: moderate. I keep the availability adjustment to low: this
> is a copy, EMIS holds the authoritative records, and losing our copy for days harms no
> individual and no mission.

### Q3 {#INT-061.Q3}
Asked of: PER-IO · Task: C-2
INF-04, forecasts and reports: do you confirm confidentiality moderate, integrity moderate and
availability low?
**A3 {#INT-061.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-027.A4]] [[ART-INFOTYPES]]
> I confirm. The forecasts and reports reveal the same trends as the data they come from, and a
> tampered forecast misleads part orders and briefings, so moderate for both. A missing forecast
> delays early ordering by a day or a week; officers order on the usual signals: low.

### Q4 {#INT-061.Q4}
Asked of: PER-IO · Task: C-2
Is any of your information classified, is anything missing from the list, and does anything
other than INF-03 hold PII?
**A4 {#INT-061.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[INT-059.A2]]
> None of it is classified; it is all CUI. Nothing is missing. Only INF-03 holds PII among my
> types, and that includes the "de-identified" exports and the training extract, which I treat
> as PII until release 1.6 salts the pseudonyms.
