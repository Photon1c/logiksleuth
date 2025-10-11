# Quick Start: OpenAI Agents

## Installation
```bash
pip install openai
export OPENAI_API_KEY="sk-your-key-here"
```

## Usage

### Command Line
```bash
# Default: rule-based (no agents)
python columbo.py

# With OpenAI agents
python columbo.py --agent

# Verbose mode
python columbo.py --agent --verbose

# Help
python columbo.py --help
```

### Python API
```python
from agents import enable_agents
from engine import run_analysis
from models import Graph

# Enable agents
enable_agents(True)

# Build your graph
g = Graph()
# ... add actors, edges, evidence ...

# Run with agents
report = run_analysis(g, use_agents=True)

# Check mode
print(f"Agent mode: {report['agent_mode']}")
```

## Safety

- **Agents OFF by default** ✓
- **Triple-layer safety checks** ✓
- **Graceful fallback** if API unavailable ✓
- **100% test pass rate** ✓

## Testing
```bash
python test_safety.py    # Core safety tests
python test_agents.py    # Agent safety tests
```

## Documentation
- **README.md**: Main documentation
- **AGENT_GUIDE.md**: Complete agent guide (450+ lines)
- **AGENT_IMPLEMENTATION.md**: Technical details
- **FINAL_SUMMARY.md**: Full implementation summary

## What You Get

### Without --agent (Default)
```
[RULE-BASED MODE]
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50
- Pattern: comms pressure observed [E2]
- RISK: Operational posture downgraded [E3] cf=0.70 ind=0.70
```

### With --agent
```
[HYBRID MODE: Rule-based + OpenAI Agents]
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50
- [AGENT] H: Complex funding network suggests coordination [E1]
- Pattern: comms pressure observed [E2]
- [AGENT] Pattern: Communication frequency increased pre-event [E2]
- RISK: Operational posture downgraded [E3] cf=0.70 ind=0.70
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

### API Error
System automatically falls back to rule-based mode ✓

## Status Check
```python
from agents import get_agents_status

status = get_agents_status()
print(f"Enabled: {status['enabled']}")
print(f"OpenAI available: {status['openai_available']}")
print(f"API key set: {status['api_key_set']}")
```

---

**TIP**: Start with rule-based mode, then try --agent when ready!

