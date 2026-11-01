# Document downloads, 2026-10-31

Written at p9. 22 reference documents are pending (13 tier 1, 9 tier 2). A person downloads the PDFs into
`references/_inbox/`. A maintainer agent does everything else.

**Titles are confirmed; links are not.** On 2026-11-01 a maintainer read all 22 documents and matched each to
its ID. Eight titles in the tables below are the p9 brief's wording and differ from the document;
`references/index.yaml` holds each document's own title and revision. No link has been probed. The files were
saved through a browser extension, so their download records hold no file URL (the CNSS files name only
`https://www.cnss.gov/`), and a file name that matches a link proves nothing about the URL. A link can be wrong
or gone; if one fails, use the site's landing page and find the document there. For the four CNSS PDFs, a local
log (`.omc/logs/cnss-verified.txt`, not committed) records a re-fetch over verified TLS on 2026-10-31 and a
SHA-256 for each file, and each imported file's SHA-256 equals the logged value. The log records no comparison
with the browser copies.

## What the human does

Do this while you are at the machine. Browsers block repeat downloads (L-0015), so you may be asked to allow
automatic downloads for a site, or have to download one file per fresh tab.

1. Open each link in the lists below, in a real browser, tier 1 first.
2. Save the PDF into the `references/_inbox/` folder of this repository. Keep the file name the browser gives it.
   Do not rename anything; the maintainer works out which document each file is by reading it.
3. If a page shows a certificate warning, a login or an error page, stop on that document. Do not click through a
   certificate warning.
4. Tell the maintainer when you are done, and which documents you could not get or got stuck on.

That is all. You do not run commands or edit files.

## Downloads

Tier 1 blocks the freeze. Tier 2 does not.

### esd.whs.mil

| Tier | ID | Title (unconfirmed) | Link (unconfirmed) |
|---|---|---|---|
| 1 | DODI5000.83 | Technology and Program Protection to Maintain Technological Advantage | no direct link; find it on <https://www.esd.whs.mil/DD/DoD-Issuances/DoDI/> |
| 1 | DODI8500.01 | Cybersecurity | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/850001_2014.pdf> |
| 1 | DODI8530.01 | Cybersecurity Activities Support to DoD Information Network Operations | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/853001p.pdf> |
| 1 | DODI8531.01 | DoD Vulnerability Management | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/853101p.pdf> |
| 2 | DODD8140.01 | Cyberspace Workforce Management | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodd/814001p.pdf> |
| 2 | DODI5000.74 | Defense Acquisition of Services | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500074p.pdf> |
| 2 | DODI5000.75 | Business Systems Requirements and Acquisition | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500075p.PDF> |
| 2 | DODI5000.81 | Urgent Capability Acquisition | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500081p.PDF> |
| 2 | DODI5000.82 | Requirements for the Acquisition of Digital Capabilities | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500082p.pdf> |
| 2 | DODI5400.11 | DoD Privacy and Civil Liberties Programs | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/540011p.pdf> |
| 2 | DODI5400.16 | DoD Privacy Impact Assessment (PIA) Guidance | no direct link; find it on <https://www.esd.whs.mil/DD/DoD-Issuances/DoDI/> |
| 2 | DOWI8430.01 | DoW Instruction 8430.01 (title recorded at import) | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/843001p.PDF> |
| 2 | DTM-24-001 | Directive-type Memorandum 24-001 (title recorded at import) | <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dtm/DTM-24-001.PDF> |

### dodcio.defense.gov and media.defense.gov

| Tier | ID | Title (unconfirmed) | Link (unconfirmed) |
|---|---|---|---|
| 1 | DODCIO-CATO-EVAL | cATO Evaluation Criteria | <https://dodcio.defense.gov/Portals/0/Documents/Library/cATO-EvaluationCriteria.pdf> |
| 1 | DODCIO-CATO-IG | DoD Continuous Authorization to Operate (cATO) Implementation Guide | <https://dodcio.defense.gov/Portals/0/Documents/Library/DoDCIO-ContinuousAuthorizationImplementationGuide.pdf> |
| 1 | DODCIO-CSRMC | DoD Cybersecurity Risk Management Construct (CSRMC) | <https://media.defense.gov/2025/Sep/24/2003808112/-1/-1/1/DOD-CIO-CYBER-SECURITY-RISK-MANAGEMENT-CONSTRUCT.PDF> |
| 1 | DODCIO-CSRMC-TENETS | DoD Cybersecurity Risk Management Construct (CSRMC): Strategic Tenets | <https://media.defense.gov/2025/Sep/24/2003808111/-1/-1/1/DOD-CIO-CYBER-SECURITY-RISK-MANAGEMENT-CONSTRUCT-STRATEGIC-TENETS.PDF> |
| 1 | DODCIO-RECIPROCITY | DoD Cybersecurity Reciprocity Playbook | <https://dodcio.defense.gov/Portals/0/Documents/Library/(U)%202024-01-02%20DoD%20Cybersecurity%20Reciprocity%20Playbook.pdf> |

### cnss.gov

The site uses a DoD PKI certificate that browsers may not trust (L-0003, L-0016); in L-0015 the whole site
failed in a real browser. Try the browser first. If the browser shows a certificate error, do not click through
it and do not try to work around it. Tell the maintainer, who tries `curl --cacert` with DISA's DoD PKI
bundle and a cookie jar, the path that worked in L-0016 (full verification, scoped to the fetch). The
`openDoc.cfm` links only work inside a session started from the listing page, and some CNSS documents may need a
PKI login. Direct links to these four are not known; open the listing page and find the document.

