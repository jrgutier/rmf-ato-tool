# rmf-tool

A forkable GitHub template for the DoD Risk Management Framework (RMF, on NIST
SP 800-37r2), anchored to the DoD acquisition lifecycle. It provides:

- a local, pinned library of public reference documents (NIST, DoD, CNSS, DoD CIO),
  with deterministic text extractions;
- the RMF roadmap as validated YAML, rendered into a Markdown manual;
- agent-agnostic playbooks, persona cards and a deterministic `rmf` CLI, so an AI
  agent in a fork can interview simulated (or real) stakeholders and emit a
  consistent, OSCAL-validated **draft** ATO package.

Outputs are drafts for training and preparation. They do not replace a real
Security Control Assessor or Authorizing Official.

Agents: start with [AGENTS.md](AGENTS.md).

## Quick start

```sh
make bootstrap          # installs uv, jq, qpdf, git-lfs if missing; syncs the venv; runs rmf doctor
uv run rmf --help
uv run rmf ci           # fast lane + checks for every closed phase (.phases/*.closed)
```

Opt-in extras:

- `EXTRACT=1 make bootstrap` also installs the `[extract]` extra (PyMuPDF, AGPL; see NOTICE).
- `OCR=1 make bootstrap` also installs `ocrmypdf` and `tesseract`.

## Forking

1. Create your repository from this template, then clone it (see the LFS note below).
2. `make bootstrap`.
3. Follow the fork workflow in [AGENTS.md](AGENTS.md#fork-workflow).
4. Send lessons that touch upstream files (framework, playbooks, personas,
   templates, src) back upstream as a pull request.

## CUI warning

Never put Controlled Unclassified Information (CUI) or classified material into
a fork unless the repository host, every machine involved, **and the LLM
endpoint your agent uses** are authorized for it. The upstream template and its
example contain only public and fictional material.

## Clone size (Git LFS)

The 32 reference PDFs under `references/pdf/` are stored in Git LFS and committed:
about 34 MB for the 17 NIST documents (fetched automatically) and 17 MB for the 15 DoD and
CNSS documents (imported browser-assisted by the maintainer, per
`playbooks/_ops/fetch-blocked-refs.md`), 51 MB in all by `du -sh`. A new or changed DoD or
CNSS PDF is added the same way, by whoever updates `references/index.yaml`. Text
extractions and NIST OSCAL JSON (about 32 MB) are in plain git; `references/INDEX.md`
lists every document with its source URL and SHA-256. To clone without the PDFs:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone <your-fork-url>
git lfs pull --include "references/pdf/SP800-37R2.pdf"   # fetch individual PDFs later
```

## License

MIT (see [LICENSE](LICENSE)); the optional `[extract]` extra pulls an AGPL
dependency, and the reference documents are US Government public works
(see [NOTICE](NOTICE)).
