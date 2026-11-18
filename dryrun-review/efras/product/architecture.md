# EFRAS architecture {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system is described; providers and vendors are
> fictional.

## Components {#components}

Component IDs are the program's configuration-item numbers; keep them unchanged.

| ID | Component | Type | Inside the boundary | Notes |
|---|---|---|---|---|
| CMP-EDGE | Application load balancer and web application firewall | service | yes | managed provider service, program-configured; TLS termination, WAF rules |
| CMP-WEB | Web front end | software | yes | single-page application served from containers |
| CMP-API | Readiness API service | software | yes | REST API; role checks; business logic |
| CMP-INGEST | Nightly ingest worker | software | yes | pulls EMIS and supply extracts, validates, loads the database |
| CMP-FORECAST | Forecast batch job | software | yes | nightly part-failure model scoring |
| CMP-REPORT | Report rendering service | software | yes | renders PDF and slide exports; see `conops.md#limitations` item 2 |
| CMP-K8S | Managed Kubernetes cluster | virtual-machine | yes | provider-managed control plane; program-managed worker node groups |
| CMP-DB | Managed PostgreSQL database | database | yes | encrypted at rest with program keys; point-in-time recovery |
| CMP-OBJ | Object storage buckets | service | yes | landing zone for extracts, report cache, de-identified exports |
| CMP-KMS | Key management and secrets | service | yes | provider key service and secrets store, program-owned keys |
| CMP-LOGS | Log pipeline and log store | service | yes | cluster, application and cloud audit logs; forwards to ECSSP |
| CMP-SANDBOX | Analytics sandbox | service | yes | notebook environment for data scientists; reads the training extract only |
| CMP-CSP | Example GovCloud IL4 region | service | no | separately authorized cloud service offering |
| CMP-ECAP | Example Enterprise Cloud Access Point | service | no | DoD boundary protection between NIPRNet and the cloud |
| CMP-IDB | Enterprise identity broker | service | no | CAC authentication, SAML/OIDC federation |
| CMP-EMIS | Example Maintenance Information System | interconnection | no | source of maintenance data; separately authorized |
| CMP-SUPPLY | Example Supply Status Service | interconnection | no | source of supply status; separately authorized |
| CMP-SWF | Example Software Factory | service | no | DevSecOps platform and pipeline; separately authorized |
| CMP-ECSSP | Example Cybersecurity Service Provider | service | no | boundary monitoring and incident support |

## Authorization boundary {#boundary}

The EFRAS boundary is the program-owned production cloud account and everything the program
configures in it: the edge (CMP-EDGE), the four application services and the batch jobs
(CMP-WEB, CMP-API, CMP-INGEST, CMP-FORECAST, CMP-REPORT), the cluster worker nodes (CMP-K8S),
the database (CMP-DB), object storage (CMP-OBJ), keys and secrets (CMP-KMS), the log pipeline
(CMP-LOGS) and the analytics sandbox (CMP-SANDBOX). The cloud provider's infrastructure, the
access point, the identity broker, the software factory, ECSSP and the two source systems are
outside and separately authorized. The pre-production account is a separate environment with
synthetic data and is not part of this authorization.

## Network architecture {#network}

- **Virtual network:** one virtual private network with three subnet tiers: edge (load
  balancer only), application (cluster nodes) and data (database endpoint, private endpoints
  to object storage and key service). Security groups allow edge → application on 443,
  application → data on the database port and storage endpoints only.
- **Ingress:** only from the ECAP (NIPRNet) to the load balancer on 443, TLS 1.2 or 1.3 with
  DoD-approved cipher suites. No public IP addresses on any node.
- **Egress:** application tier egress through a managed NAT gateway to an allow-list: EMIS and
  supply extract endpoints, the identity broker, ECSSP log collector, and the software factory
  registry. Everything else is denied and logged.
- **Management:** the cluster API is private; engineers reach it through the provider's
  privileged access path from the ERST privileged access workstations after CAC sign-in.

## Interconnections {#interconnections}

