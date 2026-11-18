---
artifact_id: ART-BND
run_id: 20261118-synthetic-01
produced_by_task: P-11
touched_by: [P-11]
sources: [INT-025.A1, INT-025.A2, INT-025.A3, INT-025.A4, INT-026.A1, INT-026.A2, INT-026.A3, product/architecture.md#boundary, product/architecture.md#network, product/data-flows.md#top, ASM-008]
---
# Authorization boundary, network architecture and data flows

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| Authorization boundary | EFRAS-BND-1 | P-11 |
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
The information types of PII are named once P-12 identifies them. Diagram:
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
C-1 adds the leveraged authorizations.

<!-- P-16 appends "## Connections and approvals": each external connection of
     artifacts/data/boundary.yaml by CONN ID, the approvals it needs and their status, any
     cross-domain solution and mission partner terms, and whether the system is on the DODIN or
     outside it under a waiver; it adds P-16 to touched_by. -->
