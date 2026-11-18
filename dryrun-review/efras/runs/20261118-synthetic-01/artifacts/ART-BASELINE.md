---
artifact_id: ART-BASELINE
run_id: 20261118-synthetic-01
produced_by_task: S-1
touched_by: [S-1, S-2, S-3]
sources: [INT-070.A1, INT-070.A2, INT-070.A3, INT-070.A4, INT-070.A5, INT-071.A1, INT-071.A2, INT-071.A3, INT-071.A4, INT-072.A1, INT-072.A2, INT-073.A1, INT-073.A2, INT-074.A1, INT-074.A2, INT-074.A3, INT-074.A4, INT-074.A5, INT-074.A6, INT-075.A1, INT-075.A2, INT-075.A3, INT-075.A4, INT-076.A1, INT-076.A2, INT-077.A1, INT-077.A2, INT-078.A1, INT-078.A2, INT-078.A3, INT-078.A4, INT-079.A1, INT-079.A2, INT-079.A3, INT-080.A1, INT-080.A2, INT-081.A1, INT-082.A1, INT-083.A1, INT-083.A2, INT-084.A1, INT-084.A2, INT-084.A4, INT-085.A1, ASM-017, ART-CAT, ART-ORG-CONTEXT, ART-REQ, ART-RA]
---
# Control baseline, tailoring and allocation

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
<!-- END rmf:facts -->

## Selection basis

The baseline in the facts block was resolved by `rmf baseline resolve` into `baseline.json` with
method `cnssi1253`: CNSSI 1253 per-objective selection for the approved categorization. It is the
union of the Appendix D controls the confidentiality, integrity and availability columns select at
the levels in the facts block, plus the NSS privacy control baseline. The two Privacy Overlay sets
the categorization lists are applied on top [[INT-070.A1]] [[ART-CAT]]. The SP 800-53B high-water
mark was not used: it is only the fallback while CNSSI 1253 is degraded [[INT-070.A1]].

For this dry run, `run.yaml` limits the selection to a fixed subset of 50 controls, and the
baseline ID carries that subset size. Of the 50 controls, 46 come from the Appendix D columns.
PT-2, PT-3 and RA-8 come from the Privacy Overlays. PM-5 comes from the NSS privacy control
baseline alone [[INT-073.A2]]. No enhancement is selected, so no enhancement stands without its
base control.

**NSS privacy control baseline.** EFRAS is not a National Security System [[ART-CAT]]. It is
categorized and its controls are selected under CNSSI 1253 because DoDI 8510.01 directs CNSSI 1253
for DoD systems, and CNSSI 1253's selection includes the NSS privacy control baseline as a default
[[INT-070.A2]]. The ISSM keeps that baseline, and the senior official for privacy agreed and asked
that her agreement be recorded as the basis [[INT-073.A1]]. The P-4 record that calls the
Component's systems NSS is wrong for EFRAS. Selection does not rest on that record, and correcting
it is left to its owner [[INT-070.A2]].

**Organizational additions.** The Component has no organizationally tailored baseline and no CSF
profile. Its risk board directs the Privacy Overlays for every system that processes PII, and they
are already on the categorization. No other overlay applies. DoD assignment values enter as
parameter values at tailoring and in the security plan, not as added controls [[INT-070.A3]]
[[ART-ORG-CONTEXT]]. The organization defined no security or privacy capabilities ahead of
selection, so there is no `capabilities.yaml` [[INT-070.A5]].

## Common controls available for inheritance

Four authorized providers offer controls in the selected set. Each holds a current authorization
[[ART-ORG-CONTEXT]]:

