"""Deterministic OSCAL UUIDs (plan §6.6):
``uuid5(NAMESPACE_RMF, f"{system_id}/{model}/{entity_id}")``.

Random UUIDs would change on every build and defeat GEN-STALE-001 (B4 rejected, Phase 2).
"""

from __future__ import annotations

import uuid

NAMESPACE_RMF = uuid.uuid5(uuid.NAMESPACE_URL, "urn:rmf-tool")


def uuid_for(system_id: str, model: str, entity_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE_RMF, f"{system_id}/{model}/{entity_id}"))
