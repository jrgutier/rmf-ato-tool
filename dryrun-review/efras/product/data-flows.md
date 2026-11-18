# EFRAS data flows {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system is described.

| ID | From | To | Path | Information | Protection |
|---|---|---|---|---|---|
| DF-1 | user browser (NIPRNet) | web front end and API (CMP-WEB, CMP-API) via ECAP and edge (CMP-EDGE) | NIPRNet, ECAP, load balancer | readiness views, queries, exports | TLS 1.2+ end to end; CAC-authenticated session |
| DF-2 | identity broker (CMP-IDB) | API (CMP-API) | egress allow-list | authentication assertions | signed SAML/OIDC assertions over TLS |
| DF-3 | EMIS (CMP-EMIS) | ingest worker (CMP-INGEST) to object storage (CMP-OBJ) | egress allow-list | maintenance actions, maintainer PII | mutual TLS; extract file signed by EMIS; checksum validated |
| DF-4 | supply service (CMP-SUPPLY) | ingest worker (CMP-INGEST) | egress allow-list | supply status | TLS with API token from secrets store |
| DF-5 | ingest worker (CMP-INGEST) | database (CMP-DB) | data subnet | validated records | TLS to the database; encrypted at rest with program keys |
| DF-6 | database (CMP-DB) | forecast job (CMP-FORECAST) and back | data subnet | features and forecasts | TLS; least-privilege database roles |
| DF-7 | API (CMP-API) | report service (CMP-REPORT) to object storage (CMP-OBJ) | application subnet | report exports | TLS; signed short-lived download links |
| DF-8 | database (CMP-DB) | analytics sandbox (CMP-SANDBOX) via object storage | private endpoint | training extract (pseudonymized, see `conops.md#limitations` item 1) | encrypted at rest; sandbox read-only role |
| DF-9 | all components | log pipeline (CMP-LOGS) to ECSSP (CMP-ECSSP) | egress allow-list | audit records | TLS |
| DF-10 | software factory (CMP-SWF) | cluster (CMP-K8S) | pipeline deploy role | signed container images, infrastructure templates | image signature verified at admission |

## Main flows {#main}

Every night the ingest worker pulls the EMIS and supply extracts (DF-3, DF-4), validates and
loads them (DF-5), and the forecast job scores parts (DF-6). During the day users view
dashboards and request exports (DF-1, DF-7). If EMIS is unreachable the nightly load is skipped
and dashboards show the previous day's data with a banner; nothing is lost because EMIS keeps
the source records.

## Management flow {#management}

Releases come only through the software factory (DF-10). Engineers administer the cluster and
database through the private management path described in `architecture.md#network`.

## Audit flow {#audit}

See `architecture.md#logging`; DF-9 runs continuously.
