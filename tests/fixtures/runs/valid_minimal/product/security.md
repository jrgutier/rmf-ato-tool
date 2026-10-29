# FDR security design

## Accounts

Operator and administrator accounts come from the enterprise identity provider; local
accounts are limited to one break-glass administrator. Accounts are reviewed quarterly.

## Audit

The relay service and the operating system log sign-in, configuration change and relay
errors to the appliance audit log, which is forwarded to the enclave SIEM.

## Configuration

The appliance is built from a hardened RHEL 9 image that applies the DISA STIG settings.

## Authentication

All interactive sign-ins use CAC-based multi-factor authentication through the identity
provider.

## Boundary protection

The enclave firewall allows only TLS from the relay to the enclave ingest service; the
radio-side interface accepts only signed report traffic.

## Patching

Security patches are applied monthly from the program's mirrored repositories.
