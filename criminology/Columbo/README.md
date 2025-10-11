# Columbo: Investigative Analysis Framework

A synthetic, abstract investigative analysis tool for examining relationships, claims, and evidence in complex cases. **No real PII or operational data.**

## Features

### Core Features
- **Graph-based modeling**: Actors, Edges (claims), and Evidence
- **Compartmentalized reasoning pools**: Multiple analytical perspectives
- **Safety guards**: Prevents operational detail, weapons info, targeting, or PII
- **Confidence & Independence scoring**: Track claim quality
- **OpenAI Agent Integration** ✨ NEW: Optional AI-enhanced reasoning (OFF by default)

### Add-ons (New!)

1. **CSV I/O** (`csv_io.py`)
   - Export/import actors, edges, and evidence to/from CSV
   - Preserve full graph state for sharing and version control

2. **Claim-Audit Report** (`audit.py`)
   - Pros (supporting evidence)
   - Cons (contradicting evidence)  
   - Falsifiers (what would disprove each claim)
   - Quality flags (low confidence, echo risk, etc.)

3. **Independence Checker** (`independence.py`)
   - Detects echo chambers via source overlap analysis
   - Adjusts independence scores based on source reuse
   - Flags overused sources

4. **Minimal Dash UI** (`dash_ui.py`)
   - Left panel: Interactive network graph
   - Right panel: Analysis findings
   - Color-coded by role and confidence

5. **Safety Unit Tests** (`test_safety.py`)
   - 20+ tests to ensure safety guard cannot be bypassed
   - Coverage for obfuscation, encoding, case tricks
   - Integration tests in full pipeline

6. **OpenAI Agent Integration** ✨ NEW (`agents.py`, `columbo.py`)
   - Optional AI-powered reasoning agents
   - **OFF by default** (preserves 100% safety test success)
   - Hybrid mode: combines rule-based + agent findings
   - Triple-layer safety: input check, output check, hybrid fusion
   - Command-line: `python columbo.py --agent`
   - See `AGENT_GUIDE.md` for full documentation

## Installation

```bash
# Basic (no UI, no agents)
# No external dependencies needed for core features

# With UI and Agents
pip install -r requirements.txt

# Just UI (no agents)
pip install dash plotly networkx

# Just Agents (no UI)
pip install openai
```

## Quick Start

### Basic Usage (Original)
```bash
python scenario_example.py
```

### Extended Demo (All Add-ons)
```bash
python scenario_example_extended.py
```

### Run Safety Tests
```bash
python test_safety.py    # Core safety tests (100% pass rate)
python test_agents.py    # Agent safety tests
```

### Command-Line Interface (NEW!)
```bash
# Rule-based mode (default)
python columbo.py

# With OpenAI agents (hybrid mode)
python columbo.py --agent

# Load from CSV with agents
python columbo.py --agent --csv my_case

# See all options
python columbo.py --help
```

## Usage Examples

### CSV I/O
```python
from csv_io import export_graph_csv, import_graph_csv

# Export
export_graph_csv(graph, prefix="my_case")
# Creates: my_case_actors.csv, my_case_edges.csv, my_case_evidence.csv

# Import
graph = import_graph_csv(prefix="my_case")
```

### Audit Report
```python
from audit import generate_claim_audit, print_audit_report

audit_report = generate_claim_audit(graph)
print_audit_report(audit_report)
```

### Independence Check
```python
from independence import check_source_independence, print_independence_report

independence_report = check_source_independence(graph)
print_independence_report(independence_report)
```

### Dash UI
```python
from dash_ui import launch_ui
from engine import run_analysis

report = run_analysis(graph)
launch_ui(graph, report, port=8050)
# Opens browser at http://localhost:8050
```

## File Structure

```
Columbo/
├── models.py              # Core data structures (Actor, Edge, Evidence, Graph)
├── engine.py              # Analysis orchestration
├── reasoning_pool.py      # Compartmentalized reasoning functions
├── safety.py              # Safety guard (blocks harmful content)
├── csv_io.py              # CSV export/import ✨ NEW
├── audit.py               # Claim-audit reports ✨ NEW
├── independence.py        # Source independence checker ✨ NEW
├── dash_ui.py             # Minimal Dash UI ✨ NEW
├── test_safety.py         # Safety guard unit tests ✨ NEW
├── test_agents.py         # Agent safety tests ✨ NEW
├── agents.py              # OpenAI agent integration ✨ NEW
├── columbo.py             # CLI with --agent flag ✨ NEW
├── scenario_example.py    # Original basic demo
├── scenario_example_extended.py  # Extended demo ✨ NEW
├── requirements.txt       # Dependencies ✨ NEW
├── README.md             # This file
└── AGENT_GUIDE.md        # Agent documentation ✨ NEW
```

## CSV Schemas

### actors.csv
```
id,role,notes
A_inst,INSTIGATOR,Unknown sponsor
A_fac1,AGENCY,Security org Alpha
```

### edges.csv
```
edge_id,src,dst,etype,claim,confidence,independence,sources
E1,A_inst,A_fac1,FUNDING,"Indirect funding flows",0.6,0.5,"EV1;EV3"
```

### evidence.csv
```
id,stype,summary,url_or_ref,integrity_score,contradicts,supports
EV1,FINREC,"Unusual transfers",,0.5,,E1
```

## Safety Philosophy

This tool is designed for **abstract analysis only**:
- ✅ Patterns, hypotheses, risk flags
- ✅ High-level relationship analysis
- ❌ Operational details
- ❌ Weapons/targeting information
- ❌ Personal identifying information

The safety guard actively blocks harmful content. See `test_safety.py` for bypass prevention tests.

## Roles

- `INSTIGATOR`: Suspected sponsor/planner
- `FACILITATOR`: Enabling entity
- `EXECUTIONER`: Direct actor
- `VICTIM`: Target/affected party
- `WITNESS`: Observer
- `AGENCY`: Organizational entity
- `ORG`: General organization
- `UNKNOWN`: Undefined role

## Edge Types

- `FUNDING`: Financial flows
- `COMMS`: Communication patterns
- `TASKING`: Direction/orders
- `STAND_DOWN`: Operational posture changes
- `COVERUP`: Post-event narrative control
- `PROPAGANDA`: Information operations
- `OTHER`: Miscellaneous

## Testing

Run the safety test suite:
```bash
python test_safety.py
```

Expected output:
```
SAFETY GUARD TEST SUITE
================================================================================

test_basic_banned_keywords (__main__.TestSafetyGuard) ... ok
test_case_insensitivity (__main__.TestSafetyGuard) ... ok
...

================================================================================
Tests run: 20+
Success rate: 100%
================================================================================
```

## License

This is a synthetic educational/analytical tool. Use responsibly.

## Contributing

When adding features:
1. Maintain safety-first philosophy
2. Keep abstractions high-level
3. Add tests for any safety-related changes
4. Update this README with new capabilities

## Future Enhancements

Potential additions:
- Timeline analysis
- Bayesian probability updates
- Multi-graph comparison
- Advanced LLM integration with safety rails
- Export to other graph formats (GraphML, GEXF)


