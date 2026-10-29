# FDR program

## Mission

FDR delivers sensor reports from field units to the program's analysts within minutes.
Analysts tolerate an outage of up to a day, because field units buffer reports.

## Organization

The program office reports to the component CIO, who appoints the authorizing official.
The enterprise security office (CISO) runs the analysis enclave and its common controls.

## Stakeholders

The sponsor, the program manager, the ISSM and ISSO, the developer team, the information
owner, the security control assessor and the authorizing official.

## Risk management

The component accepts moderate residual risk for developmental systems that carry a dated
POA&M. Organizational threats of concern are compromised field units and insider misuse of
administrator accounts.

## Requirements

Every interactive user authenticates with CAC multi-factor authentication; reports are
signed by field units and protected in transit with TLS; the appliance follows DISA STIGs.

## Registration

New systems are registered in the component system registry before categorization.

## Monitoring

The organization requires monthly vulnerability scans, quarterly control assessments of a
third of the baseline, and a quarterly security status report to the AO.

## Information life cycle

Sensor reports are kept in the report store for 30 days after forwarding, then purged;
configuration backups are kept for one year.
