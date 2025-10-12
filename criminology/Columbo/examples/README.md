# Example CSV Files

This directory contains example CSV files demonstrating the Columbo data format.

## Files

- `demo_actors.csv` - Example actors (4 actors)
- `demo_edges.csv` - Example relationship claims (4 edges)
- `demo_evidence.csv` - Example evidence items (7 pieces of evidence)

## Usage

### Import Example Data

```python
from csv_io import import_graph_csv

# Import the demo graph
graph = import_graph_csv("examples/demo")

# Run analysis
from engine import run_analysis
report = run_analysis(graph)
```

### Via CLI

```bash
python columbo.py --csv examples/demo
```

## Field Descriptions

### demo_actors.csv
- `id`: Unique identifier (no PII)
- `role`: Actor role (INSTIGATOR, AGENCY, EXECUTIONER, VICTIM, etc.)
- `notes`: Brief description (abstract, no PII)

### demo_edges.csv
- `edge_id`: Unique edge identifier
- `src`, `dst`: Source and destination actor IDs
- `etype`: Edge type (FUNDING, COMMS, STAND_DOWN, COVERUP, etc.)
- `claim`: Natural language claim (abstract, high-level)
- `confidence`: Analyst confidence [0.0-1.0]
- `independence`: Source independence [0.0-1.0]
- `sources`: Semicolon-separated evidence IDs

### demo_evidence.csv
- `id`: Unique evidence identifier
- `stype`: Source type (FINREC, DOC, MEDIA, TESTIMONY, etc.)
- `summary`: Brief evidence summary
- `url_or_ref`: Optional reference (docket number, archive link)
- `integrity_score`: Evidence integrity [0.0-1.0]
- `contradicts`: Semicolon-separated edge IDs this evidence contradicts
- `supports`: Semicolon-separated edge IDs this evidence supports

## Creating Your Own

1. Copy these files as templates
2. Replace with your own synthetic/redacted data
3. Maintain abstract, high-level descriptions (no PII, no operational details)
4. Use consistent ID schemes (e.g., A_xxx for actors, E_xxx for edges, EV_xxx for evidence)
5. Test with: `python columbo.py --csv your_prefix`

## Safety Reminder

- No PII (names, addresses, phone, email, gov IDs)
- No operational details
- No weapons/targeting information
- Keep all descriptions abstract and high-level

See main README.md for full safety guidelines.

