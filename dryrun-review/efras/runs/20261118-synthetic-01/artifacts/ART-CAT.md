---
artifact_id: ART-CAT
run_id: 20261118-synthetic-01
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-067.A1, INT-067.A2, INT-067.A3, INT-068.A1, INT-068.A2, INT-068.A3, INT-068.A4, INT-069.A2, INT-061.A1, INT-061.A2, INT-061.A3, INT-061.A4, INT-062.A1, INT-062.A2, INT-063.A1, INT-063.A2, INT-063.A3, INT-064.A1, INT-064.A2, INT-064.A3, INT-064.A4, INT-065.A1, INT-065.A2, INT-065.A3, INT-066.A1, INT-051.A1, ART-INFOTYPES, ART-ORG-CONTEXT, ART-SD, ART-RA, ART-BIA, ART-REQ]
---
# Security categorization

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

## Impact per information type

Each information owner confirmed the values of their own types [[INT-061.A1]]
[[INT-062.A1]] [[INT-063.A1]]. The data steward owns INF-01, INF-03 and INF-04, the supply status
data owner owns INF-02, and the program owns INF-05 and INF-06. No owner adjusted a value at C-2.
The adjustments shown were made by the owners at P-12 and were confirmed here [[ART-INFOTYPES]].

| Type | C | I | A | Basis |
|---|---|---|---|---|
| INF-01 Maintenance and readiness data | moderate (from low) | moderate (from low) | low | aggregated readiness trends; tampering hides degraded readiness; EMIS is the fallback [[INT-061.A1]] |
| INF-02 Supply status | low | moderate (from low) | low | limited harm if disclosed; wrong status misorders parts [[INT-062.A1]] |
| INF-03 Maintainer PII | moderate | moderate | low (from moderate) | phishing and identity misuse for 30,000 people; EFRAS holds a copy, not the authoritative record [[INT-061.A2]] |
| INF-04 Forecasts and reports | moderate (from low) | moderate (from low) | low | same trends as their source data; tampered forecasts mislead orders [[INT-061.A3]] |
| INF-05 Audit records | moderate | moderate | low | names and DoD ID numbers; accountability; ECSSP holds a copy [[INT-063.A1]] |
| INF-06 System security information | moderate (from low, held at the user information level) | moderate | low | keys and policy protect the user information; restorable from the pipeline [[INT-063.A2]] |

INF-02 is CUI with low confidentiality for the type. The DoDI 8500.01 floor for CUI applies to
the system's confidentiality, which is held at moderate [[INT-062.A1]]. No type is classified.
No type is missing. PII is in INF-03 and INF-05 only [[INT-061.A4]] [[INT-062.A2]].

## System categorization

The system categorization in the facts block is the high-water mark of the table, objective by
objective [[INT-065.A2]]:

- confidentiality takes the moderate of INF-01, INF-03 to INF-06;
- integrity takes the moderate of every type;
- availability is low for every type once the owner of INF-03 adjusted its provisional moderate
  to low.

The categorization follows CNSSI 1253 because DoDI 8510.01 directs CNSSI 1253 for DoD systems
[[ART-ORG-CONTEXT]]. That is not because the system is a National Security System: the CIO
determined at P-16 that it is not one [[INT-051.A1]]. The product profile proposed both this
trigraph and `nss: true`. The trigraph is confirmed by the owners' values, but the NSS proposal
is not adopted, and the PM withdrew it [[INT-063.A3]]. Two earlier records still say otherwise:
the P-4 answer INT-010.A1 and the `nss: true` flags on ra.yaml connections. They belong to P-4
and P-14 and are left for those tasks to correct. The categorization does not depend on them
[[INT-051.A1]].

The levels were reviewed against the organization, the environment, the mission, the use, data
sharing and the national interest. Aggregation, PII and time criticality were also weighed, as
SP 800-60 and FIPS 199 direct [[INT-065.A2]]. None raises an objective above the mark, so there
is no adjustment. This agrees with the system risk assessment, whose highest risk is moderate
[[ART-RA]], and with the BIA: no process's disruption impact exceeds the availability impact
[[INT-066.A1]] [[ART-BIA]]. The categorization is documented against the capability needs
statement P-15 read [[ART-REQ]]. It is revisited at any significant or situational change, and
at least every three years [[INT-065.A3]].

## Overlays

