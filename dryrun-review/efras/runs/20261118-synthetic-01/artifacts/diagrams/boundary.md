# EFRAS authorization boundary diagram

Drawn by the agent from the product's component and boundary tables (ASM-008); the ISSE accepted
diagrams drawn from those tables (INT-025.A4). Fictional.

```text
 NIPRNet users                                   Separately authorized (outside)
      |                                          +--------------------------------+
      v                                          | CMP-IDB  identity broker       |
 +-----------+                                   | CMP-EMIS maintenance info sys  |
 | CMP-ECAP  | (outside, DoD access point)       | CMP-SUPPLY supply status svc   |
 +-----------+                                   | CMP-SWF  software factory      |
      | 443                                      | CMP-ECSSP CSSP                 |
======|==== EFRAS AUTHORIZATION BOUNDARY: program-owned production cloud account ====
||    v                                                                           ||
||  [edge subnet]  CMP-EDGE load balancer + WAF                                   ||
||    | 443                                                                       ||
||  [application subnet]  CMP-K8S worker nodes running                            ||
||      CMP-WEB  CMP-API  CMP-INGEST  CMP-FORECAST  CMP-REPORT                    ||
||    |                                     (isolated) CMP-SANDBOX notebooks       ||
||  [data subnet]  CMP-DB (data store)  CMP-OBJ (data store)  CMP-KMS             ||
||  CMP-LOGS log pipeline ---------------------------------------> to CMP-ECSSP   ||
====================================================================================
   Underneath, outside: CMP-CSP Example GovCloud IL4 region (data centers, physical
   protection, hypervisor, managed-service internals; inherited).
   Pre-production account: separate environment, synthetic data, not in this boundary.
```

Shows: components, internal boundaries (subnet tiers), third-party services, physical
protections (inherited from CMP-CSP), isolated components (CMP-SANDBOX).
