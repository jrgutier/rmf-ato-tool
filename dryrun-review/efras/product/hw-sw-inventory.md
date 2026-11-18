# EFRAS hardware and software list {#top}

> **FICTIONAL — FOR DEMONSTRATION.** Providers, vendors and products are fictional.

Inventory IDs are the program's configuration-item numbers; keep them unchanged. EFRAS owns no
hardware: the provider's hardware is inherited (see `architecture.md#leveraged`). Quantities
are for the production environment.

## Items {#items}

| ID | Item | Kind | Component | Vendor | Product | Version | Quantity | Priority |
|---|---|---|---|---|---|---|---|---|
| INV-001 | Load balancer and web application firewall | service | CMP-EDGE | Example GovCloud (fictional) | managed application load balancer + WAF | provider-managed | 1 | high |
| INV-002 | Web front end container | software | CMP-WEB | Example Readiness Software Team (fictional) | efras-web | 1.5.0 | 3 replicas | moderate |
| INV-003 | Readiness API container | software | CMP-API | Example Readiness Software Team (fictional) | efras-api | 1.5.0 | 3 replicas | high |
| INV-004 | Ingest worker container | software | CMP-INGEST | Example Readiness Software Team (fictional) | efras-ingest | 1.5.0 | 1 (nightly) | high |
| INV-005 | Forecast job container | software | CMP-FORECAST | Example Readiness Software Team (fictional) | efras-forecast (model v3) | 1.5.0 | 1 (nightly) | moderate |
| INV-006 | Report rendering container | software | CMP-REPORT | Example Readiness Software Team (fictional) | efras-report | 1.5.0 | 2 replicas | low |
| INV-007 | Hardened container base image | operating-system | CMP-K8S | Example Software Factory (fictional) | sf-base-minimal | 2026.09 | all containers | high |
| INV-008 | Managed Kubernetes service | service | CMP-K8S | Example GovCloud (fictional) | managed Kubernetes | 1.33 | 1 cluster | high |
| INV-009 | Worker node image | virtual-machine | CMP-K8S | Example GovCloud (fictional) | hardened node image | 2026.10 | 6 nodes | high |
| INV-010 | Managed PostgreSQL database | database | CMP-DB | Example GovCloud (fictional) | managed PostgreSQL | 16.4 | 1 primary + 1 standby | high |
| INV-011 | Object storage buckets | service | CMP-OBJ | Example GovCloud (fictional) | object storage | provider-managed | 4 buckets | high |
| INV-012 | Key management and secrets store | service | CMP-KMS | Example GovCloud (fictional) | key service + secrets manager | provider-managed | 1 | high |
| INV-013 | Log pipeline and log store | service | CMP-LOGS | Example GovCloud (fictional) | log service | provider-managed | 1 | moderate |
| INV-014 | Analytics notebook environment | service | CMP-SANDBOX | Example GovCloud (fictional) | managed notebooks | provider-managed | 3 seats | low |
| INV-015 | Image-processing library (inside efras-report) | software | CMP-REPORT | open source | example-imagelib | 2.9.1 | 1 | low |
| INV-016 | Web framework runtime (inside efras-api) | software | CMP-API | open source | example web framework | 4.2 | 1 | high |

## Asset priority {#priority}

The data path is high: the API, ingest worker, database, object storage and keys
(INV-003, INV-004, INV-010..INV-012) hold or move the CUI and PII, and the edge (INV-001) is the
only way in. The cluster platform (INV-007..INV-009) is high because every service runs on it.
Forecasting and the web front end are moderate; reports, the sandbox and the image library are
low for mission but INV-015 carries the open vulnerabilities in `conops.md#limitations` item 2.

## Hostnames {#hostnames}

The service is published as `efras.example.mil` (fictional) behind the access point. Cluster
nodes have only private addresses; none is reachable from NIPRNet directly.