| Tier | ID | Title (unconfirmed) | Link (unconfirmed) |
|---|---|---|---|
| 1 | CNSSI1254 | Risk Management Framework Documentation, Data Element Standards, and Reciprocity Process for National Security Systems | no direct link; find it on <https://www.cnss.gov/CNSS/issuances/Instructions.cfm> |
| 1 | CNSSI4009 | Committee on National Security Systems (CNSS) Glossary | no direct link; find it on <https://www.cnss.gov/CNSS/issuances/Instructions.cfm> |
| 1 | CNSSP12 | National Information Assurance Policy for Space Systems Used to Support National Security Missions | no direct link; find it on <https://www.cnss.gov/CNSS/issuances/Policies.cfm> |
| 1 | CNSSP22 | Cybersecurity Risk Management Policy | no direct link; find it on <https://www.cnss.gov/CNSS/issuances/Policies.cfm> |

## If a document cannot be obtained

Tell the maintainer which one and what you saw. A tier 2 document just stays unassessed; nothing else changes.
A tier 1 document goes to the degraded-reference policy (`playbooks/_ops/fetch-blocked-refs.md`, "If a required
document cannot be obtained"). Only the user may approve that, and AC-1 is then reported not met.

## Maintainer: import steps

The maintainer runs these after the human reports, in this order, one document at a time. The PDF is untrusted
data: the import checks `%PDF-` and `qpdf --check`, and the maintainer reads the document before recording
anything.

1. Identify the file in `references/_inbox/` by reading it, and match it to an ID above.
2. `uv run rmf refs import <ID> references/_inbox/<file>.pdf`. Add `--url <url>` only when that is the URL the file
   was actually downloaded from; it is stored without query or fragment. Leave it out for a file saved from a
   listing page or whose URL is not known.
3. Run `uv run rmf refs extract --id <ID>`. Extraction needs the AGPL extractor, so bootstrap with `EXTRACT=1`
   (`make bootstrap EXTRACT=1`) first.
4. Edit `references/index.yaml` for the entry: set `revision` to the edition, date and change number the document
   shows (a month and year or ISO date; REF-007), and add `revision_stamp {page, anchor}` pointing at that
   passage, checked with `uv run rmf refs show <ID> --page N --anchor A`. If no passage can show the date, declare
   `revision_source: {reason: ...}` and say where the date comes from in `revision_note`.
5. Replace the `title` with the document's own title. Every pending entry's title came from the p9 brief and was
   not read from a document, so this applies to all 22, not only DOWI8430.01 and DTM-24-001.
6. Set `required: true` on the entry and add its ID to `src/rmf_tool/refs/required.py`, plus the required-set
   tests (`tests/unit/test_refs_required.py`). Do this in the same commit that imports the document.
7. Update the PDF counts in `README.md` (DOC-002) and the `du -sh` sizes it states.
8. `uv run rmf refs sync`, then `uv run rmf refs verify`, `uv run rmf validate`, `uv run rmf ci --profile p9`.

Cite a document only after its import commit: a pending reference fails FW-CITE-002 and a `required: false` PDF
fails FW-CITE-003. The two CSRMC PDFs come from `media.defense.gov` (ADR-0006).

## Import note, 2026-11-01

All 22 documents are imported. The checks prove each text is the extraction of the pinned PDF, not that it reads
correctly, so triage reads these against the PDF.

Findings I-1 to I-4 in [2026-11-01-import-findings.md](2026-11-01-import-findings.md) and work items WI-50 to WI-53
track the first four below.

- **CNSSP12, OCR text layer.** All 15 pages are scans with an Acrobat OCR text layer, and the errors reach the
  register: `C SSP 12` for the running head, `ational` for National, `l.` and `(l)` for item labels 1. `rmf refs
  extract --ocr` does not help; it acts only on pages with no text. In scratch, `ocrmypdf --force-ocr` fixed those
  errors but added others (`Jmproving`, `Ata`, `Reference 0`), and its text comes from a new PDF, not the pinned one.
- **DODCIO-CSRMC, scrambled extraction.** The page is a graphic, and the extractor's table finder read it as one
  table of fragments. Its scope has `tables: false`, so those fragments are neither entries nor rejections. One
  entry and 23 rejections remain, in scrambled reading order. Read the five phases and the tenet band from the PDF.
- **DODCIO-CSRMC-TENETS, rejected tenets.** Nine of the ten tenets are rejected as `no-marker`, because each heading
  joins its sentence (`Automation Automate to enhance...`). Only the continuous monitoring tenet entered; the other
  nine are promoted with the heading in the statement.
- **Figures with no extracted text.** On these in-scope pages the figure is an image, so only its caption is in
  the text: DODI5000.74 pp. 5, 12; DODI5000.75 p. 6; DODI5000.81 pp. 4, 9, 10; DODI5000.82 p. 5; DODI5000.83 p. 20;
  DODI8500.01 pp. 27, 37; DODI8530.01 pp. 34, 35; DODI8531.01 p. 14; DODCIO-CATO-IG pp. 7, 12, 17, 18;
  DODCIO-CATO-EVAL pp. 5, 6, 7.
- **Glossary duty sentences.** Five glossaries are two-column, and their extraction runs each term's label into the
  neighbouring definition, so those pages are excluded. Their seven duty sentences are promoted one at a time with
  `rmf conformance promote --sentence`: DODI5000.74 p. 27 (2), DODI5000.75 pp. 37 and 38 (3), DODI5000.82 p. 29,
  DOWI8430.01 p. 34.
- **DODCIO-RECIPROCITY p. 12.** A blank line in the extraction splits item 4.2.j, so REQ-DODCIO-RECIPROCITY-0065
  stops at `systems’` and its last word is promoted alone as REQ-DODCIO-RECIPROCITY-0163. Triage marks 0163
  not-applicable with the reason `last word of REQ-0065; read together`, and assesses 0065.
