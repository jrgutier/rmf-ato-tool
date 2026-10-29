# FDR architecture

## Overview

FDR is one relay appliance running the relay service and a local report store, managed from
an operator console. Operators sign in through the enterprise identity provider.

## Components

- CMP-FDR: the Field Data Relay as a whole (this system).
- CMP-RELAY: the relay service software on the relay appliance.
- CMP-STORE: the PostgreSQL report store on the relay appliance.
- CMP-CONSOLE: the operator console workstation.
- CMP-IDP: the enterprise identity provider (external, separately authorized).

## Boundary

The authorization boundary encloses the relay appliance (relay service and report store)
and the operator console. The identity provider and the analysis enclave are outside it.

## Network

The appliance has two interfaces: a radio-side interface on the field network and an
enclave-side interface behind the enclave firewall. The console sits on the management VLAN.

## Data flow

Field units send signed reports to the relay service, which stores them and forwards them
over TLS to the analysis enclave. Operators review relay health from the console.

## Lifecycle

FDR is under development; first fielding follows developmental test.
