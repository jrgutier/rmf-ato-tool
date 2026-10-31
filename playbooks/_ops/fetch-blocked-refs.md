# Ops playbook: acquire blocked references (browser-assisted)

**Who runs this:** the user, operating Claude in Chrome (or a plain browser) on their own
machine. Agents never automate this step. It closes the Phase 2 exit gate (`p2x`) and
must happen before Phase 3b.

**Why it exists:**
- esd.whs.mil answers scripted clients with HTTP 403 (L-0002).
- dodcio.defense.gov did the same on 2026-10-29.
- cnss.gov serves an incomplete TLS certificate chain (L-0003).

The rules (INV-7) are to never spoof a User-Agent and never disable TLS verification. A
person therefore downloads these files in a real browser, and `rmf refs import` checks
and pins them.

## Rules

- Download only from the entry's `landing_url` (or a link on that page) on an allowed
  domain: `esd.whs.mil`, `cnss.gov`, `dodcio.defense.gov`, `public.cyber.mil`,
  `media.defense.gov` (the CSRMC PDFs only, ADR-0006), `nist.gov`.
- Never accept a non-PDF. An HTML error page, a login wall saved as `.pdf`, or a ZIP is
  rejected by the import (`%PDF-` magic + `qpdf --check`); do not try to work around that.
- One file per index entry. If a landing page offers several attachments that belong
  under one placeholder (for example `CNSSI1253F-OVERLAYS`), first add one index entry per
  public attachment (copy the placeholder entry and give it a new `CNSSI1253F-<NAME>` ID),
  then import each file under its own ID.
- Never edit `sha256`, `size_bytes`, `downloaded` or `status` in `references/index.yaml`
  by hand; the import writes them.

## Steps

1. List what is pending:

   ```sh
   uv run rmf refs verify --format json | jq -r '.findings[] | select(.rule=="REF-001") | .message'
   ```

   Each `pending-acquisition` entry's `landing_url` and candidate `urls` are in
   `references/index.yaml` and in `references/INDEX.md`.
2. In the browser, open the entry's `landing_url`, find the current issuance (note the
   change number or version date shown on the page), and download the PDF into
   `references/_inbox/` (gitignored). Keep the browser's file name.
3. Import and verify it:

   ```sh
   uv run rmf refs import <ID> references/_inbox/<file>.pdf --url <the PDF's URL>
   uv run rmf refs verify --id <ID>
   ```

   `--url` is optional but recommended; it is recorded as `resolved_url` and must be on an
   allowed domain. On `rejected: ... not a PDF` or `qpdf --check failed`, delete the file
   and download it again (often a login or error page was saved).
4. Read the revision from the document, not the listing. Set `revision` in
   `references/index.yaml` to the edition, date and change number the PDF shows (a month
   and year or ISO date; REF-007), and replace any placeholder `title` with the document's
   own. Run `uv run rmf refs extract --id <ID>` (needs `EXTRACT=1` bootstrap), then add a
   `revision_stamp {page, anchor}` to the passage that shows it (`rmf refs show <ID> --page N
   --anchor A`); its anchor must contain the revision's latest year. If no passage can show
   it, declare `revision_source: {reason: ...}` and say where the date comes from in
   `revision_note`.
5. Once the entry is obtained and cited-ready, set `required: true` on it and add its ID to
   `src/rmf_tool/refs/required.py` (and the required-set tests). Cite it only after that
   (FW-CITE-003). Update the README PDF counts (DOC-002).
6. After the last import, extract text, re-render the index and check the gate:

   ```sh
   uv run rmf refs sync
   uv run rmf refs verify --required
   uv run rmf ci --profile p2x
   ```

7. Commit the PDFs (Git LFS), `references/text/<ID>.md` + `.toc.yaml`,
   `references/index.yaml` and `references/INDEX.md` together.

## If a required document cannot be obtained

Follow the degraded-reference policy (plan §7.6): the entry becomes `status: degraded`
with `degraded: {approved_by: user, date, reason, fallback_refs: [...]}`, which only the
user may approve. REF-001 is then a warning, runs raise DEGRADED-001, and AC-1 is reported
as not met.

## Practical notes (L-0015)

- Do this while you are at the machine. Chromium browsers block every download after the first one from a site until you allow "automatic downloads" for it, and some downloads wait on a prompt.
- Agent-driven sessions: save one file per page load and confirm each lands in the browser's download folder before moving on.
- Don't route bytes from the page to a localhost receiver; Chrome's Local Network Access prompt blocks it.
- cnss.gov may be unreachable even in a real browser. Never click through a certificate warning. If CNSSI 1253 can't be obtained, use the degraded-reference policy below.
- **cnss.gov (L-0016):** the site uses a DoD PKI certificate. Download DISA's DoD PKI CA bundle (`https://dl.dod.cyber.mil/wp-content/uploads/pki-pke/zip/unclass-certificates_pkcs7_DoD.zip`) to a scratch folder, convert it with `openssl pkcs7 -print_certs`, and pass it as `curl --cacert` for these fetches only. Load `Instructions.cfm` with a cookie jar first; `openDoc.cfm` links only work within that session.
- **Agent-driven browser downloads (L-0016):** a fresh tab allows one download. Use one new tab per file (navigate → trigger download → close).
