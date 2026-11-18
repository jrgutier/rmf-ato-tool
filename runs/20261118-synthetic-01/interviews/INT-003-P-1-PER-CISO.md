---
interview_id: INT-003
run_id: 20261118-synthetic-01
task: P-1
persona: PER-CISO
date: 2026-11-18
topics: [C-SCRM frame, C-SCRM policy and strategy, C-SCRM levels and process, information sharing, maturity, measures, response framework, training]
---
# INT-003 — P-1 — PER-CISO

### Q1 {#INT-003.Q1}
Asked of: PER-CISO · Task: P-1
**A1 {#INT-003.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-001.A6]] [[product/architecture.md#leveraged]] [[product/conops.md#environment]] [[ASM-003]]
> My office leads C-SCRM for the Component. Its scope covers the acquisition, software
> development and sustainment processes; the Component's business and mission systems and the
> shared platforms they run on; cloud, software factory and cybersecurity services; and
> commercial software, open-source libraries, container base images and end-user hardware.
> Operational technology suppliers are in scope too, for the aviation support equipment the
> Component buys. We depend on commercial cloud regions under DoD provisional authorizations,
> DoD software factories, and their own upstream open-source and image suppliers, our critical
> fourth parties. We review the scope every year. Criticality follows the mission a supplier
> supports, how hard it is to replace, the access it gets to our data or networks, and whether
> it delivers code that runs inside our boundaries.

### Q2 {#INT-003.Q2}
Asked of: PER-CISO · Task: P-1
**A2 {#INT-003.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A1]] [[product/conops.md#limitations]]
> Our frame assumes that capable adversaries target software supply chains, chiefly
> open-source dependencies and build pipelines; that vulnerable third-party components reach
> production faster than hardened replacements can be issued, as the program's base image case
> shows; that a compromised shared platform hits every program on it at once; and that a
> software supplier compromise somewhere in our portfolio is likely within a year. We address
> adversarial, accidental, structural and environmental threat sources. Threat and impact
> assumptions are refined at the organization risk assessment and again in each system's risk
> assessment; vulnerability and likelihood assumptions are refined in the system assessment.
> We look at impact top-down from mission and bottom-up from systems, over a one-year horizon.
> Constraints: we buy through shared contract vehicles and inherit platform controls we cannot
> change; suppliers' sub-tier visibility is limited and open-source projects sign no
> agreements with us.

### Q3 {#INT-003.Q3}
Asked of: PER-CISO · Task: P-1
**A3 {#INT-003.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-001.A6]] [[INT-003.A2]]
> The risk board's appetite statement: the Component accepts moderate supply chain risk for
> business systems where a fallback exists, and low risk for components that carry code into
> mission systems. A quarter outside appetite triggers a council review and a report to the
> risk board. At Level 2 (mission and business) tolerance is no unmitigated high supplier risk
> for more than 30 days; at Level 3 (system) no critical or high vulnerability in a supplied
> component past its remediation date without an AO-approved POA&M item. Our priority is to
> protect build pipelines and shared platforms first, trading speed of new supplier adoption
> for vetting. Framing outputs: the policy, criticality list, assessment methodology,
> response guidance and monitoring guidance are in the Component C-SCRM policy and strategy;
> mission requirements, revised processes, operational requirements and acquisition guidance
> are in the strategy's annexes and the acquisition guide.

### Q4 {#INT-003.Q4}
Asked of: PER-CISO · Task: P-1
**A4 {#INT-003.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-001.A6]] [[ASM-003]]
> The Component C-SCRM policy covers Levels 1 and 2. It rests on the federal supply chain
> security law, DoDI 5200.44, DoDI 8500.01 and SP 800-161. Its statements: every acquisition
> of software, services or hardware for a Component system carries C-SCRM requirements, every
> supplier of critical components is assessed before award, and supplier incidents are
> reported to my office within 72 hours. My office owns it; program managers apply it in
> contracts. It is enforced through contract review, ATO package review and the annual
> program review. The strategy anchors to the Component risk management strategy; its
> objectives are to vet critical suppliers and to keep visibility of software components. It
> is funded from the cybersecurity budget line. Its first milestone is a Component-wide
> software bill of materials repository by 2027-06-30. Both are reviewed yearly; the last
> revision, on 2026-01-15, added software bills of materials.

### Q5 {#INT-003.Q5}
Asked of: PER-CISO · Task: P-1
**A5 {#INT-003.A5}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A4]]
> Level 1 issues the strategy and policy; Level 2 the implementation plan for each mission
> area; Level 3 each system's C-SCRM plan, which for a system is its supply chain risk
> management plan. Each level informs the next and reports back up. C-SCRM runs in each step:
> framing sets the criticality and appetite, assessment rates suppliers, response picks
> controls and contract terms, monitoring watches advisories and supplier changes. In the
> development life cycle it sits at component selection, build and release gates. Program
> assessments use our supplier questionnaire and the SP 800-161 assessment template. Our
> operations security office reviews what supplier risk information we share.

### Q6 {#INT-003.Q6}
Asked of: PER-CISO · Task: P-1
**A6 {#INT-003.A6}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A5]]
> For sharing we follow the SP 800-150 key practices: we set goals, inventory our internal
> sources, scope and rule what we share, join the Defense Industrial Base sharing community and
> a DoD software assurance community, enrich and automate feeds, keep agreements, protect
> what we hold and support the communities. The DoD's liaison to the Federal Acquisition
> Security Council handles supply chain risk information for us, through the DoD CIO. We share
> unclassified supplier information only: supplier names, advisories and assessment results.
> Shared information arrives with the threat feeds used by the organization risk assessment
> and each system risk assessment.

### Q7 {#INT-003.Q7}
Asked of: PER-CISO · Task: P-1
**A7 {#INT-003.A7}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A4]]
> Maturity: supplier inventories and contract clauses (foundational) are implemented; software
> bills of materials review (sustaining) is in progress; automated supplier risk scoring
> (enhancing) has not started; supplier incident reporting (sustaining) is implemented. Next we
> take up automated supplier risk scoring. Training: all personnel get annual awareness; buyers
> and engineers get role-based C-SCRM training using the DoD Cyber Workforce Framework; our
> supplier risk assessors have acquisition and software assurance experience.

### Q8 {#INT-003.Q8}
Asked of: PER-CISO · Task: P-1
**A8 {#INT-003.A8}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A3]] [[INT-003.A7]]
> We measure C-SCRM with a simple scorecard: share of new contracts with C-SCRM clauses
> (target 100%), days an unmitigated high supplier risk stays open against tolerance (target
> 30 days or fewer), and mission impact as supplier-caused outage hours against appetite
> (target none above 72 hours for business systems). The CIO and I are primary stakeholders,
> program managers secondary; the CIO validated the goals. The council reviews the scorecard
> quarterly. Supplier data we collect is kept in the C-SCRM repository with access limited to
> my office. Our Level 1 response framework entry is a compromised open-source dependency
> inserted by an adversary through a build pipeline; Level 2's is a shared platform's base
> image carrying a known vulnerability that the platform cannot patch in time.
