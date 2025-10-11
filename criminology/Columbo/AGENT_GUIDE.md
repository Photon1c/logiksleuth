# Agent Integration Guide

## Overview

Columbo now supports **OpenAI-powered agents** for enhanced reasoning. Agents are **OFF by default** to preserve the 100% safety test success rate with rule-based reasoning.

## Safety-First Design

### Triple-Layer Safety
1. **Input Safety**: Claims are checked BEFORE being sent to agents
2. **Output Safety**: Agent responses are checked BEFORE being displayed
3. **Hybrid Mode**: Agent findings are COMBINED with rule-based findings (never replace them)

### Default: OFF
```python
# Agents are disabled by default
AGENTS_ENABLED = False  # Preserves 100% safety test success
```

## Quick Start

### 1. Install OpenAI Package
```bash
pip install openai
```

### 2. Set API Key
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows
set OPENAI_API_KEY=sk-...
```

### 3. Run with Agents
```bash
# Command-line
python columbo.py --agent

# Verbose mode
python columbo.py --agent --verbose
```

### 4. Programmatic Usage
```python
from models import Graph, Actor, Edge
from engine import run_analysis
from agents import enable_agents

# Enable agents
enable_agents(True)

# Build graph
g = Graph()
# ... add actors, edges, evidence ...

# Run with agents (hybrid mode)
report = run_analysis(g, use_agents=True)

# Check mode
print(f"Agent mode: {report['agent_mode']}")
print(f"Findings: {report['findings']}")
```

## How It Works

### Hybrid Mode
When agents are enabled, Columbo runs in **hybrid mode**:

1. **Rule-based reasoning** runs first (100% safety tested)
2. **Agent-based reasoning** runs in parallel (3 specialized agents)
3. **Hybrid assessment** combines both outputs
4. **Safety guards** validate all findings

```
Rule-based     Agent-based
   Pool    +      Pool      → Hybrid → Safety → Output
(tested)      (enhanced)     Fusion    Check
```

### Three Specialized Agents

#### 1. Instigator Agent
- **Scope**: FUNDING, TASKING edges only
- **Task**: Generate hypotheses about instigation patterns
- **Output format**: `H: [hypothesis] [edge_id] cf=X.XX/ind=X.XX`
- **Prompt constraints**: Abstract, no operational details

#### 2. Facilitator Agent
- **Scope**: STAND_DOWN, COVERUP edges only
- **Task**: Generate risk flags about facilitation patterns
- **Output format**: `RISK: [description] [edge_id] cf=X.XX ind=X.XX`
- **Prompt constraints**: Institutional behavior focus

#### 3. Executioner Agent
- **Scope**: COMMS, PROPAGANDA, OTHER edges only
- **Task**: Identify meta-patterns in communications
- **Output format**: `Pattern: [description] [edge_id]`
- **Prompt constraints**: MAXIMUM safety (no methods/procedures)

### Agent Output Tagging
Agent-generated findings are tagged with `[AGENT]`:
```
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50  # Rule-based
- [AGENT] H: Complex funding network suggests coordination [E1]  # Agent-enhanced
```

## API Configuration

### OpenAI API Format
Columbo uses the latest OpenAI API format:

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-4",
    input="Your prompt here"
)
output = response.output_text
```

### Model Selection
Default: `gpt-4`

To change models, edit `agents.py`:
```python
response = client.responses.create(
    model="gpt-4-turbo",  # or "gpt-3.5-turbo", "gpt-4o", etc.
    input=prompt
)
```

## Safety Enforcement

### Banned Content
All agent inputs and outputs are checked against:
- Operational details
- Weapons information
- Targeting information
- PII (personally identifiable information)
- Tactical procedures

### Safety Check Example
```python
from safety import safety_guard

# Before sending to agent
claim_check = safety_guard(edge.claim)
if claim_check["status"] != "ok":
    return ["BLOCKED: Agent input contained unsafe content"]

# After receiving from agent
output_check = safety_guard(agent_response)
if output_check["status"] != "ok":
    return ["BLOCKED: Agent output violated safety"]
```

### Blocked Output
If unsafe content is detected:
```
- BLOCKED: Agent output violated safety: Contains banned pattern: kill
```

## Testing

### Run Agent Tests
```bash
python test_agents.py
```

### Test Coverage
1. **Agents disabled by default** ✓
2. **Rule-based mode always works** ✓
3. **Graceful fallback if API unavailable** ✓
4. **Dangerous claims blocked in agent mode** ✓
5. **Agent status reporting** ✓
6. **Enable/disable functionality** ✓

### Integration Tests (require API key)
```bash
export OPENAI_API_KEY="sk-..."
python test_agents.py
```

Integration tests validate:
- Agent mode produces valid output
- Safety enforcement on agent responses
- Hybrid mode combines findings correctly

