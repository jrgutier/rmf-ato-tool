# Import findings, 2026-11-01

Findings from reading the 22 documents imported from the operator downloads
([2026-10-31-operator-imports.md](2026-10-31-operator-imports.md)) against what the extractor made of them, on top
of commit `838f3f6`. Findings keep their IDs here so work items can reference them. The coverage audit of
`e996ae6` is a dated record and is not changed; its findings are `N-*`, `D-*` and `C-*`, and these are `I-*`.

## How to read this

- The maintainer read rendered pages and extracted text side by side. An independent review re-checked the import.
- A finding records a difference between a document and its text in this repository. The reference checks pass on
  all of them: they prove a text is the extraction of the pinned PDF, not that it reads correctly.
- The figure list covers in-scope pages where an image takes at least 12% of the page and a figure caption is
  present. Other images were not read.

## Findings

| ID | Document | In the document | In the repository | Sev |
|---|---|---|---|---|
| I-1 | CNSSP12 | 15 scanned pages with an Acrobat OCR text layer | The errors reach the register: `C SSP 12`, `ational` for National, `l.` and `(l)` for labels 1. `ocrmypdf --force-ocr` in scratch fixed those and added others, and the repository's OCR path did worse | Med |
| I-2 | DODCIO-CSRMC | A one-page graphic of five phases and ten tenets | The extractor reads it as a table of fragments, so its scope has `tables: false`; one entry and 23 scrambled rejections remain, and the phases are not entries | Med |
| I-3 | DODCIO-CSRMC-TENETS | Ten tenets, each a heading and a sentence or two | The heading joins its sentence, so nine were rejected as `no-marker`; they are promoted by hand with the heading in the statement. REQ-DODCIO-CSRMC-TENETS-0003 reads `Training Enhancer ole-based training program` because of the PDF's own text layer, so evidence must quote it that way | Low |
| I-4 | 10 documents, 20 pages | Figures that are images | Only the caption is in the text: DODI5000.74 pp. 5, 12; DODI5000.75 p. 6; DODI5000.81 pp. 4, 9, 10; DODI5000.82 p. 5; DODI5000.83 p. 20; DODI8500.01 pp. 27, 37; DODI8530.01 pp. 34, 35; DODI8531.01 p. 14; DODCIO-CATO-IG pp. 7, 12, 17, 18; DODCIO-CATO-EVAL pp. 5, 6, 7 | Low |
| I-5 | DODCIO-RECIPROCITY, DODI5000.81 | Numbered section headings: `5. ROLE OF VARIOUS TYPES OF AOS`, and run-in `2.5. ...` | Read as a list item or as prose, so `locator` and `context` run on past the section: RECIPROCITY sections 5 to 10 carry `4.5.ii.*`, and 5000.81 sections 1.3, 1.4, 2.2, 2.3, 2.5, 2.6 and 2.7 carry the section before. `context` can name the wrong subject: an item under 2.5 reads as the DOT&E's. Citations are unaffected. Reading the `# N. CAPS` form as a heading was tried: it removes heading entries from CNSSI1253 and DODI8531.01 and rewrites 142 locators across five documents, so it is left for a change of its own | Low |
| I-6 | The register | A promoted entry whose passage moves, as when a footer leaves it | No tool can rebase it: REQ-DODCIO-RECIPROCITY-0169 needed a one-off edit of its statement and citation. `promote --replace`, or a re-resolve on page ±1 in `rmf conformance extract`, is the fix | Low |
| I-7 | DODCIO-RECIPROCITY | A sentence cut by a blank line inside one page | It stays cut: `blocks()` joins only across pages, and `)` alone counts as terminal, so REQ 0101, 0165 to 0170 and 0053 with 0054 are fragments. Triage reads them together; a fix must not join across a blank line in general | Low |
