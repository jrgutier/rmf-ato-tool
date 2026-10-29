"""The required reference set (AC-1, plan §6.1). ``index.yaml`` must mark exactly these
entries ``required: true``; ``rmf refs verify --required`` checks that each is ``ok``."""

from __future__ import annotations

REQUIRED_IDS: tuple[str, ...] = (
    # NIST special publications
    "SP800-37R2", "SP800-53R5", "SP800-53AR5", "SP800-53B", "SP800-30R1", "SP800-39",
    "SP800-60V1R1", "SP800-60V2R1", "SP800-137", "SP800-18R1", "SP800-18R2", "SP800-34R1",
    "SP800-61R3", "SP800-128", "SP800-160V1R1",
    # FIPS
    "FIPS199", "FIPS200",
    # DoD and CNSS
    "DODI8510.01", "CNSSI1253", "DODI5000.02", "DODI5000.85", "DODI5000.87", "DODI5000.80",
    "DODI5000.88",
    # DoD CIO
    "DODCIO-CATO",
)
