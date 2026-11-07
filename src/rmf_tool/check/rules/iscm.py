"""ISCM rules: what the system continuous monitoring strategy (S-5) states
beyond a frequency per family (CONMON-001). They hold from framework_version 0.2.0 (``since``),
so a run on an older contract validates its conmon.yaml against the same schema and is not held
to them. Each is quiet until ART-CONMON is produced or seeded."""

from __future__ import annotations

from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.catalog import family
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import scope

CONMON_FILE = "artifacts/data/conmon.yaml"
LEVERAGED_FILE = "artifacts/data/leveraged-authorizations.yaml"
STIG_FILE = "artifacts/data/stig-summary.yaml"
# What the strategy states under each key. An empty list is an answer (no tool is used, nothing
# is delegated); a missing key is not.
SECTIONS = {
    "frequency_criteria": "the criteria that set each monitoring frequency",
    "tools": "the automated tools and what each assesses, or an empty list",
    "architecture": "how monitoring data is collected, stored, analyzed, retrieved and "
                    "delivered, and where it is automated",
    "monitoring": "how compliance, effectiveness and change are monitored",
    "events": "the criteria and thresholds of event-driven assessments and authorizations",
    "boundary_review": "how often the authorization boundary is revisited",
    "threat_monitoring": "who watches the threat, from which sources and how often",
    "metrics": "the metrics monitoring reports and the tasks that use them",
    "delegations": "the operations and sustainment activities delegated to external "
                   "partners, or an empty list",
    "risk_assessment": "how the risk assessment is kept current and its results communicated",
}
WATCHES = ("threat-actors", "protective-techniques", "deployed-environment")
PERIODIC = ("continuous", "daily", "weekly", "monthly", "quarterly", "semi-annually",
            "annually")  # every frequency but event-driven
APPROVERS = ("PER-AO", "PER-AODR")
CRITERIA_OWNERS = ("PER-PM", "PER-CCP")  # system owner, common control provider
ORG_STRATEGY = "ART-ORG-CONTEXT"
CSSP = "PER-CSSP"


def _strategy(ctx: Context) -> dict[str, Any] | None:
    if not scope.produced_or_seeded(ctx.run, "ART-CONMON"):
        return None
    data = ctx.data(CONMON_FILE)
    return data if isinstance(data, dict) else None


def _records(conmon: dict[str, Any], key: str) -> list[dict[str, Any]]:
    return [r for r in conmon.get(key) or () if isinstance(r, dict)]


def _section(conmon: dict[str, Any], key: str) -> dict[str, Any]:
    value = conmon.get(key)
    return value if isinstance(value, dict) else {}


def _minimums(conmon: dict[str, Any], controls: list[str]) -> dict[str, str]:
    """Each baseline control's minimum monitoring frequency: its family's, or an override."""
    by_family = {r.get("family"): r for r in _records(conmon, "frequencies")}
    out = {}
    for cid in controls:
        record = by_family.get(family(cid))
        if record is None:
            continue
        out[cid] = record.get("frequency")
        for override in record.get("overrides") or ():
            if isinstance(override, dict) and override.get("control") == cid:
                out[cid] = override.get("frequency")
    return out


