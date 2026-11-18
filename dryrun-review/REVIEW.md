# Dry run review: the fork workflow, end to end (2026-11-18)

> **FICTIONAL, SYNTHETIC.** The system, program, providers, people and every answer in this dry
> run are invented. The "authorization" was made by a simulated AO and authorizes nothing.

## Bottom line

The envisioned process works end to end on a system it had never seen. A fresh fork scaffolded
with `rmf new`, fed one product package, and carried by 16 cold-start agent sessions, produced a
complete draft DoD RMF package: every artifact AC-16 asks for, five OSCAL 1.2.1 documents that
validate, 216 traced interviews, an honest SAR and POA&M, and a simulated ATO with conditions.
State lived entirely on disk and survived a container restart mid-session.

It did not reach the 0-error bar (AC-18): `rmf check --final` ends with **1 error** (MRPT-001),
left on purpose because passing it would mean inventing network-operations coverage the product
does not support. Getting this far needed **three orchestrator rulings** to get past rules that
refused honest answers, and the run carries **27 assumptions** because the product template asks
for far less than the tasks consume.

The dry run recorded **220 findings** (3 blockers, 32 major, 112 minor, 73 notes; 19 of them
positive), in `dryrun-review/findings/`. Per the instruction for this run, **nothing upstream
was changed**: every defect is recorded for later.

## What was run

| Item | Value |
|---|---|
| Branch (acts as the fork) | `claude/project-thread-i5ojbm`, from main at `53fc0f0` |
| Target system | **Example Fleet Readiness Analytics Service (EFRAS)**, invented for this run. The docs name only the UAS ground station, which is already fully run as `examples/uas-gcs`; a new system tests the process on ground it has not seen. |
| System shape | cloud-hosted web app (IL4 PaaS), software acquisition pathway, maintainer PII, four leveraged authorizations (cloud region, access point, software factory, CSSP), seven disclosed weaknesses |
| Product package | `product/` (written by the orchestrator as a program office would hand it over): CONOPS, architecture, data flows, inventory, test results, privacy, stakeholders, one monitoring cycle |
| Run | `runs/20261118-synthetic-01`, synthetic mode, P-1 to R-5 plus M-1, M-2, M-3, M-5 (44 active tasks) |
| Controls | CNSSI 1253 M-M-L plus privacy overlay, cut to a **50-control subset** covering all 20 families (`baseline_id` CNSSI1253-M-M-L-SUBSET-50). A deviation: the schema marks `control_subset` as test-only (F-00-2). |
| Sessions | 16 general-purpose agent sessions, one RMF step or a slice of it each, with the brief in `dryrun-review/session-prompt.md` (adapted from `tests/agent/prompts/example-uas-gcs.md`); each wrote a findings file |
| Effort | about 5.5 hours of agent time, about 2,400 tool calls, about 3.7 M sub-agent tokens |

## The package

| | |
|---|---|
| Tasks done | 43 of 44 (M-5 open on MRPT-001 only); 3 deferred (M-4, M-6, M-7) |
| Artifacts | 30 `ART-*.md` plus their data files: ORG-CONTEXT, BIA, STAKE, INV, BND, INFOTYPES, RA, PIA, REQ, REG, SD, CAT, BASELINE, SSP, CMP, CP, IRP, SVCA, CONMON, STIG, SAP, AUTHREC, SAR, POAM, DIAS, RAR, AODM, AUTHRPT, CHG, SECRPT |
| OSCAL | `oscal/` profile, SSP, assessment plan, assessment results, POA&M; `rmf oscal validate`: 0 errors |
| SSP | 50 of 50 statements: 30 implemented, 14 partial, 4 planned, 2 inherited |
| Assessment | 28 satisfied, 22 other-than-satisfied; 24 findings at A-3 (9 moderate, 15 low, no CAT I), one more at M-2 |
| POA&M | 26 items (12 ongoing, 8 planned, 5 delayed, 1 risk-accepted) |
| Decision (simulated) | **ATO with conditions**, 2027-01-25 to 2028-01-25, overall risk moderate, six conditions (PIA approval, failover test, signed EMIS MOA, export de-identification, report container, leaver access); break-glass FIDO2 deviation risk-accepted |
| Traceability | 216 interviews, 533 answers all tagged SIMULATED, 27 assumptions (`reports/assumptions.md`) |
| `rmf check --final` | 1 error: MRPT-001 (F-16-2) |

The seven weaknesses the product disclosed all surfaced honestly: as partial statements in the
SSP, other-than-satisfied determinations in the SAR, POA&M items, RAR risks and decision
conditions. No weakness was hidden and none was invented.

## Where the process worked

- **Scaffolding and resume.** `rmf new` created the workspace in one command, and `rmf status`
  always named the next task with what it lacked. Every session started cold and resumed from
  disk; a container restart mid-session cost nothing (F-00-6, F-17-2).