## Command-Line Interface

### Usage
```bash
python columbo.py [OPTIONS]
```

### Options
```
--agent           Enable OpenAI agents (default: OFF)
--verbose, -v     Show mode information
--csv PREFIX      Load graph from CSV files
--help, -h        Show help message
```

### Examples
```bash
# Default: rule-based only
python columbo.py

# With agents
python columbo.py --agent

# With agents and verbose output
python columbo.py --agent --verbose

# Load from CSV with agents
python columbo.py --agent --csv my_case
```

### Environment Variables
```
OPENAI_API_KEY    Required for --agent mode
```

## Programmatic API

### Check Agent Status
```python
from agents import get_agents_status

status = get_agents_status()
print(f"Enabled: {status['enabled']}")
print(f"OpenAI available: {status['openai_available']}")
print(f"API key set: {status['api_key_set']}")
```

### Enable/Disable Agents
```python
from agents import enable_agents

# Enable
success = enable_agents(True)
if not success:
    print("Failed to enable agents")

# Disable
enable_agents(False)
```

### Run Analysis
```python
from engine import run_analysis

# Rule-based (default)
report = run_analysis(graph, use_agents=False)

# Hybrid mode
report = run_analysis(graph, use_agents=True)

# Check which mode was used
if report['agent_mode']:
    print("Ran in hybrid mode")
else:
    print("Ran in rule-based mode")
```

## Troubleshooting

### "OpenAI not installed"
```bash
pip install openai
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### "Agents requested but not enabled"
Agents must be explicitly enabled:
```python
from agents import enable_agents
enable_agents(True)
```

### API Errors
Agent mode gracefully falls back to rule-based:
```
[AGENT_ERROR] API connection failed
- H: Funding/Tasking link plausible [E1] ...  # Falls back to rules
```

## Best Practices

### 1. Start with Rule-Based
Always validate your graph with rule-based reasoning first:
```bash
python columbo.py  # Test without agents
python columbo.py --agent  # Then try with agents
```

### 2. Monitor Agent Output
Use `--verbose` to see when agents are active:
```bash
python columbo.py --agent --verbose
```

### 3. Validate Findings
Agent findings are marked with `[AGENT]` tag - review them carefully:
```python
for finding in report['findings']:
    if '[AGENT]' in finding:
        print(f"Agent-generated: {finding}")
```

### 4. Rate Limiting
OpenAI has rate limits. For large batches:
```python
import time

for graph in graphs:
    report = run_analysis(graph, use_agents=True)
    # Process report...
    time.sleep(1)  # Respect rate limits
```

### 5. Cost Management
Monitor token usage (agents call API 3 times per analysis):
- Each agent call ~200-500 tokens
- Total per analysis: ~600-1500 tokens
- Cost depends on model (GPT-4 vs GPT-3.5-turbo)

## Architecture

### Module Structure
```
agents.py
├── Agent Configuration
│   ├── AGENTS_ENABLED (default: False)
│   ├── enable_agents()
│   └── get_agents_status()
├── Agent Pools
│   ├── agent_instigator_view()
│   ├── agent_facilitator_view()
│   └── agent_executioner_view()
└── Hybrid Assessment
    └── hybrid_assessment()

engine.py
├── run_analysis(use_agents=False)
├── Mode Selection
│   ├── Rule-based (default)
│   └── Hybrid (if use_agents=True)
└── Graceful Fallback

columbo.py
├── CLI Argument Parsing
├── --agent flag
├── Agent Initialization
└── Analysis Execution
```

### Safety Flow
```
User Input
    ↓
Graph Creation
    ↓
Engine (run_analysis)
    ↓
┌───────────────────────────────────┐
│ If use_agents=True:               │
│   ├─ Rule-based pools → Safe ✓    │
│   ├─ Agent pools → Check input ✓  │
│   └─ Hybrid fusion → Check output ✓│
│ Else:                             │
│   └─ Rule-based pools only ✓      │
└───────────────────────────────────┘
    ↓
Safety Guard
    ↓
Output
```

## Future Enhancements

Potential improvements:
1. **Confidence scoring**: Agents estimate confidence/independence
2. **Source validation**: Agents check evidence consistency
3. **Claim generation**: Agents suggest new edges based on evidence
4. **Timeline analysis**: Agents detect temporal patterns
5. **Multi-agent debate**: Agents challenge each other's findings
6. **Explainability**: Agents justify their reasoning

## License & Ethics

### Ethical Use
- Use ONLY for legitimate investigative analysis
- No operational planning or targeting
- Respect privacy and legal boundaries
- Follow institutional guidelines

### Safety Commitment
Agents are designed with safety-first principles:
- Multiple validation layers
- Strict prompt constraints
- Hybrid mode preserves tested baseline
- Open source for auditability

---

For questions or issues, refer to the main README.md or test files.

