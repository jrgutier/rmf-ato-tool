"""Phase-aware validation profiles (plan §5.0).

Closed phases are marker files ``.phases/<p>.closed``. ``--profile pX`` evaluates
``closed ∪ {pX}``; no profile evaluates ``closed``; ``release`` is every phase and
``fork`` is release without the example checks and AGENT-001.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PHASES = ("p1", "p2", "p2x", "p3a", "p35", "p3b", "p4", "p5", "p6", "p7", "p8", "p9",
          "p10")
PROFILES = (*PHASES, "release", "fork")
# A profile including the key phase may only run once the value phases are closed.
REQUIRES_CLOSED = {"p3b": frozenset({"p2x"})}
PHASES_DIR = ".phases"


class ProfileError(ValueError):
    """Unknown profile or marker, or an unmet phase prerequisite (exit code 2)."""


@dataclass(frozen=True)
class Profile:
    name: str
    phases: frozenset[str]
    examples: bool = True  # evaluate checks on examples/ (p7)
    agent_severity: str | None = "W"  # AGENT-001: "W", "E", or None (skipped)

    def includes(self, phase: str) -> bool:
        return phase in self.phases


def closed_phases(root: Path) -> frozenset[str]:
    """Phases with a ``.phases/<p>.closed`` marker; unknown marker names are an error."""
    directory = root / PHASES_DIR
    if not directory.is_dir():
        return frozenset()
    found = {p.stem for p in directory.glob("*.closed")}
    unknown = sorted(found - set(PHASES))
    if unknown:
        raise ProfileError(f"unknown phase marker(s) in {PHASES_DIR}/: {', '.join(unknown)}")
    return frozenset(found)


def resolve(root: Path, name: str | None) -> Profile:
    closed = closed_phases(root)
    if name is None:
        return Profile("closed", closed)
    if name == "release":
        return Profile(name, frozenset(PHASES), agent_severity="E")
    if name == "fork":
        return Profile(name, frozenset(PHASES), examples=False, agent_severity=None)
    if name not in PHASES:
        raise ProfileError(f"unknown profile {name!r}; expected one of {', '.join(PROFILES)}")
    profile = Profile(name, closed | {name})
    for phase in sorted(profile.phases):
        missing = REQUIRES_CLOSED.get(phase, frozenset()) - closed
        if missing:
            raise ProfileError(
                f"profile {name} includes {phase}, which requires closed phase(s) "
                f"{', '.join(sorted(missing))}"
            )
    return profile


def rule_active(rule_phase: str, profile: Profile) -> bool:
    """A rule is evaluated only when its enforcement phase is in the profile."""
    if rule_phase not in PHASES:
        raise ProfileError(f"unknown rule phase {rule_phase!r}")
    return profile.includes(rule_phase)
