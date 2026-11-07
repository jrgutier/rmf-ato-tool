---
artifact_id: ART-PIA
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-14
touched_by: [P-14]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Privacy impact assessment

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-PIA (playbook: playbooks/P/P-14.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment.
     A system with no PII, or one P-12 found needs no PIA, writes the Determination section only,
     stating the not-required determination and its basis; artifacts/data/pia.yaml is then not
     written. -->

## Determination

<<FILL: the PIA determination P-12 recorded in artifacts/data/infotypes.yaml privacy.pia (required, adapted or not required), its DoDI 5400.16 basis and when the PIA is due; for an NSS excluded from the requirement, how its privacy implications were considered; with tokens>>

## Assessment

<<FILL: what the PIA on DD Form 2930 (or 2930A) states, as in pia.yaml assessment: how PII handling conforms to legal, regulatory and policy requirements, the need for the PII, its privacy risks and effects, and the protections and alternative processes examined to mitigate them, with tokens>>

## Coordination, reviews and approval

<<FILL: who the PM coordinated the PIA through (ISSM, privacy representative, records management office) and when, the PER-CISO review for cybersecurity policy and the PER-PRIV review for privacy policy, and the final approval by the Component CIO or reviewing official before the authorization decision, with tokens>>

## Submission, publication and updates

<<FILL: the submission of the approved PIA to the DoD CIO, the publication of section 1 in the Component's public repository (or why publication is restricted) and that it stays there while the system holds PII, and each later review of the PIA (a change creating new privacy risk, an authorization, a change in posture), with tokens>>
