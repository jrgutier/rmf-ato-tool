# EFRAS data flow diagram

Drawn by the agent from `product/data-flows.md#top` (ASM-008). Fictional. Arrows show the
direction data moves.

```text
 user browser --DF-1 readiness views, queries, exports--> CMP-EDGE --> CMP-WEB / CMP-API
 CMP-IDB    --DF-2 authentication assertions-----------> CMP-API
 CMP-EMIS   --DF-3 maintenance actions + maintainer PII--> CMP-INGEST --> CMP-OBJ (landing)
 CMP-SUPPLY --DF-4 supply status-----------------------> CMP-INGEST
 CMP-INGEST --DF-5 validated records (incl. PII)-------> CMP-DB
 CMP-DB    <--DF-6 features and forecasts-------------> CMP-FORECAST
 CMP-API    --DF-7 report exports--> CMP-REPORT --> CMP-OBJ (report cache, exports)
 CMP-DB     --DF-8 training extract (pseudonymized)--> CMP-OBJ --> CMP-SANDBOX
 all        --DF-9 audit records--> CMP-LOGS --> CMP-ECSSP (external)
 CMP-SWF    --DF-10 signed images, templates-------> CMP-K8S
```

Shows: data types, data direction, external flows (DF-1 to DF-4, DF-9, DF-10), data stores.
