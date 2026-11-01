.PHONY: bootstrap ci ci-release test render refs

# Idempotent toolchain setup. EXTRACT=1 adds the AGPL [extract] extra; OCR=1 adds OCR tools.
bootstrap:
	scripts/bootstrap.sh

# Fast lane plus the checks of every closed phase (.phases/*.closed).
ci:
	uv run rmf ci

# All profiles, slow tests, AGENT-001 as an error.
ci-release:
	uv run rmf ci --release

# In series on purpose, for readable order while debugging; rmf ci uses workers from 4 cores up.
test:
	uv run pytest -q

# Regenerate MANUAL.md and docs/manual/ from framework/.
render:
	uv run rmf render

# Fetch, verify, extract and index references.
refs:
	uv run rmf refs sync
