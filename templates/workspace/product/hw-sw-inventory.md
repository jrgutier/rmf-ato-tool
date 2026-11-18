# Hardware and software list

## Items

| ID | Item | Kind | Component | Vendor | Product | Version | Quantity | Priority |
|---|---|---|---|---|---|---|---|---|
| INV-001 | One row per hardware, software or firmware item inside the boundary | software | CMP-EXAMPLE | vendor | product | version | per site or total | high, moderate or low |

Kinds: hardware, software, operating-system, firmware, virtual-machine, network-device,
database, service. The boundary's OSCAL component types are fewer: P-11 maps a virtual
machine, operating system, firmware or database engine to `software`, a network device to
`hardware` and a managed database or cloud offering to `service`. For virtual and cloud
items, one row per configuration item with its quantity is enough.

## Secure configuration

For each item, the STIG, SRG or other configuration guide it is held to (title and release;
program-built application software is usually held to the Application Security and
Development STIG) and the date of its last checklist review or scan.

## Release history

Each release: number, date, the environments it reached (pre-production, production) and
the components it changed, so an inventory version can be tied to what is fielded.

## Asset priority

Which assets matter most to the mission and why.
