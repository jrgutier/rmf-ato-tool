---
interview_id: INT-147
run_id: 20261118-synthetic-01
task: A-2
persona: PER-SCA
date: 2026-11-18
topics: [methods depth and coverage, reuse of developer and test results, external providers, schedule, rules of engagement, penetration test, assessor-owed items]
---
# INT-147 — A-2 — PER-SCA

### Q1 {#INT-147.Q1}
Asked of: PER-SCA · Task: A-2 · Control focus: all 50 baseline controls (methods, depth, coverage)
How will you assess the 50 controls: which methods and objects, at what depth and coverage, and how will you group the work?
**A1 {#INT-147.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[ART-RA]] [[ART-CAT]] [[INT-151.A1]]
> Every one of the 50 controls is in scope; nothing is excluded. Each control gets an examine of
> its specification (the SSP statement, the plan or procedure it names) and the records or
> configuration that show it working. Every control the program implements in code or
> configuration also gets a test; the policy and plan controls (ac-1, at-2, at-3, ca-2, ca-5,
> ca-7, cp-2, ir-8, pl-2, pm-5, ps-3, ra-3, ra-8, sa-9) get examine and interview, because there is
> no mechanism to test. One interview round per role covers many controls at once: the ISSM,
> the ISSO, the ISSE, the PM, the developer lead, the CSSP liaison and the privacy officer.
> Depth and coverage follow the AODR's assurance requirements: focused depth and coverage for
> everything, comprehensive for the controls behind the moderate risks in ART-RA (TE-01
> exfiltration through the API, TE-02 re-identification of exports) and for the open
> weaknesses the program disclosed, the controls the SSP records as partial: ac-3, ac-6, au-11,
> ca-3, cm-6, cp-2, cp-4, ia-2, ia-5, ir-4, pl-2, pt-3, ra-5, ra-8, sa-11, sc-7, si-2. The inherited pe-3 and mp-6 are examined at basic depth against the
> provider's authorization package. Order: kickoff and document examination first, interviews
> and scans in the first week, technical tests and the penetration test in the second, then the
> privacy tests and the out-brief.

### Q2 {#INT-147.Q2}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2, sa-11, ra-5, cm-6, ac-3 (reuse of developer and DT results)
Which developer, developmental test and earlier assessment results will you reuse, and which will you only examine?
**A2 {#INT-147.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]] [[product/test-results.md#stig-scan]] [[product/test-results.md#pentest]] [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#dt-2]] [[product/test-results.md#account-review]] [[INT-144.A3]]
> We reuse two results as assessment results. First, the STIG and SRG scan of 2026-10-22: our
> team witnessed it, it used the DoD SCAP content, and it ran on release 1.5.0 in pre-production,
> built from the same templates as production; we supplement it with our own scan of release
> 1.5.1 because the server header and the export scoping fix changed images since. Second, the
> component red team's penetration test of 2026-10-27 to 2026-10-31 with the PT-1 retest of
> 2026-11-10: the red team is independent of ARSPO, tested from NIPRNet through the access
> point, and its findings PT-1 to PT-3 are specific. We supplement it with the PT-3 retest and a
> further test with the CSSP watching. The release 1.5.0 pipeline gates, DT-2 and the ISSO's
> account review are the program's own tests, which we did not witness; under POL-02 we do not
> reuse them as results. We examine them as evidence for ac-2 (with the session timeout), ac-3,
> au-6, cp-9, sa-11, sr-3 and sr-11 and re-perform a sample: the squadron scoping
> tests through the API, the tampered EMIS extract, the inactive-account disable and the image
> signature check at admission. DoDI 8510.01 and DoDI 5000.87 want those results used, and this
> is how we use them without lowering the independence the AO required.

### Q3 {#INT-147.Q3}
Asked of: PER-SCA · Task: A-2 · Control focus: pe-3, mp-6, cp-9, si-2, sc-7, si-4, au-6, ir-4, ir-6, ra-5, sa-11, sr-3, sr-11, ca-3 (external providers)
How do you handle the external providers and connected systems, and have you reviewed their agreements and assessments?
**A3 {#INT-147.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ART-SVCA]] [[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]]
> I reviewed on 2026-11-18 the agreements and the assessment packages the PM obtained for the
> seven external parts. The four providers whose controls EFRAS inherits (the IL4 cloud region,
> the access point, the software factory and the CSSP) each hold an authorization by our AO, and
> their security plans and assessment reports were made available to the PM on 2026-05-01; their
> assessors were independent of the provider's operations, and I read their procedures. For
> those we do not re-test the provider's side: we examine the customer responsibility matrix or
> service agreement, confirm the inherited control is offered and in force, and test only the
> EFRAS side of each hybrid control. The cloud region is commercial; its assessment was by an
> accredited third-party assessment organization under the DoD provisional authorization. The
> identity broker, EMIS and the supply status service are DoD systems EFRAS connects to, not
> control providers; we examine the onboarding approval, the interim EMIS approval and the
> signed supply agreement under ca-3, and test the EFRAS end of each connection; for each of the
> three the PM obtained the system's authorization letter from its AO, and EFRAS relies on them
> only for what it verifies itself (signed extracts, federated CAC assertions, a read-only API).
> The software
> factory's assessment report has an open POA&M item (the delayed hardened base image); we
> take that into account for sr-3, sr-11 and sa-11.

### Q4 {#INT-147.Q4}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2, sa-11, sc-7 (schedule, rules of engagement, penetration test)
What is the schedule, what may your team do on which systems, and what penetration test do you plan?
**A4 {#INT-147.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pentest]] [[product/architecture.md#top]] [[INT-148.A1]]
> We start on 2026-11-19 and finish with the out-brief on 2026-12-11, so that the report reaches
> the AODR well before the decision needed for the 2027-02-01 MVCR deployment. Kickoff
> 2026-11-19; interviews from 2026-11-20; our authenticated vulnerability and STIG scan on
> 2026-11-23; the container checklist review on 2026-11-24; the penetration test from
> 2026-11-30 to 2026-12-04; the leaver-timing test on 2026-12-01; the DT-2 re-performance on
> 2026-12-02; the REQ-11 and REQ-12 verification on 2026-12-03; the privacy tests on
> 2026-12-07; the out-brief on 2026-12-11. Rules of engagement: all testing is in the
> pre-production account with synthetic data, built from the production templates; nothing
> runs against production, live data or the NIPRNet outside the access point path the program
> already uses. Scans are authenticated, with accounts the PM issues for the window. Before any
> test the ISSO and the CSSP are told the source addresses and times; the ISSM can stop a test
> at any time, and a critical finding is reported to the ISSM and the AODR within one working
> day. No denial-of-service testing, no social engineering, no data leaves the account. The
> penetration test follows NIST SP 800-115 and is run by the same component red team, with the
> CSSP monitoring and responding as it would in production: it retests PT-3 (the sandbox egress
> wildcard), re-checks PT-1, and tries the API, web, report and ingest paths from NIPRNet and as
> an insider officer, for five working days with two testers. ca-8 is not in the 50-control
> subset, so this test is the organization's addition.

### Q5 {#INT-147.Q5}
Asked of: PER-SCA · Task: A-2 · Control focus: cm-6, ps-4, ac-2, sa-11 (assessor-owed items)
Which items has the program left for you to verify?
**A5 {#INT-147.A5}** respondent: simulated · tag: SIMULATED · basis: [[ART-STIG]] [[ART-SSP]] [[product/test-results.md#account-review]] [[ART-REQ]]
> Four. First, the Application Security and Development STIG review of the five program-built
> containers (BM-04) has never been done; we do it under cm-6 with the developer present. Second,
> the account review of 2026-10-06 removed two leavers during the review, which can mean the
> out-processing notice did not disable them in time; under ps-4 and ac-2 we sample the
> squadron out-processing records against the identity broker's disable times. Third, sa-11
> says no test has verified REQ-11 (protocols from the DoD IT Standards Registry) and REQ-12
> (Section 508): we examine the interface specifications against the registry and run an
> accessibility test of the web interface with assistive technology. Fourth, the PT-3 retest,
> which is part of the penetration test.
