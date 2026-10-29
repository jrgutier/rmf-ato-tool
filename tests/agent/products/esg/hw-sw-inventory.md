# ESG hardware and software list {#top}

> **FICTIONAL.** Invented for testing the `rmf` tool; vendors and products are fictional.

Inventory IDs are the program's configuration-item numbers; keep them unchanged. One row
describes the item as installed on every unit; quantities are per site.

## Items {#items}

| ID | Item | Kind | Component | Vendor | Product | Version | Qty per site | Priority |
|---|---|---|---|---|---|---|---|---|
| INV-001 | Gateway appliance | hardware | CMP-GW-HW | Example Rugged Devices (fictional) | ERD-400 edge appliance | rev C | 1 | high |
| INV-002 | Gateway operating system image | operating-system | CMP-GW-OS | Example Systems Integration Team (fictional) | ESG OS image | 2.1.4 | 1 | high |
| INV-003 | Sensor collector service | software | CMP-COLLECTOR | Example Systems Integration Team (fictional) | esg-collector | 2.1.4 | 1 | high |
| INV-004 | Admin web console | software | CMP-WEBUI | Example Systems Integration Team (fictional) | esg-console | 2.1.4 | 1 | high |
| INV-005 | Local buffer database | database | CMP-STORE | Example Data Engines (fictional) | EmbedStore | 5.3 | 1 | moderate |
| INV-006 | Field radio module firmware | firmware | CMP-GW-HW | Example Rugged Devices (fictional) | ERD radio firmware | 4.0.2 | 1 | moderate |
| INV-007 | Field sensor node | hardware | CMP-SENSOR-NET | Example Sensor Works (fictional) | ESW-20 sensor node | rev B | up to 40 | moderate |
| INV-008 | Sensor node firmware | firmware | CMP-SENSOR-NET | Example Sensor Works (fictional) | ESW node firmware | 1.9.0 | up to 40 | moderate |

## Asset priority {#priority}

The program ranks the gateway and its software (INV-001..INV-004) high, because losing or
corrupting them removes or falsifies a whole site's sensing. Sensor nodes and the buffer are
moderate: one failed node leaves a gap in coverage, and the buffer only matters while IODS is
unreachable.

## Hostnames {#hostnames}

Units are named `esg-<site>-01` (for example `esg-north-01`). They are physical (not
virtual), and none is reachable from the public internet.
