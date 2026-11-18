---
artifact_id: ART-BND
run_id: 20261118-synthetic-01
produced_by_task: P-11
touched_by: [P-11, P-16, C-1]
sources: [INT-058.A6, INT-060.A1, INT-025.A1, INT-025.A2, INT-025.A3, INT-025.A4, INT-026.A1, INT-026.A2, INT-026.A3, INT-047.A1, INT-047.A2, INT-048.A1, INT-048.A2, INT-049.A1, INT-050.A1, INT-051.A1, product/architecture.md#boundary, product/architecture.md#network, product/data-flows.md#top, ASM-008, ART-INFOTYPES]
---
# Authorization boundary, network architecture and data flows

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
| National security system | no | C-1 |
| Missions and business functions | MSN-01 Naval aviation readiness: keeping aircraft mission-capable; MSN-02 Aircraft maintenance and readiness management; MSN-03 Daily readiness reporting for squadron, air wing and fleet (BP-01); MSN-04 Part failure forecasting for early part orders (BP-02); MSN-05 Fleet readiness analysis and de-identified data set export (BP-03) | P-8 |
<!-- END rmf:facts -->

## Authorization boundary

The boundary is the program-owned production cloud account and the twelve components the
program configures in it: CMP-EDGE, CMP-WEB, CMP-API, CMP-INGEST, CMP-FORECAST, CMP-REPORT,
CMP-K8S, CMP-DB, CMP-OBJ, CMP-KMS, CMP-LOGS and CMP-SANDBOX; every inventory item belongs to
one of them [[INT-025.A1]] [[ART-INV]]. The AO confirmed this is the set to be authorized
[[INT-026.A1]]. The edge is the account: traffic enters only through CMP-EDGE from the access
point and leaves only through the egress allow-list [[INT-025.A2]].

Outside the boundary, and why: the cloud provider's infrastructure, the access point, the
software factory and the CSSP are covered by their own authorizations or agreement, and EMIS,
the supply status service and the identity broker are separately authorized systems. The AO
takes the risk of the connections to them, not their internal risk [[INT-026.A2]]. The
pre-production account holds only synthetic data and is not part of this authorization; real
data there would return the boundary to the AO [[INT-026.A1]] [[product/architecture.md#boundary]].

Boundary condition: any new interconnection, or any component moved into or out of the
production account, is a boundary change the ISSM brings to the AODR before it is made
[[INT-026.A3]]. EFRAS is not a complex system; it has no subsystems with their own
categorization [[INT-025.A4]]. The diagram is `artifacts/diagrams/boundary.md`, drawn from the
product tables [[ASM-008]].

## Network architecture

One virtual private network with edge, application and data subnet tiers; security groups allow
only edge to application on 443 and application to data on the database port and storage
endpoints. Ingress comes only from the ECAP on 443 with TLS 1.2 or 1.3; no node has a public
address. Egress goes through a managed NAT gateway to an allow-list of five destinations, and
everything else is denied and logged. Administration uses the provider's privileged access path
from ERST privileged access workstations after CAC sign-in [[INT-025.A2]]
[[product/architecture.md#network]]. Diagram: `artifacts/diagrams/network.md` [[ASM-008]].

## Data flows

The flows DF-1 to DF-10 are the complete set [[INT-025.A3]] [[product/data-flows.md#top]].

| Crossing | Flows | Protection |
|---|---|---|
| inbound | DF-1 users, DF-2 identity assertions, DF-3 EMIS extract, DF-4 supply status, DF-10 signed images | TLS 1.2+ and CAC session; signed assertions; mutual TLS with signed, checksummed extract; API token from the secrets store; signature checked at admission |
| outbound | DF-9 audit records to ECSSP | TLS |
| inside | DF-5 to DF-8 | TLS, least-privilege database roles, signed short-lived links, read-only sandbox role |

Maintainer PII crosses the boundary in DF-3 and moves inside in DF-5 and DF-6; pseudonymized
records leave the database in DF-7 exports and the DF-8 training extract, which the product
discloses as re-identifiable until release 1.6 [[INT-025.A3]] [[product/conops.md#limitations]].
The PII belongs to information types INF-03 (maintainer records) and INF-05 (audit records)
[[ART-INFOTYPES]]. Diagram:
`artifacts/diagrams/data-flows.md` [[ASM-008]].

## External components

| Component | Provides | Authorization |
|---|---|---|
| CMP-CSP | infrastructure, physical protection, managed-service internals | DoD provisional authorization IL4 |
| CMP-ECAP | boundary protection between NIPRNet and the cloud | ATO |
| CMP-IDB | CAC authentication and federation (IC-3) | enterprise service ATO |
| CMP-EMIS | maintenance data and maintainer PII (IC-1) | ATO; agreement under legal review, interim e-mail approval |
| CMP-SUPPLY | supply status (IC-2) | ATO; service-level agreement signed |
| CMP-SWF | pipeline, scanning, image signing and deployment | ATO |
| CMP-ECSSP | monitoring, incident support, vulnerability alerts | service agreement under the CSSP's ATO |

[[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]] [[INT-026.A2]].
C-1 linked the four providers EFRAS inherits from to their leveraged authorizations in
`boundary.yaml`: CMP-CSP to LA-01, CMP-ECAP to LA-02, CMP-SWF to LA-03 and CMP-ECSSP to LA-04,
all inherited as common control providers. The identity broker and the two source systems are
interconnections, not leveraged authorizations; their agreements are ICX-01 to ICX-03 in
`system-description.yaml` [[INT-060.A1]] [[INT-058.A6]].

## Enterprise Architecture (P-16)

**Placement.** EFRAS is a business-support capability in the Component's aviation logistics and
readiness portfolio. It is a read-only consumer downstream of EMIS and the supply status service,
and it feeds readiness views to the fleet [[INT-049.A1]]. In the security architecture it is a
tenant of the Component's IL4 cloud, behind the enterprise access point and identity broker, and
monitored by the Component CSSP. It adds no enterprise service [[INT-049.A1]].

In the privacy architecture, EFRAS is a downstream holder of records under the Component's
aviation maintenance records SORN. EMIS stays the collecting system, and the privacy office's
program controls are common controls EFRAS relies on [[INT-050.A1]].

**National Security System.** EFRAS is not a National Security System. It holds no classified
information and performs no intelligence, cryptologic, command and control or weapons function.
As a logistics business application it falls under the statutory exclusion [[INT-051.A1]]. It
still uses the CNSSI 1253 baselines under DoD policy. No NSA assessment is owed, so
`nss-assessments.yaml` records `nss: false` [[INT-051.A1]].

**Hosting.** EFRAS is hosted in the IL4 cloud region, cloud first for a new start. It is not in a
DECC. It cannot be an application in an existing enclave, because no Component enclave offers
the managed platform at IL4. The cloud hosting assessment found it can be cloud-hosted without
compromising security or integrity. Five enterprise services are reused rather than built anew:
the cloud region, the access point, the identity broker, the software factory and the CSSP
[[INT-048.A1]] [[INT-048.A2]].

### Connections and approvals

EFRAS is on the DODIN; no waiver is needed [[INT-047.A1]]. Its one DISN attachment is CONN-01,
through the ECAP to NIPRNet. That connection goes through the DISA cloud connection process. The
production request was submitted on 2026-10-15 and is still requested, not approved
[[INT-047.A1]].

The other six connections are reached through the cloud and that attachment, over the egress
allow-list. They need no DISA approval of their own:

- CONN-02: cloud region, bidirectional.
- CONN-03: identity broker, bidirectional.
- CONN-04: EMIS, inbound. Interim e-mail approval; the agreement is under legal review.
- CONN-05: supply status service, inbound.
- CONN-06: software factory, inbound.
- CONN-07: CSSP, outbound.

Their ports, protocols and data are in `boundary.yaml`; the system-to-system agreements are with
the external components above [[INT-047.A2]]. No connection crosses a security domain, and there
is no mission partner interconnection [[INT-047.A1]].
