# EFRAS privacy information {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real PIA, SORN or office is described.

## PII handled {#pii}

Maintainer name, DoD ID number, rate or rank, qualifications and work-center assignment, for
about 30,000 maintainers whose names appear on maintenance actions in EMIS. EFRAS collects
nothing directly from individuals; all PII arrives in the EMIS extract (DF-3). The PII is used
to show qualification coverage per work center and to join actions to people.

## Authority and notice {#authority}

- Authority: the component's maintenance-records authority (fictional citation in the draft
  PIA).
- System of records notice: an existing component SORN for aviation maintenance records
  (fictional) covers the records; the component privacy office confirmed coverage by e-mail on
  2026-08-19, pending the PIA.
- Privacy Act statement: not required, because EFRAS collects nothing from individuals.

## Privacy impact assessment {#pia}

The PIA is drafted (version 0.9, 2026-09-30) and with the component privacy office. Open item:
the office asked how the de-identified exports are protected (see
`conops.md#limitations` item 1).

## Minimization and retention {#minimization}

EFRAS keeps maintainer PII only as long as the linked maintenance action is within the 5-year
analysis window; older records are purged monthly by the ingest worker. Exports for analysts
and the training extract are meant to be de-identified; see the known limitation above.