| ID | System | Direction | Agreement | Authorization |
|---|---|---|---|---|
| IC-1 | Example Maintenance Information System (CMP-EMIS) | EMIS → EFRAS nightly extract (pull over mutual TLS) | MOA drafted, under legal review; interim e-mail approval (see `conops.md#limitations` item 3) | EMIS ATO 2025-04-22 (fictional), valid to 2028-04-22 |
| IC-2 | Example Supply Status Service (CMP-SUPPLY) | Supply → EFRAS nightly API pull | service-level agreement signed 2026-06-30 (fictional) | ATO 2024-11-05 (fictional) |
| IC-3 | Enterprise identity broker (CMP-IDB) | both | enterprise onboarding approval 2026-05-12 (fictional) | enterprise service ATO |

## Leveraged authorizations {#leveraged}

| Provider | Covers | Decision | Date authorized |
|---|---|---|---|
| Example GovCloud IL4 region (CMP-CSP) | physical and environmental protection, infrastructure and hypervisor, managed service internals (Kubernetes control plane, database engine patching, storage durability), media sanitization | DoD provisional authorization IL4 | 2024-09-18 (fictional) |
| Example Enterprise Cloud Access Point (CMP-ECAP) | boundary protection between NIPRNet and the cloud, traffic inspection | ATO | 2025-01-10 (fictional) |
| Example Software Factory (CMP-SWF) | pipeline integrity, static and dynamic code scanning, container image hardening and signing, developer access control, artifact repository | ATO | 2025-10-01 (fictional) |
| Example Cybersecurity Service Provider (CMP-ECSSP) | 24x7 security monitoring of forwarded logs, incident response support, vulnerability alerts | service agreement under the CSSP's ATO | 2026-04-01 (fictional) |

## Identity and access {#identity}

- Users authenticate with CAC at the identity broker, which passes a signed assertion with the
  user's DoD ID number, organization and group memberships. EFRAS maps groups to five
  application roles (`viewer`, `officer`, `analyst`, `app-admin`, `auditor`). Roles are
  requested in the component's access request system, approved by the user's supervisor and
  the information owner for `analyst`, and provisioned by the ISSO.
- Users see only their own squadron or air wing unless they hold `analyst`.
- Accounts unused for 35 days are disabled automatically; the ISSO reviews all role
  assignments quarterly (last review 2026-10-06, see `test-results.md#account-review`).
- Sessions time out after 15 minutes idle; the identity broker enforces CAC and lockout.
- Cloud operations engineers use named console roles federated through the identity broker
  with CAC; two sealed break-glass accounts use FIDO2 keys (see `conops.md#limitations`
  item 5). Service accounts use workload identity; no long-lived access keys.
- Data scientists access only the analytics sandbox, which reads the training extract.

## Logging {#logging}

- The load balancer and WAF, the application services (sign-in, role changes, data exports,
  admin actions, failed authorization), the cluster audit log, the database audit extension
  and the cloud account activity log all write to the log pipeline (CMP-LOGS).
- Logs are kept 90 days in the log store (see `conops.md#limitations` item 6) and forwarded in
  near real time to ECSSP, which keeps them one year and alerts on its use cases.
- The ISSO reviews a weekly report of privileged actions, exports and denied requests; alerts
  for break-glass use and export volume spikes page the on-call engineer.

## Configuration management {#configuration}

- Infrastructure is code: every cloud resource is defined in version-controlled templates and
  deployed only by the pipeline. Manual console changes are detected by a drift scan every
  hour and reported to the ISSO.
- Container images use the software factory's hardened base images; worker nodes use the
  provider's hardened node image and are checked against the Kubernetes STIG. The database is
  configured per the PostgreSQL STIG to the extent a managed service allows; inherited items
  are noted in the STIG summary.
- Every change goes through pull request review, the pipeline's security gates (static scan,
  dependency scan, image scan, dynamic scan, policy checks) and ISSO sign-off; major releases
  also go to the configuration control board.

## Software updates {#updates}

- Application updates ship as pipeline releases every three weeks; emergency patches can be
  deployed within 48 hours under the same gates.
- Worker node images roll monthly to the provider's latest hardened image. Managed service
  patching (database engine, control plane) is done by the provider in announced windows.
- Base image updates come from the software factory; release 1.5.2 waits on a base image fix
  (see `conops.md#limitations` item 2).

## Physical protection {#physical}

All hardware is in the cloud provider's data centers and inherited from its IL4 provisional
authorization. ERST privileged access workstations are government-furnished, kept in the
program's controlled office space.