| Provider | Controls in the selected set | Full or partial | Authorization | Trace |
|---|---|---|---|---|
| Example GovCloud IL4 region | pe-3, mp-6 | full | DoD provisional authorization IL4, 2024-09-18, current | [[INT-071.A1]] |
| Example GovCloud IL4 region | si-2, cp-9 | partial: the program patches its images and containers and runs its own backups | as above | [[INT-071.A1]] |
| Example Enterprise Cloud Access Point | sc-7, si-4 | partial: the program owns its subnets, security groups, WAF rules and egress allow-list | ATO 2025-01-10, current | [[INT-071.A2]] |
| Example Software Factory | sa-11, sr-3, sr-11 | partial: the program owns its code, dependencies, tests and admission policy | ATO 2025-10-01, current, one open POA&M item (late hardened base image) | [[INT-071.A3]] |
| Example Cybersecurity Service Provider | si-4, au-6, ir-4, ir-6, ra-5 | partial: the program forwards logs, reviews its own, handles and reports incidents and scans inside the account | under the CSSP's own ATO; ARSPO service agreement 2026-04-01 | [[INT-072.A1]] |

Only PE-3 and MP-6 are offered whole. The access point and the factory warned against recording
any of their controls as fully inherited [[INT-071.A4]]. The CSSP keeps forwarded audit records
for one year for its own analysis. That copy is not the program's archive, so AU-11 stays with the
program [[INT-072.A2]]. The factory also offers SA-10, SA-15 and CM-14, which the dry-run subset
does not hold [[INT-071.A3]].

The Component privacy office provides program-level privacy controls (PM-18, PM-19, PM-26, PM-27,
and parts of PT-5 and AT-2) without a separate authorization package [[ART-ORG-CONTEXT]]. Of these,
only AT-2 is in the selected set. The system owner's and AO's determination for each provider is
S-3's to record [[INT-070.A1]].

**Determination (S-3).** On 2026-11-18 the PM and the AODR, acting for the AO, made the
determination for all five providers named in `allocation.yaml` `providers`. They read the
providers' plans, assessment reports and monthly status, and the privacy office's program review.
They examined the parameter values and found each provider's controls commensurate with EFRAS's
risk for what they cover [[INT-081.A1]] [[INT-082.A1]]. Only PE-3 and MP-6 are inherited whole.
Two caveats stay with the program: the software factory's open POA&M item on the base image, and
the CSSP's log copy, which is not the program's retention [[INT-081.A1]].

## Tailoring and allocation

### Tailoring (S-2)

The ISSM produced `artifacts/data/tailoring.yaml` with the senior official for privacy, the common
control provider and the PM [[INT-074.A1]] [[INT-075.A1]] [[INT-076.A2]] [[INT-077.A2]].

- **Overlays.** The Privacy Overlays' Moderate and Accountability sets are applied. They only
  select controls, so they do not conflict [[INT-074.A1]].
- **Actions.** There are 16 parameter actions and 1 specification action. There are no add,
  remove or compensating actions [[INT-074.A2]] [[INT-074.A4]].
  - The parameter values are the Privacy Overlay's values or stricter ones for AC-2, CM-2, CM-3,
    SC-8, SC-12 and SC-28, plus the Component's one-year retention for AU-11 [[INT-074.A3]].
  - The specification is an SI-12 addendum: maintainer PII is kept for the 5-year analysis
    window and purged monthly [[INT-075.A1]].
  - PE-3 and MP-6 carry the cloud provider's values [[INT-076.A1]].
- **Scoping and compensating.** No control is scoped out, and no compensating control is used.
  The FIDO2 break-glass accounts still meet IA-2 with multi-factor authentication. They are a
  deviation from the CAC policy for the AO to accept, not a compensating control. AU-11 (90-day
  store against one year), CP-4 (failover untested) and RA-8 (PIA not approved) stay in the
  baseline as gaps. S-4 records them as partial or planned, and they go to the POA&M
  [[INT-074.A2]].
- **Supplementation.** None. In a real selection the ISSM would add SI-10 (REQ-04), SI-19 (REQ-14)
  and MP-3 (REQ-09). The dry-run subset is fixed, so these stay recorded gaps
  [[INT-074.A4]] [[INT-075.A4]].
