"""The merged framework model (plan Decision A2): one file per entity type under
``framework/``, tasks split per RMF step, loaded into one model with a global ID space.

Entities stay plain mappings (their shape is fixed by ``framework.schema.json``); the
model adds the per-kind ID index and where each entity was read from.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

FRAMEWORK_DIR = "framework"
SCHEMA_DIR = "framework/schema"
FRAMEWORK_SCHEMA = "framework/schema/framework.schema.json"
TASKS_DIR = "tasks"
BASELINES_DIR = "baselines"  # CNSSI 1253 control baselines (ADR-0002)

STEP_ORDER = ("P", "C", "S", "I", "A", "R", "M")


@dataclass(frozen=True)
class Collection:
    kind: str  # key in the merged document and in stats
    file: str  # path relative to the framework root
    pattern: re.Pattern[str]  # FW-ID-002


COLLECTIONS: tuple[Collection, ...] = (
    Collection("phases", "phases.yaml", re.compile(r"^PH-[A-Z]{2,6}$")),
    Collection("milestones", "milestones.yaml", re.compile(r"^MS-[A-Z0-9]{1,8}$")),
    Collection("reviews", "reviews.yaml", re.compile(r"^RV-[A-Z]{2,6}$")),
    Collection("decisions", "decisions.yaml", re.compile(r"^AD-[A-Z]{2,6}$")),
    Collection("steps", "rmf-steps.yaml", re.compile(r"^[PCSIARM]$")),
    Collection("personas", "personas.yaml", re.compile(r"^PER-[A-Z]{2,10}$")),
    Collection("artifacts", "artifacts.yaml", re.compile(r"^ART-[A-Z]+(?:-[A-Z]+)*$")),
    Collection("external_inputs", "external-inputs.yaml",
               re.compile(r"^EXT-[A-Z0-9]+(?:-[A-Z0-9]+)*$")),
    Collection("pathways", "pathways.yaml", re.compile(r"^PW-[A-Z]{2,6}$")),
    Collection("tasks", f"{TASKS_DIR}/<step>.yaml", re.compile(r"^[PCSIARM]-[1-9]\d?$")),
)
KINDS = tuple(c.kind for c in COLLECTIONS)
META_FILE = "meta.yaml"

# Entities that must cite at least one reference (FW-CITE-001, AC-8).
CITING_KINDS = ("tasks", "artifacts", "personas", "decisions")

# NIST SP 800-37r2 tasks (plan §6.2). FW-TASK-001 compares IDs and names exactly
# (dash variants normalized), so renaming a task is a deliberate change here.
TASKS_80037: dict[str, str] = {
    "P-1": "Risk Management Roles",
    "P-2": "Risk Management Strategy",
    "P-3": "Risk Assessment—Organization",
    "P-4": "Organizationally-Tailored Control Baselines and CSF Profiles",
    "P-5": "Common Control Identification",
    "P-6": "Impact-Level Prioritization",
    "P-7": "Continuous Monitoring Strategy—Organization",
    "P-8": "Mission or Business Focus",
    "P-9": "System Stakeholders",
    "P-10": "Asset Identification",
    "P-11": "Authorization Boundary",
    "P-12": "Information Types",
    "P-13": "Information Life Cycle",
    "P-14": "Risk Assessment—System",
    "P-15": "Requirements Definition",
    "P-16": "Enterprise Architecture",
    "P-17": "Requirements Allocation",
    "P-18": "System Registration",
    "C-1": "System Description",
    "C-2": "Security Categorization",
    "C-3": "Security Categorization Review and Approval",
    "S-1": "Control Selection",
    "S-2": "Control Tailoring",
    "S-3": "Control Allocation",
    "S-4": "Documentation of Planned Control Implementations",
    "S-5": "Continuous Monitoring Strategy—System",
    "S-6": "Plan Review and Approval",
    "I-1": "Control Implementation",
    "I-2": "Update Control Implementation Information",
    "A-1": "Assessor Selection",
    "A-2": "Assessment Plan",
    "A-3": "Control Assessments",
    "A-4": "Assessment Reports",
    "A-5": "Remediation Actions",
    "A-6": "Plan of Action and Milestones",
    "R-1": "Authorization Package",
    "R-2": "Risk Analysis and Determination",
    "R-3": "Risk Response",
    "R-4": "Authorization Decision",
    "R-5": "Authorization Reporting",
    "M-1": "System and Environment Changes",
    "M-2": "Ongoing Assessments",
    "M-3": "Ongoing Risk Response",
    "M-4": "Authorization Package Updates",
    "M-5": "Security and Privacy Reporting",
    "M-6": "Ongoing Authorization",
    "M-7": "System Disposal",
}
OPTIONAL_TASKS = frozenset({"P-4", "P-6"})
TASK_CITATION_REF = "SP800-37R2"


def task_sort_key(task_id: str) -> tuple[int, int]:
    """RMF step order, then task number (P-2 before P-10)."""
    step, _, num = task_id.partition("-")
    rank = STEP_ORDER.index(step) if step in STEP_ORDER else len(STEP_ORDER)
    return rank, int(num) if num.isdigit() else 0


@dataclass(frozen=True)
class Location:
    file: str  # repo-relative where possible
    line: int | None = None  # 1-based


@dataclass
class Entity:
    kind: str
    data: Any  # the mapping read from YAML
    location: Location

    @property
    def id(self) -> str:
        value = self.data.get("id") if hasattr(self.data, "get") else None
        return value if isinstance(value, str) else ""


@dataclass
class Framework:
    meta: Any
    meta_location: Location
    entities: list[Entity] = field(default_factory=list)

    def of(self, kind: str) -> list[Entity]:
        return [e for e in self.entities if e.kind == kind]

    def index(self, kind: str) -> dict[str, Entity]:
        """ID -> entity; the last one wins for duplicates (FW-ID-001 reports them)."""
        return {e.id: e for e in self.of(kind)}

    def ids(self, *kinds: str) -> set[str]:
        return {e.id for e in self.entities if e.kind in kinds}

    def counts(self) -> dict[str, int]:
        return {kind: len(self.of(kind)) for kind in KINDS}
