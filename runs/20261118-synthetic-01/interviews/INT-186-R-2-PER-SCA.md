---
interview_id: INT-186
run_id: 20261118-synthetic-01
task: R-2
persona: PER-SCA
date: 2026-12-17
topics: [exploitability of findings, compensating factors observed, confidence in the evidence]
---
# INT-186 — R-2 — PER-SCA

### Q1 {#INT-186.Q1}
Asked of: PER-SCA · Task: R-2 · Control focus: pt-3, ra-5, si-2
Which findings are exploitable today, and by whom?
**A1 {#INT-186.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[INT-171.A2]] [[product/test-results.md#pentest]] [[product/test-results.md#pipeline-1-5]]
> Two are proven or near-proven. FND-018: the red team and our privacy-trained assessor
> re-identified maintainers from 50 DoD ID numbers; anyone with an export and a roster can do
> it, so with real data it would be certain, not hypothetical. FND-019 and FND-024: the two
> imagelib highs are public, past the 30-day window, and reachable by any signed-in user
> through the report renderer, which has no outbound access; I would rate exploitation more
> likely than the P-14 assessment did, because the fix has slipped twice and the user base is
> about 3,000. The rest need an insider or a failure: the leaver accounts (FND-001, FND-017)
> are a real path for a departed maintainer who still holds a CAC for up to 35 days; the
> database STIG settings and the undocumented container configuration matter only if
> something else goes wrong first.

### Q2 {#INT-186.Q2}
Asked of: PER-SCA · Task: R-2 · Control focus: cm-6, ac-2, ps-4
Which weaknesses did you find that the risk assessment does not hold, and what compensates?
**A2 {#INT-186.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[INT-174.A3]] [[INT-161.A1]] [[ASM-021]]
> Two. The leaver gap: no departure notice reaches the account manager; the 35-day inactivity
> disable and the quarterly review are the only backstops, and CAC turn-in helps only once the
> person actually leaves the base. And the five application containers have no documented
> secure configuration, so nobody can say whether a setting drifted; signed images and
> admission control limit what can run, but not how it is configured. My confidence in the
> evidence is moderate overall: everything was tested in pre-production with synthetic data
> built from the production templates, which I trust for configuration but not for volume.
