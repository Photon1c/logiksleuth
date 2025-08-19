# Murder Accountability Project Fork

This space is meant to serve as an initial open-source space for a collection of scripts and tools for open-source use.

The aim is to aid in the analysis of the murder accountability project's datasets. This space is evolving fast, a few upgrades are in the works:

- Agent integration for in-depth feature engineering and ML layer integrations.
- Three.js globe visualization with multi-layer data graphic filters.
- Law enforcement cooperation through live agent development and monitoring (following BOLA wrap model, currently not available to the public)

<details><summary>Project Map</summary>

Protecting PII (Personally Identifiable Information) is done by implementing strict and rigosour filters that are run throughout different stages.
```mermaid
flowchart TD
  A["Source Intake (UCR, MAP, court dockets, news, FOIA)"] --> B{Case Status?}
  B -->|Closed/Convicted| C["PII Scan (regex + heuristics)"]
  B -->|Active/Pending| D["Minimal Fields Extract (age band, sex, MO, county, date band)"]
  B -->|Unknown| E["Status Resolver (rule: docket/API check)"]

  C --> F{PII Risk?}
  F -->|Low| G["Normalize & Link (IDs, MO, geo grid, time bins)"]
  F -->|High| H["Quarantine Queue (manual review + redaction tasks)"]

  D --> I["Auto-Deidentify (name→drop, DOB→year, addr→city centroid, GPS→~10km geohex, date→week band)"]
  I --> J{Quality OK?}
  J -->|Yes| G
  J -->|No| H

  E -->|Resolved=Closed| C
  E -->|Resolved=Active| D
  E -->|Unresolvable| H

  G --> K["Access Tagger (public/research/restricted/LE)"]
  K --> L[(Research Lake)]
  H --> M[(Restricted Vault)]

  subgraph Oversight
    N["Audit Log (field changes, reviewer, time)"]
    O["Policy Engine (RBAC, retention, re-ID safeguards)"]
  end
  A --> N
  C --> N
  D --> N
  H --> N
  K --> O
```

</details>

