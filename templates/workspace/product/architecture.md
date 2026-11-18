# Architecture

Replace each section's guidance with your system's design. Keep the headings; run
artifacts cite them by slug (`product/architecture.md#identity-and-access`).

## Components

| ID | Component | Type | Inside the boundary | Notes |
|---|---|---|---|---|
| CMP-EXAMPLE | One row per component (hardware, software, service) | software | yes | Give every component a stable CMP-* ID; list external systems and services too, marked "no" |

## Authorization boundary

What is inside the boundary, what is outside, and where the edge is.

## Network architecture

Interfaces, networks, permitted traffic (ports, protocols, directions) and segmentation.

## Interconnections

Each connected system: direction, agreement and its own authorization.

| Connection | Other system | Its AO | Direction | Agreement (ISA, MOA, MOU, SLA) | Reference | Status (signed, draft, interim approval) | Date | Signatories |
|---|---|---|---|---|---|---|---|---|
| CONN-01 | example system | title of its AO | in, out or both | ISA | ISA-0001 | signed | 2026-01-01 | both AOs |

## Leveraged authorizations

Each separately authorized provider whose controls the system inherits, what it covers, the
decision and the date authorized.

## Identity and access

How each user group authenticates, how accounts are requested, approved, reviewed and
removed, local or shared accounts, lockout and session settings.

## Logging

Which events each component logs, where logs go, retention, and who reviews them how often.

## Configuration management

The secure configuration baseline (which SRGs or STIGs), how it is applied and checked for
drift, and how changes are approved.

## Software updates

How updates are built, verified and installed, and how current fielded units are.

## Physical protection

Where equipment is and how it is protected.
