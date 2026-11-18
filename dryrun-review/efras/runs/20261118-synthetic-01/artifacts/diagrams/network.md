# EFRAS network architecture diagram

Drawn by the agent from `product/architecture.md#network` (ASM-008). Fictional.

```text
 NIPRNet --> CMP-ECAP --443 TLS1.2/1.3--> [edge subnet: CMP-EDGE]  (no public IPs)
                                               | SG: 443 only
                                               v
                                   [application subnet: CMP-K8S nodes]
                                     |  SG: DB port + storage endpoints only
                                     v
                     [data subnet: CMP-DB, CMP-OBJ endpoint, CMP-KMS endpoint]

 application subnet --> managed NAT gateway --> egress allow-list:
     CMP-EMIS extract endpoint (mTLS) | CMP-SUPPLY API | CMP-IDB | CMP-ECSSP collector
     | CMP-SWF registry ;  everything else denied and logged

 management: ERST privileged access workstations --CAC--> provider privileged
             access path --> private cluster API (CMP-K8S)
```

Shows: components, external connections, routing controls (security groups, NAT allow-list),
data stores (CMP-DB, CMP-OBJ).