- **Rules as a contract.** Most tasks passed `rmf check --task` on the first or second cycle,
  and sessions repeatedly called the rule messages precise and actionable (F-01-19, F-02-17,
  F-03-11, F-04-13, F-05-13, F-08-10, F-09-9, F-10-11, F-11-14, F-12-10, F-13-9, F-14-13,
  F-15-13, F-16-18).
- **Honesty holds under pressure.** When a rule demanded a false entry, every session stopped
  rather than fabricate it, and recorded "not demonstrated" under an assumption instead of
  inventing a pass (ASM-020 to ASM-024). The tagging and assumptions report made every invented
  value visible.
- **Breadth.** The framework covered the cloud case (DTM 24-001 activities, IL4 determination,
  CSSP agreement), privacy (overlay, PIA, Privacy Act records), C-SCRM and the software pathway
  without a single missing task.
- **Deterministic outputs.** OSCAL built and validated on every build; POA&M original dates froze
  at A-6 as documented.

## What got in the way, by theme

### 1. Rules and schemas that refuse an honest answer (3 blockers)

The process's core promise is honest drafts, but some rules can only pass with a false entry.

- **F-02-1 (blocker):** `scrm.yaml criticality.functions` needs at least one mission-critical
  function, while the BIA found none and SCRM-002 accepts none. Workaround CF-01 cascaded into
  two supplier risk assessments, a focal point and a TAC request the program does not need
  (F-03-1, ASM-012).
- **F-05-1 (blocker):** MLEV-001 counts only fully inherited (`common`) allocations, so a
  provider of hybrid controls fails, and the error is charged to C-1. Workaround: re-record three
  providers' arrangement, which pulled in RECIP-001 package reviews (F-06-1) and left one provider
  with three different roles that no rule noticed (F-08-1).
- **F-05-2 (blocker):** TLR-009 needs a control for every requirement, including Section 508 and
  the DoD IT Standards Registry, which no control satisfies. Workaround: trace both to SA-11
  (F-06-3).
- Same pattern, not blocking: a draft PIA cannot be recorded (F-02-9, F-15-10), "no weakness"
  is refused on low-risk connections (F-02-2), independent assessors cannot record "examined and
  re-performed" developer results (F-11-3), a held partial pen test cannot be recorded (F-11-6),
  CNSSP 15 and classified reporting are forced on a non-NSS (F-09-5), DODIN awareness areas no
  output owns (F-16-2).

### 2. Checks that hide errors or charge them to the wrong task (major)

The loop "check until 0 errors" is only as good as what `check` shows.

- A plain `rmf check` reports 0 while earlier or current tasks fail (F-02-3, F-05-3).
- `rmf check --family` hides PVAL-001, INT-001 and ASMT-005 in the family's own file, so the
  S-4 and A-3 batching loop reports 0 on failing work (F-06-4, F-12-6, F-13-1).
- Rules charged to the wrong task: PIIF-001 to P-11 (F-02-3), an exact-name match charged to P-2
  (F-04-1), MLEV-001 to C-1 (F-05-1), MPLAN-001 to M-4 (F-10-2), A-1 rules that read an A-2 file
  so `--task A-1` can never fail (F-11-1).
- Later tasks silently break earlier ones and `rmf status` sends the run backwards (F-09-1,
  F-15-5, F-16-13); Prepare checks need S-4 outputs (F-03-2, F-04-2).

### 3. The contract lives in code, not in the playbooks (major, high cost)

Almost every session read rule source or schemas to learn which fields a record needs (F-01-13,
F-03-10, F-08-5, F-11-10, F-15-4, F-15-6). Data templates are missing for infotypes, tailoring,
allocation and conmon (F-02-8, F-05-7, F-09-2); templates carry a sixth front-matter key the
protocol forbids (F-10-6, F-13-4); playbooks and templates disagree on headings and outputs
(F-03-3, F-03-5, F-14-3, F-15-8). Persona cards lack question banks for most tasks where the
persona is responsible (F-01-12, raised again in ten sessions). This is the largest single cost
driver (F-17-3).

### 4. The product template asks for far less than the run needs (major)

The template has no stakeholders or privacy file (F-00-3) and asks for no organizational
policy, threat, capability, PPP, cybersecurity strategy, test strategy, STIG rule IDs, cloud
responsibility data or registry identifiers (F-01-2, F-02-12, F-03-9, F-04-8, F-08-4, F-10-1,
F-11-8). The result: 27 assumptions, and about 150 values in `cloud.yaml` resting only on
simulated answers. In a hybrid run these are exactly the documents a program must hand over.

### 5. Consistency the checker does not catch (major)

Rules pass on wrong input in several places: an SSP `partial` or an open STIG finding can sit
beside a SAR `satisfied` (F-12-1); a statement promising a plan is not tied to the plan (F-07-1);
a STIG finding's control is not tied to its SSP status (F-10-7); whether the system is an NSS
has no single home and the run disagreed with itself (F-03-4, F-04-5); PVAL-001 checks only the
first value and skips unbounded ones (F-06-5, F-08-6).

