"""DASH-001: the system-level dashboard of a cATO. "All security controls will need to be fed into
a system level dashboard view, providing a real time and robust mechanism for AOs to view the
environment" (DoD CIO cATO memo p. 1); "AO and designated cybersecurity personnel must have
real-time access to the results of testing, scanning, monitoring, and performance metrics"
(EVAL p. 11); the dashboards show findings, the plan of action, security posture and residual
risk (IG CM03, RM04), aggregating vulnerability analysis, compliance scans and control
effectiveness for the environment and the applications (IG p. 9), with automated alerts (IG
p. 8); the package demonstrates the dashboard in operation (EVAL p. 11)."""

from __future__ import annotations

from rmf_tool import baseline as baseline_mod
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding
from rmf_tool.check.rules.cato import _mapping, _record, _strs, lacks

FEEDS = ("testing", "scanning", "monitoring", "performance-metrics")
SHOWS = ("findings", "poam", "security-posture", "residual-risk", "vulnerability-analysis",
         "compliance-scans", "control-effectiveness")
SCOPE = ("environment", "applications")
REAL_TIME = ("real-time", "near-real-time")
AO = "PER-AO"


def dashboard(ctx: Context) -> list[RunFinding]:
    data, out, err = _record(ctx, "DASH-001")
    if data is None:
        return out
    if "dashboard" not in data:
        err("the cATO package demonstrates no system-level dashboard (cato.yaml dashboard)")
        return out
    dash = _mapping(data.get("dashboard"))
    fed = dash.get("controls_fed")
    if fed != "all":
        unfed = [c for c in baseline_mod.control_ids(ctx.run) if c not in _strs(fed)]
        if unfed:
            err(f"all security controls are fed into the system-level dashboard view, and "
                f"{', '.join(unfed)} is not")
    missing = lacks(dash.get("feeds"), FEEDS)
    if missing:
        err(f"the AO has no real-time access to the results of {', '.join(missing)} on the "
            "dashboard")
    if AO not in _strs(dash.get("access")):
        err("the AO and designated cybersecurity personnel have real-time access to the "
            f"dashboard, and its access names {', '.join(_strs(dash.get('access')))}")
    limit = _mapping(dash.get("feasibility_limit"))
    if dash.get("refresh") not in REAL_TIME and not str(limit.get("reason") or "").strip():
        err(f"the dashboard is {dash.get('refresh')}, not near real time, and records no "
            "feasibility_limit saying why a nearer view is not feasible")
    unshown = lacks(dash.get("shows"), SHOWS) + lacks(dash.get("scope"), SCOPE)
    if unshown:
        err(f"the dashboard does not visualize {', '.join(unshown)}")
    if dash.get("automated_alerts") is not True:
        err("the dashboard raises no automated alerts for managing the risk in production")
    return out