- **Assumptions.** All twelve assumptions were tested:
  - The five SP 800-53B baseline assumptions and the three CNSSI 1253 assumptions hold.
  - Of the additional situations, classified information and cross-domain connections do not
    apply. Information that needs protection under law and policy (Privacy Act PII and CUI) does
    apply. The Privacy Overlays address it, together with PT-2, PT-3, RA-8, SC-8 and SC-28.
  - The Privacy Overlay's workforce training assumption holds.

  [[INT-074.A5]] [[INT-075.A3]]
- **Assurance.** No additional assurance-related controls are needed. Moderate assurance comes
  from the factory's release evidence, SA-11 and the supply chain controls [[INT-074.A6]].
- **Trade-offs.** Three trade-offs were weighed [[INT-077.A1]]:
  - cost: a funded archive tier for AU-11 in release 1.6, instead of relying on the CSSP's copy;
  - complexity: IA-2 kept with sealed break-glass keys, instead of custom console federation;
  - supply chain: SA-11, SR-3 and SR-11 implemented through the software factory.
- **Law and policy.** No control is removed or compensated, so no law or policy test was needed.
  The PM accepted the tailoring and its cost [[INT-077.A2]].
- **C-SCRM decisions for S-4.** SR-3 and SR-11 are selected and kept, and they are implemented
  through the software factory with the program's own admission policy. Their cost is part of the
  factory tenancy. Not implementing them would leave the open-source supply chain risk (SC-04,
  VUL-02) unmanaged. No procurement adds new supply chain controls [[INT-077.A1]] [[ART-RA]].

### Allocation (S-3)

The ISSM designated each control. The ISSE placed the controls on components, and the senior
official for privacy designated the privacy controls. The result is in
`artifacts/data/allocation.yaml`, one record per control [[INT-078.A1]] [[INT-078.A2]]
[[INT-078.A3]] [[INT-079.A1]] [[INT-080.A1]]:

| Type | Count | Controls |
|---|---|---|
| common | 2 | pe-3, mp-6 (Example GovCloud IL4 region) |
| hybrid | 14 | si-2, cp-9 (cloud region); sc-7 (access point); sa-11, sr-3, sr-11 (software factory); au-6, ir-4, ir-6, ra-5, si-4 (CSSP); at-2, pt-2, pt-3 (Component privacy office) |
| program-management | 1 | pm-5, the Component's system inventory kept by the CIO's office |
| system-specific | 33 | the rest |

The PM-5 designation is the ISSM's [[INT-079.A2]]. SI-4 is shared by the CSSP and the access
point. The schema takes one provider per control, so the CSSP, which carries most of it, is
recorded, and the access point's inspection is described here [[INT-079.A1]]. The components
with the most controls are the cluster CMP-K8S (16), the API CMP-API and the edge CMP-EDGE (8
each) and the database CMP-DB (7). Nineteen procedural controls have no component home and are
allocated to `this-system` [[INT-078.A4]]. The ISSO confirmed that the allocation matches the
controls the ISSO operates: AC-2 on CMP-API, AU-6 on CMP-LOGS, and CM-3 and CM-6 on the cluster.
The ISSO cannot yet carry AU-11's one-year retention or show a CP-4 failover result
[[INT-083.A1]] [[INT-083.A2]].

**Requirements.** Each allocation lists the REQ-## it satisfies [[INT-079.A3]]. The cross-check
of ART-REQ's allocation against the controls on each element found these gaps
[[INT-079.A3]] [[ART-REQ]]:

- REQ-11 (standards registry) and REQ-12 (Section 508) are implemented by no control in the set,
  and REQ-12 has no control in the SP 800-53 catalog. Both are verified, not implemented: the
  developer checks interface conformance against the registry by analysis and tests the web
  pages for accessibility. `allocation.yaml` therefore traces both to sa-11 (developer testing
  and evaluation). That trace stands for "verified outside the control set through the
  developer's test and evaluation"; it does not claim that SA-11 satisfies either requirement.
  The product material holds no test result for either yet [[INT-084.A4]].