| Overlay | Applies | Why |
|---|---|---|
| Privacy Overlays, Moderate set (CNSSI 1253F Attachment 6) | yes | Question 1 is yes: INF-03 is PII beyond logs and account records. The privacy risk analysis below gives moderate [[INT-064.A1]] [[INT-064.A4]] |
| Privacy Overlays, Accountability (ACCT) set | yes | Question 2 is yes: the INF-05 audit records hold users' names and DoD ID numbers [[INT-064.A1]] |
| Classified System Overlay | no | no classified information is stored, processed or sent [[INT-065.A1]] |
| Space Platform Overlay | no | not a space system [[INT-065.A1]] |
| Cross domain, Intelligence or special access overlays (not held in the library) | no | no classified, SCI or SAP information and no connection across security domains [[INT-065.A1]] |
| Component-mandated overlays | none beyond the Privacy Overlays for PII systems | [[ART-ORG-CONTEXT]] [[INT-065.A1]] |

**Privacy risk analysis.** The senior official for privacy assessed each of the seven Appendix
factors individually and dropped none [[INT-064.A2]] [[INT-064.A3]] [[INT-064.A4]]:

| Factor | Level | Reason |
|---|---|---|
| 1 Data elements | moderate | name, DoD ID, rate or rank, qualifications and work center can harm in other contexts; no SSN, health or financial data |
| 2 Data quality | low | from the authoritative EMIS, validated nightly; no decision about the person rests on it |
| 3 Data use | low | qualification coverage and record joins; no personnel, benefit or disciplinary decision |
| 4 Data analytics | moderate | 30,000 people aggregated, fleet-wide queries, model training on re-identifiable pseudonyms until release 1.6 |
| 5 Data location and accessibility | moderate | IL4 cloud behind CAC multifactor sign-in, but about 3,000 users, downloadable exports and e-mailed reports |
| 6 Potential harm to the individual | moderate | targeted phishing and identity misuse; embarrassment over qualifications; no safety risk |
| 7 Potential harm to the agency | moderate | Privacy Act breach response and notification; loss of the fleet's trust |

No factor was added. The factors were weighted equally, not as a high-water mark. Five moderate
and two low give an overall privacy risk level of moderate. The re-identifiable exports are the
outlying risk; they are tracked as a known weakness and do not raise the level to high
[[INT-064.A4]] [[product/conops.md#limitations]]. As the overlay's section 4.2 directs, this risk
level is used in place of a PII confidentiality impact level (PCIL). CNSSI 1253 footnote 23
still names PII impact levels, but no PCIL is set and no objective is raised for PII
[[INT-064.A1]].

The senior official for privacy set the moderate level at C-2. The official's approval of the
overlays, the PII determination and the categorization is recorded at C-3 [[INT-064.A4]].

## Review and approval

**Privacy approval.** The senior official for privacy acted in person, not through a designee,
on 2026-11-18, before the AODR's review [[INT-067.A1]] [[INT-067.A2]] [[INT-067.A3]]. The
official approved:

- the determination that the system processes PII (INF-03 and INF-05);
- the confirmation that the logs include PII, which brings in the Accountability set;
- the Moderate and Accountability Privacy Overlay sets;
- the categorization.

That approval does not cover the PIA, which is still with the privacy office
[[INT-067.A3]].

**Review.** The AODR reviewed the categorization for the AO [[INT-068.A1]] [[INT-068.A2]]
[[INT-068.A3]]:

- *Owners.* Every type carries its owner's confirmed value.
- *Lowered values.* The one lowered value, INF-03 availability, rests on EMIS being the
  authoritative copy, not on cost.
- *CUI.* INF-02's low confidentiality for a CUI type is acceptable because the CUI floor holds
  at the system level.
- *High-water mark.* Each system value is the high-water mark, and no value was set above it.
- *Overlays.* Each overlay decision has a reason.
- *Fit.* The result fits the risk assessment.

The review found no defect, so no correction was made. One observation was recorded: the P-4
answer that the Component's systems are NSS should be corrected by its owner before control
selection relies on it [[INT-068.A3]].

**Approval.** The AODR approved the categorization in the facts block and its two Privacy
Overlay sets on the AO's behalf on 2026-11-18, without conditions. The AODR asked for a new
categorization at any significant change [[INT-068.A4]]. The ISSM entered the approved
categorization in the registration record the same day [[INT-069.A2]].
