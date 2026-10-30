---
interview_id: INT-068
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [ac assessment evidence, account reviews, shared accounts, account monitoring]
---
# INT-068 — A-3 — PER-ISSO

### Q1 {#INT-068.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2, ac-2.2, ac-6.7
Show the evidence of account approval and review.

**A1 {#INT-068.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]]
> Here is the 2026-09-08 quarterly review record: 14 CAC accounts on the six stations, each
> with my signed group-membership approval; 6 sealed break-glass accounts with intact seal
> numbers and no use; the directory group exports from S6 match the station role mapping. The
> previous quarter's record is dated 2026-06-09.

### Q2 {#INT-068.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2, ac-2.7, ac-2.9, ac-6.9
Can maintenance actions be tied to a person today?

**A2 {#INT-068.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#account-review]]
> No. Five maintainers share `gcsmaint` on each workstation and router, and the GDT has one
> vendor administrator account. The OS and router logs show `gcsmaint` but not who used it,
> and GDT administrator events stay in the GDT's own log. The paper maintenance log names the
> maintainer for scheduled work only. The fix is per-maintainer accounts in release 2.4,
> planned for 2027-02.

### Q3 {#INT-068.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2.12
Who reviews account use while a station is disconnected?

**A3 {#INT-068.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#environment]]
> Nobody, during disconnected periods. S6 reviews the collector once logs arrive after
> reconnect. My weekly station report exists only during test events so far; it is not yet
> in operational use.

### Q4 {#INT-068.Q4}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-7, ac-8, ac-11, ac-17
Show the settings for lockout, banner, session lock and remote access on a station.

**A4 {#INT-068.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[product/test-results.md#stig-scan]]
> On station 3 in front of you: the workstation policy shows lockout after 3 failures, the
> DoD notice and consent banner at sign-in, and the 15-minute screen lock with a blank image;
> Wi-Fi and Bluetooth are off in firmware. The router configuration shows SSH only from the
> S6 management subnet, admin role required, idle timeout 15 minutes, logging to the
> collector. The 2026-09-15 STIG scan has no open findings on these settings.