- The access point and the software factory are recorded in `leveraged-authorizations.yaml` as
  separately authorized organizational systems (LA-02, LA-03, each with a valid ATO, ends per
  ASM-017, the AO made aware through the AODR) and the CSSP as a service under agreement
  (LA-04). Each provides only part of its controls, so the allocations stay hybrid; only the
  cloud region supplies whole common controls [[INT-084.A1]] [[INT-084.A2]] [[INT-085.A1]].
- REQ-09 (CUI marking) is only partly carried, by SI-12 on CMP-INGEST and CMP-REPORT. Nothing on
  CMP-WEB marks pages.
- ART-REQ allocates part of REQ-01 to the identity broker as a common control provider. The
  broker is not on the Component's common control list, so IA-2 stays system-specific and relies
  on the broker as an external service.
- REQ-17 (C-SCRM terms), REQ-18 (cloud contract clauses) and REQ-19 (workforce qualification)
  are carried by SR-3, SA-9, and AT-3 with PS-3. ART-REQ lists them only as one row,
  "REQ-17 to REQ-19", so `allocation.yaml` does not name them.

Every requirement allocated to a provider maps to a hybrid control of that provider: REQ-05 to
AU-6 (CSSP), REQ-06 to CP-9 (cloud region), REQ-07 to SA-11, SR-3 and SR-11 (factory), REQ-10 to
SC-7 (access point), and REQ-14 and REQ-15 to PT-3 and PT-2 (privacy office) [[INT-079.A3]].

## Privacy tailoring

The system processes PII. The senior official for privacy took part in selection with the ISSM: she
confirmed the NSS privacy control baseline and named the privacy controls the overlays bring in
[[INT-073.A1]] [[INT-073.A2]]. At S-2 she agreed the privacy parameter values. Before
implementation she conferred on each of the ten selected controls with a Privacy Implementation
Considerations checkmark (AU-6, CM-6, IA-2, IA-5, PE-3, PS-3, PS-4, SC-7, SC-12, SI-4), as
recorded in `tailoring.yaml` `privacy_implementation`. The only additional step she required is
the sandbox egress fix [[INT-075.A1]] [[INT-075.A2]]. AC-2(8) is not selected [[INT-075.A4]].

The tailoring leaves no gap in compliance with privacy requirements and adds no privacy risk,
because it removes and substitutes nothing [[INT-075.A1]]. A separate privacy gap does exist, and
it comes from the dry-run subset, not from tailoring. The set holds no de-identification control,
and the exports are re-identifiable today. RA-8 and PT-3 keep it visible, and it goes to the POA&M
[[INT-075.A1]] [[product/conops.md#limitations]].

## Requirements to address in tailoring

The ISSM and the senior official for privacy named six requirements of ART-REQ that the selected
set does not obviously cover. S-2 is asked to weigh each one [[INT-070.A4]] [[INT-073.A2]]:

| Requirement | Why not obviously covered | Controls that cover part of it |
|---|---|---|
| REQ-04 ingest signature, checksum and schema checks | input validation (SI-10) is outside the subset | sc-8, sa-11 |
| REQ-09 CUI marking on pages and exports | marking controls (MP-3, AC-16) are outside the subset | none in the set |
| REQ-11 DoD IT Standards Registry | acquisition controls (SA-4) are outside the subset | none in the set |
| REQ-12 Section 508 accessibility | no SP 800-53 control; a design requirement verified by test | none |
| REQ-13 measurable, traced requirements | acquisition and engineering controls (SA-4, SA-8) are outside the subset | pl-2, sa-11 |
| REQ-14 de-identification | de-identification (SI-19) is outside the subset | pt-2, pt-3, si-12 for minimization and the purge |

The ISSM expects these to be noted rather than supplemented, because the dry-run subset is fixed
[[INT-070.A4]].
