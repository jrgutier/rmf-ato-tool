# ADR-0005: record acceptance criteria from AC-24 here

Date: 2026-10-31 · Status: accepted · Phase: 8

## Context

AC-1 to AC-23 are defined in the original plan under `.omc/plans/`, which is gitignored.
The coverage work (`docs/audits/2026-10-31-coverage-audit.md`) adds rules, and every rule in
`src/rmf_tool/check/registry.yaml` names an AC.

## Decision

Acceptance criteria from AC-24 on are defined in this ADR, one line each, and extended in
later phases by appending below. A rule that cites an AC points here.

| AC | Phase | Criterion | Rule |
|---|---|---|---|
| AC-24 | p8 | The counts that README.md, AGENTS.md and the registry header state equal the values computed from the registry, framework and reference index | DOC-002 |
| AC-25 | p9 | The framework cites no PDF reference that is `required: false` | FW-CITE-003 |
| AC-26 | p9 | Every pinned PDF states an exact revision, and a `revision_stamp` points at the passage in the text that shows it | REF-007 |
| AC-27 | p9 | Every control in the pinned OSCAL catalog is in the text of the three SP 800-53 PDFs or declared in the entry's `oscal_only_controls` | REF-008 |
| AC-28 | p10 | Every task holds the entities its SP 800-37r2 Chapter 3 block maps to, or a waiver names the open work item that closes the gap; the SDLC note matches the block | FW-TASK-002 |
| AC-29 | p10 | The register has the declared shape, every PDF and web reference has a source whose scopes and exclusions cover every page with a reason, every citation resolves and every statement is in its cited passage | FW-REQ-001 |
| AC-30 | p10 | Every evidence entry resolves and is linked both ways (a rule lists the entries it enforces, a pin names a non-identity field, `asserts` shares the statement's vocabulary and a token of the failing message or the property's title, `sentence` equals one marked sentence of the statement, whole, a declared `claim` agrees with the judge's classification), `covered` rests on evidence that can fail and a distinct strong item cites each marked sentence of an entry with several, of any kind, and no target of any kind exceeds its fan-out cap without a reviewed exception | FW-REQ-003 |
| AC-31 | p10 | Every `partial`, `deferred` and `not-applicable` entry has a reason and `partial` carries at least one evidence item; a `deferred` tier 1 entry records `approved_by: user`; a reviewed entry that left its source records `removal_reason`; triage patterns are document-scoped, specific, capped, sampled and never on tier 1; a document over a quarter retired (not-applicable, deferred or partial on evidence that cannot fail), however its statuses were set, has a `retirements` record approved by the user; every register work item binds entries; `closed` means every entry covered on evidence that judges strong, `closed-partial` leaves honest partials none of them tier 1, and an open item cannot have every entry covered | FW-REQ-004 |
| AC-32 | p10 | Each source text matches the hash reviewed in `conformance/text-hashes.yaml`, so any edit to a document fails until it is re-reviewed and accepted; an offline re-extraction equals the register; every scope yields entries or says why not; no entry awaits review | FW-REQ-005 |
| AC-33 | p10 | A revision agrees with what its document says about itself wherever that sits: the anchor holds the revision's latest full date, and the highest `Change N` with its date, the `INCLUDES UPDATES AS OF` date and the last errata date are all named, unless a `revision_source` reason exempts the entry | REF-007 |
| AC-34 | p10 | Extraction noise is marked `not-a-requirement` with a reason, and is not counted in a document's retired share, which measures real requirements only; a noise entry whose statement holds one of the extractor's duty phrases (`MODAL`, `SHOULD`) has a reason that uses that phrase and says why it binds no one. That check is a speed bump: a reason can repeat the word and lie. The semantic check is the sampled audit (`rmf conformance sample --status not-a-requirement`), not the rule. A document over half noise needs a `noise` record approved by the user Noise and retired entries together over half of a document's live entries need a retirements record. | FW-REQ-004 |
| AC-35 | p11 | A termination date follows its decision, stays inside the type's term limit and is absent where the type forbids one, and ongoing authorization records its time-driven frequency, event triggers and the AO's acknowledgment | AODM-002 |
| AC-36 | p11 | An ATO at High or Very High risk records the Component CIO's concurrence or non-concurrence, dated before the decision, with directions on a non-concurrence | AODM-003 |
| AC-37 | p11 | An ATO records the Intelligence Community threat assessment issued within the 12 months before it and reviewed by the PM | AODM-004 |
| AC-38 | p11 | A record that modifies, continues, revokes or replaces another names one that exists, is earlier and is in force on its date; a cATO or continuation leaves the ATO in the ledger; an authorization to use names the provider's completed ATO; a new AO cannot extend the termination date | AODM-005 |
| AC-39 | p11 | A test event on a live network or with live data falls under an IATT or authorization in force on its date | AODM-006 |
| AC-40 | p11 | A cATO rests on an ATO, records the Component CISO notice and the DoD CISO approval before the decision, and is on an allowed pathway and product kind | AODM-007 |
| AC-41 | p11 | A run is held to the framework contract it was created under, an older run gets one warning naming the difference, and `--release` fails unless the example is on the current contract | RUN-VER-001 |
| AC-42 | p11 | Each record is decided by the official of its type, on a subject the type applies to, and conveyed to the system owner or common control provider | AODM-009 |
| AC-43 | p13 | At the freeze no tier 1 entry is a candidate and every tier 1 partial carries an evidence item that judges strong; candidates outside tier 1 warn, and open work items do not block | FW-REQ-002 |

## Consequences

- `docs/CHECKS.md` lists AC-24 for DOC-002, and this file says what it means.
- An AC is never renumbered or reused (INV-3).

## FW-REQ-002 at p13: what `candidate` and a later import mean

Recorded at p10 so p13 implements it without redesign; nothing in p10 prevents it.

- p13 freezes the reference set: the `ref` list of `conformance/sources.yaml` at the freeze
  commit, recorded as `conformance/frozen.yaml` (`refs: [...]`, `frozen_at: <commit>`).
- FW-REQ-002 fails the freeze on any live `candidate` entry of a frozen reference whose
  document is `tier: 1` or whose kind states an obligation (`lettered`, `modal`, `indicative`,
  `imperative`, and every pin field), and on any open register work item. A `should` or
  `table` candidate in a document without `tier: 1` (most documents carry no tier) warns and
  stays listed as untriaged. The split is `report.blocks_freeze` (now `rules.blocks_freeze`) and
  `rmf conformance report` prints the three counts now, so the p13 workload is visible from p10.
- An entry of a reference imported after the freeze (a fork's import, or a T2 document that
  arrives later) is a warning through profile severity, like `agent_severity`: `E` under
  `release`, `W` under `fork`. Such entries stay unassessed and are never reported as covered;
  `rmf conformance report` lists their references under `unassessed`.
- The register, the pin and `text-hashes.yaml` already distinguish the two cases (a reference
  is in or out of the frozen list), so the rule needs only the frozen list and the severity
  lookup `profiles.py` already provides.

## Decisions taken with the user, 2026-10-31

- FW-REQ-002 at p13: every tier 1 entry and every obligation must be triaged or the freeze
  fails. `should` and `table` entries in a document without `tier: 1` warn and stay listed as
  untriaged, so the tool reports them as not reviewed.
- cATO authority: the sources conflict (DoDI 5000.90 lets the AO authorize; the cATO memo has
  the DoD CISO approve). AD-CATO stays an AO decision, and AODM-007 will also require a
  recorded DoD CISO approval, which satisfies both.
- p14 adds a lifecycle scenario through M-4, M-6 and M-7, so all 47 tasks run in an agent
  session.
- Extraction is a first pass. Triage reads whole pages and promotes misses with
  `rmf conformance promote`; recall is reported as a measured figure across fresh seeds.

## Decisions taken with the user, 2026-11-01

- The 25% limit counts real requirements only. It was set when entries were assumed to be
  requirements; about 27% are extraction noise, so nearly every document tripped it and the
  approvals it forced would have said nothing. `not-a-requirement` separates noise from
  `not-applicable`, a real requirement the tool has nothing to hold it with.
- Noise has its own limit, half of a document's live entries, with a `noise` record approved
  by the user above it. Without one a document could be turned to noise whole and pass. It is
  not 25%: noise runs to 40% of a document, and the user chose not to approve junk one
  document at a time.
- Acquisition process is modelled at its RMF touchpoints only: what a run consumes or produces.
  A purely acquisition duty is deferred with a reason, and a tier 1 deferral still needs
  approval. This narrows "everything in the documents" for acquisition process alone.
- Triage runs on Opus throughout, after a pilot in which Sonnet wrongly retired 3 of 185 real
  requirements and Opus none of 214.
- The DoD 5000 series may exceed the 25% limit where that comes solely from the touchpoints
  decision. The user approved this for DoDI 5000.02, 5000.74, 5000.75, 5000.80, 5000.81, 5000.82,
  5000.83, 5000.85, 5000.87, 5000.88, 5000.89 and 5000.90, each with its own record in
  `conformance/policy.yaml`, listed at p13 and reversible there. It does not extend to any other
  document, to entries retired for another reason, or to tier 1 deferrals.
- A document over either limit gets its record when Fable's audit confirms it on merit, under
  this standing approval from the user, and every such record is listed for reversal at p13.
  Anything Fable cannot confirm stops for the user. Tier 1 deferrals are not covered.
- The tool models only what a run uses: when a run consumes an outside body's output, the duty that
  shapes that output stays, and that body's internal procedure is not-applicable.

## Decisions taken with the user, 2026-11-01 (p11)

- `rmf_tool.run.authorization.in_force` is the one reading of what stands on a date. `AD-CONT` and
  `AD-CATO` lift the termination date by attaching to their ATO, so revoking either restores it.
- A run older than a rule's `since` is not held to it. Rules read the ledger through one loader, so
  a pre-ledger run's `decision.yaml` is lifted in memory by the conversion `rmf run migrate` writes.

## The evidence bar, decided with the user 2026-11-02

Fable's review of the pilot found 25% of sampled `covered` did not hold: `covered` could rest on a
word overlap and one fixture per rule. The user set the bar: tier 1 gets full proof, everything else
an honest `partial` citing where it is built, and the freeze accepts that.

- `covered` means a real test fails if the duty is broken.
- A rule item carries `fixture` (a negative fixture) and `expect` (a literal fragment of the failing
  message). FW-REQ-003 checks that the fixture's `rule` is that rule, listed in
  `expect.errors`, that it declares that fragment in `expect.messages`, and that it sits in one failing call of the rule's source with the
  same-module helpers it calls. `test_negative` proves messages for the fixture's own rule only, so
  an `also` rule needs its own fixture. `expect` holds two content words or equals one declared
  message whole. `test_negative` proves the fixture fails with it, so FW-REQ-003 stays static. A
  fixture named `<RULE>.<clause>.yaml` is one clause of a rule. One fixture proves one clause: two
  sentences of an entry share a fixture only with two distinct messages.
- `asserts` carries a token of `expect`, or of the property's title on a schema item, as well as the
  word overlap with the statement.
- Every item carries `claim: presence|constraint`. Presence caps at `partial` on prose kinds and
  may be `covered` on the `table` kind only. The judge classifies schema items itself (enum, const,
  pattern, format, numeric bounds and minItems are constraint; the rest is presence) and rule items:
  a fixture that only deletes, or a clause whose tests read that a value is absent (found in the
  rule's AST: `not x`, a comparison of a plain field read with None, "", 0 or an empty container,
  `len(x) == 0`, `x in (None, "")`, or the `else` of a truthiness test), is presence; the rest is
  constraint, including a lookup that finds nothing. With no clause to read it is presence. A
  declared claim that disagrees is an error. The
  cap goes by kind, so a `lettered` entry with no marked sentence is not a table row.
- A `pinned` item is strong only with `read_by` naming a rule item of the entry, on the same
  sentence, whose rule reads the field; on an entry with several marked sentences both must name the
  same one. A pin beside a rule item capped at presence stays weak. A schema item is held only if
  every property above it is required, or `read_by` names such a rule making the optional parent
  present.
- A field a decision type lists in `requires` is held by the triple pin, rule clause and schema
  shape, each judging strong on the same sentence, and the rule leg's fixture breaks that field;
  fewer is `partial`. The judge finds the field in the fixture's mutated paths, its declared message
  and the clause's own tests, never in the `expect` fragment, which an author can cut short. A field
  named only inside an interpolated or free message, such as `underlying`, rests on the fixture
  declaring the message in full.
- `holds_when` states the gate of the clause cited. A rule that calls `produced_or_seeded` needs it.
  Such an entry is still `covered`, and `rmf conformance report` counts it separately as
  `conditional`.
- Unresolved sentences are computed, never stored, because a stored list drifts: a sentence of a
  `partial` entry with no strong item. `rmf conformance report` lists them and totals tier 1's as
  `tier1_debt`.
- Work item status gains `closed-partial`: built, the remaining entries honestly `partial`, none of
  those tier 1. An item with a tier 1 `partial` entry stays open. `closed` means every entry covered.
  FW-REQ-004 no longer refuses a `covered` entry on an open item, since such an item now holds both;
  it refuses an open item whose entries are all covered.
- FW-REQ-002 at p13 lets a non-tier-1 obligation freeze at `partial` with evidence; a tier 1 entry
  needs `covered` or an approved deferral. FW-REQ-002 itself stays for p13.
- A marked sentence that is a permission or an open list of examples can never fail, so it is not
  proof debt, and an agent cannot rule it out. `ruling_sought: [{sentence, reason, approved_by?}]`
  names it, whole, by the same check as evidence. Without `approved_by: user` the entry stays
  `partial`, its work item cannot close, and the sentence leaves `unresolved` for
  `summary.awaiting_ruling`, outside `tier1_debt`. With it, `covered` needs no item on that
  sentence, and FW-REQ-003 refuses an entry with every marked sentence ruled out as `covered`
  (this text first called such an entry `not-a-requirement`; the 2026-11-08 freeze note below
  supersedes that: it stays `partial` and passes FW-REQ-002). Never for a duty that is merely
  hard to test.
- AODM-009 split the deciding official, subject and recipients out of AODM-001, which had reached 34
  evidence items against the fan-out cap of 25 once each clause was cited alone.

## The tier 1 freeze, decided with the user 2026-11-08

The register outside tier 1 became advisory (the scope cut of the same day), so the freeze no
longer asks every obligation to be triaged. This supersedes the FW-REQ-002 readings of
2026-10-31 and 2026-11-02 above at every tier: a tier 1 partial with a strong item now passes
where `covered` or an approved deferral was required, open work items no longer block at any
tier, and outside tier 1 nothing blocks.

- FW-REQ-002 (AC-43, phase p13) errs on a live tier 1 entry still `candidate`, and on a tier 1
  `partial` none of whose evidence items judges strong (`evidence.judge`). A tier 1 partial
  passes with one strong item and a reason naming what is unheld; the unheld sentences stay
  `tier1_debt` in `rmf conformance report`, and their work items stay open as the backlog.
- Debt is counted per sentence, so a single-sentence tier 1 partial whose one sentence a strong
  item holds adds nothing to `tier1_debt`, though its reason names duty still unheld. The report
  counts such entries apart: `summary.tier1_partial_entries` (every tier 1 partial) and
  `summary.tier1_partial_by_reason` (those whose remainder lives only in `reason`).
- A tier 1 `partial` whose every marked sentence the user ruled out (`ruling_sought` with
  `approved_by: user`) passes FW-REQ-002 with no strong item: it has nothing left to prove, the
  reading FW-REQ-003 gives it when it refuses such an entry as `covered`. It stays `partial`
  rather than `not-a-requirement`: the ruling says the sentence needs no evidence, not that it
  is extraction noise, and a re-mark would move noise shares the user approved records for.
  This status is the lead's default (central fix C1), pending the user's confirmation; it
  supersedes the 2026-11-02 reading above.
- Open work items no longer block the freeze, at any tier.
- A `candidate` outside tier 1 warns, one finding per document with its count; `should` and
  `table` kinds are no longer told apart from obligations there.
- `rules.blocks_freeze` is the one reading: FW-REQ-002 and `summary.freeze` of the report
  (`tier_1`, `tier_1_partial_without_strong`, `advisory_elsewhere`) both call it.
- The rule is registered at p13, which stays open and is built ahead of p12
  (`profiles.AHEAD`): `rmf validate --profile p13` runs it, and it joins `release` and `fork`
  only once `.phases/p13.closed` exists, so the gate stays honest about what is enforced today.
- The frozen reference list and the warning for a reference imported after the freeze, recorded
  at p10, are still to be built at p13.
- The judge reads repo-scope rules (FW-*) too: a rule item may cite one whose negative fixture is
  a framework overlay under `tests/fixtures/framework_neg/`, whose `expect.yaml` declares its
  `messages`, which `test_framework_negative` proves the rule emits. The claim and `expect` checks
  are those of run rules; an overlay has no mutations, so its claim comes from the clause alone.
  A repo-scope rule's source includes the functions it calls in other `rmf_tool` modules, since
  most are one call into the module holding their clauses. FW-ID-* join the generic rules that
  are denied as evidence: a unique, well-formed ID holds for any content.

- The user's decision of 2026-11-09 on the tier 1 leftovers (docs/audits/2026-11-08-tier1-leftovers.md)
  lets two groups pass the freeze as named tier 1 debt through a reviewed field,
  `freeze_debt: {group, unheld}`, set by `rmf conformance mark --freeze-debt`. Group B is a duty
  held only by a presence-only item on a required field; group C is a duty no run record can fail
  yet, whose candidates become `partial` on their prose or citation item with the missing record
  named. `rules.blocks_freeze` passes a tier 1 partial carrying it with no strong item; a
  candidate still blocks. FW-REQ-004 checks its shape: only on a tier 1 `partial`, bound to the
  work item that keeps the debt on the backlog (the C records are WI-790 to WI-79x, left open),
  and group B with an item the judge holds at the presence cap (an optional parent, a pin or a bare rule item does not count). `summary.freeze`
  counts `freeze_debt_B` and `freeze_debt_C`, which `rmf conformance report` prints; no separate file reports them. A C partial
  on prose counts as retired, so the per-document retired shares move; a document passing 25% is
  shown to the user before any retirements record is written.