def sections(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None:
        return []
    out = [make("ISCM-001", f"conmon.yaml has no {key}: the strategy states {what}", CONMON_FILE)
           for key, what in SECTIONS.items() if key not in conmon]
    watches = _section(conmon, "threat_monitoring").get("watches") or ()
    if "threat_monitoring" in conmon:
        for kind in WATCHES:
            if kind not in watches:
                out.append(make("ISCM-001", f"threat monitoring does not watch {kind}: the "
                                "strategy watches threat actor activity, new protective "
                                "techniques and the deployed threat environment", CONMON_FILE))
    return out


def tools(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None or baseline_mod.load(ctx.run) is None:
        return []
    controls = baseline_mod.control_ids(ctx.run)
    baseline = set(controls)
    minimum = _minimums(conmon, controls)
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("ISCM-002", message, CONMON_FILE))

    automated: set[str] = set()
    stig = ctx.data(STIG_FILE)
    benchmarks = {b.get("id") for b in (stig.get("benchmarks") or ()) if isinstance(b, dict)} \
        if isinstance(stig, dict) else set()
    for tool in _records(conmon, "tools"):
        tid, freq = tool.get("id"), tool.get("frequency")
        if tool.get("method") != "test":
            err(f"{tid} is an automated tool, so it assesses by the test method, not "
                f"{tool.get('method')}")
        for cid in tool.get("assesses") or ():
            if cid not in baseline:
                err(f"{tid} assesses {cid}, which is not in the baseline: the strategy documents "
                    "the controls each automated tool assesses")
                continue
            automated.add(cid)
            if minimum.get(cid) == "continuous" and freq != "continuous":
                err(f"{tid} collects {cid} {freq}, but the strategy monitors it continuously: "
                    "a tool behind a continuous frequency collects at that frequency")
        spec = tool.get("desired_state")
        strategy = tool.get("strategy")
        if strategy == "desired-state" and not isinstance(spec, dict):
            err(f"{tid} follows the desired state strategy but defines no actual state, desired "
                "state or defect method")
        if strategy != "desired-state" and isinstance(spec, dict):
            err(f"{tid} defines a desired state block but its strategy is {strategy}, not "
                "desired-state")
        if strategy == "desired-state" and isinstance(spec, dict):
            actual = spec.get("actual_state") or {}
            desired = spec.get("desired_state") or {}
            if actual.get("collection") != "automated":
                err(f"{tid} collects its actual state manually: the desired state strategy "
                    "needs an automated actual state specification")
            for ref in desired.get("data") or ():
                if ref not in benchmarks and not (str(ref).startswith("product/")
                                                  and ctx.run.resolve(str(ref)).is_file()):
                    err(f"{tid} rests its desired state on {ref}, which is neither a benchmark "
                        "in stig-summary.yaml nor a product file: the desired state is "
                        "data-based")
            if set(desired.get("controls") or ()) != set(actual.get("controls") or ()):
                err(f"{tid}: the desired state does not cover the controls of the actual state, "
                    "so the two are not comparable")
    for cid in controls:
        if minimum.get(cid) == "continuous" and cid not in automated:
            err(f"no automated tool assesses {cid}, so it needs a manual assessment "
                "frequency, not continuous")
    return out


def frequency_basis(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None or baseline_mod.load(ctx.run) is None:
        return []
    baseline = set(baseline_mod.control_ids(ctx.run))
    criteria = {c.get("id"): c for c in _records(conmon, "frequency_criteria")}
    organizational = set(_section(conmon, "organizational_frequencies").get("families") or ())
    out: list[RunFinding] = []

    def err(message: str) -> None:
        out.append(make("ISCM-003", message, CONMON_FILE))

    for record in _records(conmon, "frequencies"):
        fam = record.get("family")
        refs = record.get("criteria") or ()
        if not refs:
            err(f"the {fam} frequency names no criteria: the system strategy identifies the "
                "criteria for each frequency the organizational strategy does not set")
        for ref in refs:
            if ref == ORG_STRATEGY and fam not in organizational:
                err(f"the {fam} frequency cites ART-ORG-CONTEXT, but organizational_frequencies "
                    "does not list the family as one the organizational strategy sets")
            if ref != ORG_STRATEGY and ref not in criteria:
                err(f"the {fam} frequency rests on {ref}, which frequency_criteria does not "
                    "define")
        for override in record.get("overrides") or ():
            cid = override.get("control") if isinstance(override, dict) else None
            if cid not in baseline or family(str(cid)) != fam:
                err(f"override {cid} under {fam} is no baseline control of that family")
    for ident, criterion in criteria.items():
        owner = criterion.get("established_by")
        if owner not in CRITERIA_OWNERS:
            err(f"{ident} is established by {owner}: frequency criteria are established by "
                "PER-PM, the system owner, or PER-CCP")
        others = set(criterion.get("consulted") or ()) - {owner}
        if not others:
            err(f"{ident} names no other official it was established with: the criteria are "
                "established in collaboration with other organizational officials")
    return out


def approval(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None:
        return []
    record = conmon.get("approval")
    if not isinstance(record, dict):
        return [make("ISCM-004", "conmon.yaml records no approval: the authorizing official "
                     "approves the strategy", CONMON_FILE, None, {"S-6"})]
    approver = record.get("approved_by")
    if approver not in APPROVERS:
        return [make("ISCM-004", f"the strategy is approved by {approver}: the authorizing "
                     "official or designated representative approves the continuous "
                     "monitoring strategy and the minimum frequency of each control",
                     CONMON_FILE, None, {"S-6"})]
    return []


def reporting(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None:
        return []
    out = []
    recipients = set(_section(conmon, "reporting").get("recipients") or ())
    if not recipients & set(APPROVERS):
        out.append(make("ISCM-005", "monitoring results do not reach the authorizing official: "
                        "reports, manual results included, go to the AO or designated "
                        "representative", CONMON_FILE))
    review = _section(conmon, "boundary_review")
    freq = review.get("frequency")
    if "boundary_review" in conmon and freq not in PERIODIC:
        out.append(make("ISCM-005", f"the authorization boundary is revisited {freq}, not "
                        "periodically: its scope is revisited on a schedule", CONMON_FILE))
    return out


def delegations(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None or "delegations" not in conmon:
        return []
    partners = {d.get("partner") for d in _records(conmon, "delegations")}
    data = ctx.data(LEVERAGED_FILE)
    leveraged = {la.get("id") for la in (data or {}).get("leveraged_authorizations") or ()
                 if isinstance(la, dict)} if isinstance(data, dict) else set()
    roles = {r.get("responsible") for key in ("frequencies", "tools")
             for r in _records(conmon, key)}
    roles |= {v.get("responsible") for v in _section(conmon, "monitoring").values()
              if isinstance(v, dict)}
    roles |= {_section(conmon, k).get("responsible") for k in ("threat_monitoring",
                                                               "boundary_review")}
    out = []
    if CSSP in roles and CSSP not in partners:
        out.append(make("ISCM-006", "the CSSP performs monitoring for the system, but no "
                        "activity delegated to it is documented", CONMON_FILE))
    for partner in sorted(p for p in partners if str(p).startswith("LA-")):
        if partner not in leveraged:
            out.append(make("ISCM-006", f"a delegation names {partner}, which "
                            "leveraged-authorizations.yaml does not hold", CONMON_FILE))
    return out


# --- METR: the metrics the strategy reports ---------------------------------------------
def metrics(ctx: Context) -> list[RunFinding]:
    conmon = _strategy(ctx)
    if conmon is None or "metrics" not in conmon:
        return []
    found = _records(conmon, "metrics")
    if not found:
        return [make("METR-001", "conmon.yaml lists no metrics: the ISCM program has a set of "
                     "metrics and corresponding review procedures", CONMON_FILE)]
    out = []
    for metric in found:
        mid = metric.get("id")
        missing = []
        if not metric.get("objective"):
            missing.append("states no objective: each metric states the specific objective it "
                           "is derived from")
        if not metric.get("controls"):
            missing.append("states no controls: each metric states the controls it is "
                           "calculated from")
        if not metric.get("baseline"):
            missing.append("states no baseline: each metric states the baseline its values are "
                           "evaluated against")
        if not metric.get("threshold"):
            missing.append("states no threshold: each metric states the threshold that shows "
                           "nonconformance")
        if not metric.get("review"):
            missing.append("states no review: each metric states its review procedure")
        out.extend(make("METR-001", f"metric {mid} {what}", CONMON_FILE) for what in missing)
        review = metric.get("review") if isinstance(metric.get("review"), dict) else {}
        recipients = set(_strs(metric.get("reported_to")))
        for official in _strs(review.get("by")):
            if official not in recipients:
                out.append(make("METR-001", f"metric {mid} is reviewed by {official}, who is not "
                                "among the officials it is reported to: metrics are reported to "
                                "the designated officials who review them", CONMON_FILE))
    return out


def _strs(value: Any) -> list[str]:
    """The strings a list field holds; a malformed field is RUN-FM-001's to report."""
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _rank(frequency: Any) -> int | None:
    return PERIODIC.index(frequency) if frequency in PERIODIC else None


def metric_timing(ctx: Context) -> list[RunFinding]:
    """Each control a metric reads is monitored at least as often as the metric is refreshed:
    at its minimum frequency, or by a tool that assesses it more often."""
    conmon = _strategy(ctx)
    if conmon is None or baseline_mod.load(ctx.run) is None:
        return []
    controls = baseline_mod.control_ids(ctx.run)
    baseline = set(controls)
    best = {cid: _rank(freq) for cid, freq in _minimums(conmon, controls).items()}
    for tool in _records(conmon, "tools"):
        rank = _rank(tool.get("frequency"))
        for cid in _strs(tool.get("assesses")):
            if rank is not None and (best.get(cid) is None or rank < best[cid]):
                best[cid] = rank
    out = []
    for metric in _records(conmon, "metrics"):
        mid, freq = metric.get("id"), metric.get("frequency")
        wanted = _rank(freq)
        for cid in _strs(metric.get("controls")):
            if cid not in baseline:
                out.append(make("METR-002", f"metric {mid} reads {cid}, which is not in the "
                                "baseline, so it is not calculated from the security "
                                "architecture's controls", CONMON_FILE))
                continue
            if cid not in best or wanted is None:
                continue
            have = best[cid]
            if have is None or have > wanted:
                seen = PERIODIC[have] if have is not None else "only on events"
                out.append(make("METR-002", f"metric {mid} is refreshed {freq} but {cid} is "
                                f"monitored {seen}: the controls a metric is calculated from are "
                                "monitored with frequencies consistent with its timing",
                                CONMON_FILE))
    return out