### 6. Time does not move in a synthetic run (major)

The run's clock stays at its start date while the plan schedules assessment weeks ahead and the
date rules push the decision two months later. Sessions had to simulate POA&M progress under one
uniform assumption (ASM-025), and the only monitoring data predates the authorization (F-12-2,
F-14-6, F-15-1, F-16-1, F-17-5).

### 7. Fork tooling (major)

- `scripts/agent-run.sh` refuses a run under `runs/`, so it cannot drive a fork's own run, and
  it needs the Claude Code CLI despite the agent-agnostic goal (F-00-1).
- `rmf ci --profile fork` passes while the fork's run fails: no step checks `runs/*/` (F-17-1).
- No supported rehearsal scope for a fork (F-00-2); `baseline resolve` silently drops S-2 adds
  outside the subset (F-05-5).

### 8. Cloud and software-pathway fit (minor)

The software pathway must pick an MCA phase (F-00-4, F-04-11); there is no value for a DoD
provisional authorization (F-01-7); the cloud offering must be an `external-service` while being
the only common control provider (F-06-2); assessment evidence comes from pre-production, which
is outside the boundary, and nothing records it (F-11-9, F-12-7).

## Recommendations, in order

1. **Unblock honest answers.** Fix the three blockers (F-02-1, F-05-1, F-05-2), then sweep the
   schemas for `minItems: 1` and required approval fields that forbid "none yet" or "draft"
   (F-02-2, F-02-9, F-09-3, F-11-3). Add a positive fixture for each honest empty case.
2. **Make `check` trustworthy for the loop.** A plain `rmf check` should report errors in done
   and current tasks; `--family` should include every rule judging that family's files; charge
   each rule to the task that writes the record it reads. Then add `rmf ci --profile fork` a step
   for `runs/*/` (F-17-1).
3. **Move the contract into the docs.** Generate each playbook's "Done when" and a complete
   `templates/data/*.yaml` from the rules and schemas (the way playbook headers are already
   synced), add `rmf schema show`, and fill the persona question banks per task.
4. **Expand the product template** to the documents tasks consume: stakeholders, privacy, org
   policy and threat, capability and test strategy, PPP and cybersecurity strategy, leveraged
   service responsibilities, STIG checklists. Each gap became an assumption here.
5. **Add the missing cross-artifact checks**: SSP status vs SAR determination, STIG findings vs
   SSP, a single NSS determination, statements vs the plans they promise.
6. **Give synthetic runs a clock** that the date rules read and the journal records.
7. **Fork tooling:** a fork mode in `agent-run.sh` with a generic, editable prompt, and a
   documented rehearsal scope.
8. Then the minor and doc findings, file by file.

A second dry run in **hybrid** mode, or with the full baseline, is worth doing once items 1 to 3
land; it would measure how much those fixes cut the cost per task.

## Caveats about this dry run

- The orchestrator wrote the product package, so it is cleaner than a real program's material.
- 50 controls instead of about 500; sessions covered up to 13 families instead of 3.
- Three in-run workarounds were orchestrator rulings (F-02-1, F-05-1/F-06-2, F-05-2); they are
  marked in the run's assumptions and journal.
- Sessions often used Python or grep in Bash and targeted edits rather than whole-file writes,
  against the brief and INV-8, mostly to find what the playbooks did not say (F-17-4). Each
  file was whole and valid after the edit.
- `docs/LESSONS.md` was not touched; the lessons are in the findings files instead.

## Index

| File | Session unit | Findings |
|---|---|---|
| `findings/00-setup.md` | setup, product, scaffolding | 6 |
| `findings/01-prepare-org.md` | P-1 to P-9 | 19 |
| `findings/02-prepare-system.md` | P-10 to P-13 (P-14 blocked) | 18 |
| `findings/03-prepare-finish.md` | P-14 to P-18 | 12 |
| `findings/04-categorize.md` | C-1 to C-3 | 14 |
| `findings/05-select.md` | S-1, S-2 (S-3 blocked) | 14 |
| `findings/06-s3-s4a.md` | S-3, S-4 batch 1 | 10 |
| `findings/07-s4b.md` | S-4 batch 2 | 7 |
| `findings/08-s4c.md` | S-4 batch 3, cloud, agreements | 11 |
| `findings/09-s4-plans-s5-s6.md` | S-4 plans, S-5, S-6 | 9 |
| `findings/10-implement.md` | I-1, I-2 | 12 |
| `findings/11-assess-plan.md` | A-1, A-2 | 15 |
| `findings/12-a3a.md` | A-3 batch 1 | 11 |
| `findings/13-a3b.md` | A-3 batch 2 | 10 |
| `findings/14-a4-a6.md` | A-4 to A-6 | 14 |
| `findings/15-authorize.md` | R-1 to R-5 | 14 |
| `findings/16-monitor.md` | M-1, M-2, M-3, M-5, final check | 19 |
| `findings/17-orchestrator.md` | fork CI, orchestration | 5 |
