# 2026-11 triage record

The register keeps `status`, `reason` and `work_item`. It does not keep why an entry was held or
what a gap was: those lived in `x_` notes, which never reach it. This folder keeps them.

| Path | What it is |
|---|---|
| `decisions/<JOB>.yaml` | One map per job, `{REQ-ID: fields}`. `x_existing`, `x_gap`, `x_note`, `x_home`, `x_new_work_item`, `x_defer` are here and nowhere else. Slugs are as proposed; the register holds final item IDs |
| `reports/<JOB>.md` | Each job's report: counts, misses, figures, cut pairs, conflicts |
| `reads/<JOB>.txt` | Page-by-page read log |
| `timing/<JOB>.txt` | UTC start and end |
| `slug-map.yaml` | Each slug to the item IDs its entries went to |
| `cross-references.yaml` | The 181 entries that named more than one gap: the item bound, and the others |
| `report-excerpts.md` | Conflicts and library gaps copied from the reports |
| `audit.md` | Repository against source, and library gaps, with finding IDs |
| `merges.md` | The merge lists the work items were built from |

Method: `BRIEF.md` is the rule set every job followed, `CLOSEOUT.md` and `closeout.txt` the last pass,
`slugs.txt` the proposed items as they stood mid-triage. Each job read its pages whole; Opus decided, Fable audited samples (638 decisions read, 1 wrong). The close-out then reversed
capacity calls, rescoped false exclusions, and built the work items.

To follow an entry: find it in `decisions/`, read its `x_` fields, then its `work_item` in the
register and `conformance/work-items.yaml`. A slug in `x_gap` that is not the entry's work item is in
`cross-references.yaml`.

## What was not done entry by entry

Section 6 of the Classified and Privacy overlays was decided as one row set: a generator wrote those
decisions (`x_new_work_item: overlay-control-specifications`), with noise exceptions and promoted
rows by hand, so they read alike by design. Rows with no marker stayed rejected only where they hold
a justification alone.

The first splits of WI-02, 04, 15, 18, 24, 30 and 31 used document and keyword selectors. A sampled
audit found about 80 misfiled, and every member of those items was then read and 102 entries moved,
so `slug-map.yaml` can show one slug in several items. Titles of items with no recorded holder were
written from the slug's description, with the `against` clause written by hand.

## Item size

25 entries is a guide, not a rule: `BRIEF.md` and the first merge state it as a cap, and the lead
struck that. Items split by sub-duty, and run to about 58 entries where a transcription or a cohesive
sub-duty warrants it. `FAN_OUT_CAP` enforces the real limit, on evidence; the overlay family items
will need a fan-out exception when evidence is built.

## Gaps in this record

| Job | Missing | Why |
|---|---|---|
| CNSSP22, DODI5000.81, DODI5400.16 | reads, reports | Pilot jobs, run before the brief asked for either |
| DODCIO-RECIPROCITY | report | Same pilot; it has reads and timing |
| DODI5400.16 | `timing/DODI5400.16.txt` | Pilot not timed; `timing/DODI5400.16-v2.txt` is its Opus second pass |
| SP800-34R1, SP800-53AR5 | no job of that name | `decisions/SP800-34R1.yaml` and `SP800-53AR5.yaml` hold the close-out's rescoped entries; the jobs are `.p1` and `.p2` |

DODI5000.81 and DODI5400.16 were decided by Sonnet in the pilot, then re-decided by Opus after it
wrongly retired three requirements.

Of the 12 rows promoted from the Section 6 rejections, 7 carry a lost Parameter Value (Privacy 0305 to 0311) and 5 are Justification and Guidance rows promoted as guidance (Privacy 0312 to 0315, Classified 0183).
