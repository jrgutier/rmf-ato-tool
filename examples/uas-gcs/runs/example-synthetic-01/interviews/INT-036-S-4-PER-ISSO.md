---
interview_id: INT-036
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [ac family, account lifecycle, account reviews, privileged use]
---
# INT-036 — S-4 — PER-ISSO

### Q1 {#INT-036.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2, ac-2.1, ac-2.3, ac-2.13, ac-6.7
How are accounts requested, approved, disabled and reviewed on the station?

**A1 {#INT-036.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#account-review]]
> CAC users get access only through the brigade directory groups `operator`, `commander` and
> `admin`; I approve every group membership and the brigade S6 creates, disables and removes the
> directory accounts, so a departing or high-risk user is cut off as soon as S6 disables the
> directory account and the 14-day cached sign-in expires or the station reconnects. I review
> all station accounts and privileges quarterly; the last record is 2026-09-08: 14 CAC accounts,
> 6 sealed break-glass accounts unused, and the shared `gcsmaint` account used by 5 maintainers.

### Q2 {#INT-036.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2, ac-2.7, ac-2.9, ac-2.2
What about the local, shared and emergency accounts?

**A2 {#INT-036.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> `gcsmaint` is a shared privileged local account on the workstation and the router; the
> platoon's maintainers share the password and it changes every 60 days and whenever a
> maintainer leaves the platoon. Its actions cannot be tied to a person, which I referred to the
> program office; release 2.4 (planned 2027-02) replaces it with per-maintainer local accounts
> and offline CAC sign-in. The GDT management web service also has one vendor administrator
> account per station. The break-glass account is sealed, held by the platoon leader, and its
> password is reset and the seal renewed after any use.

### Q3 {#INT-036.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2.4, ac-2.12, ac-6.9
Which account and privileged events are logged, and who looks at them?

**A3 {#INT-036.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-1]]
> The workstation OS logs account creation, changes, lockouts and privilege use and the router
> logs administrative sessions; both forward to the enclave collector when the uplink is up, and
> brigade S6 reviews it there. The GDT keeps its administrator events in a local log that is not
> forwarded. While a station is disconnected for days nobody reviews for atypical use until the
> logs reach the collector; I only review a weekly station report during test events.
