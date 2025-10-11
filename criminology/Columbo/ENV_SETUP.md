# Environment Setup for OpenAI Agents

## Quick Setup

### 1. Create `.env` file
Create a file named `.env` in the Columbo directory with your API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Install Dependencies
```bash
pip install python-dotenv openai
```

### 3. Run with Agents
```bash
# Use columbo.py (not scenario_example.py)
python columbo.py --agent
```

## Which Script to Use?

### ❌ DON'T USE for agents:
```bash
python scenario_example.py --agent  # This doesn't support --agent flag
```

### ✅ USE for agents:
```bash
python columbo.py --agent           # This supports --agent flag
```

## Understanding the Output

### Rule-Based Mode (Default)
```
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50
- Pattern: comms pressure observed [E2]
- RISK: Operational posture downgraded [E3] cf=0.70 ind=0.70
```

### Hybrid Mode (With --agent)
```
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50
- [AGENT] H: Complex funding network suggests coordination [E1]
- Pattern: comms pressure observed [E2]
- [AGENT] Pattern: Communication frequency increased pre-event [E2]
- RISK: Operational posture downgraded [E3] cf=0.70 ind=0.70
```

Notice the `[AGENT]` tags showing AI-generated findings!

## What Your Results Mean

Your output showed:
```
- H: Funding/Tasking link plausible [E1] cf=0.60/ind=0.50
```

This means:
- **H:** Hypothesis (from instigator perspective)
- **[E1]:** Edge ID being analyzed
- **cf=0.60:** Confidence score (0-1 scale) = 60% confident
- **ind=0.50:** Independence score = 50% source independence

```
- RISK: Operational posture downgraded on event day [E3] cf=0.70 ind=0.70
```

This means:
- **RISK:** Risk flag (from facilitator perspective)
- **[E3]:** Edge showing stand-down behavior
- **cf=0.70:** 70% confidence in this claim
- **ind=0.70:** 70% independent sources (low echo chamber risk)

## Testing Without API Key

```bash
python columbo.py --agent --verbose
```

Will show:
```
[MODE] Agent-enhanced reasoning ENABLED
[WARN] OPENAI_API_KEY not set. Using rule-based mode.
[RULE-BASED MODE]
```

This is **graceful fallback** - the system always works!

## Files Overview

| File | Supports --agent? | Purpose |
|------|-------------------|---------|
| `scenario_example.py` | ❌ No | Simple demo (rule-based only) |
| `scenario_example_extended.py` | ❌ No | Extended demo (all add-ons except agents) |
| `columbo.py` | ✅ Yes | CLI with --agent flag support |

## Next Steps

1. Create `.env` file with your API key
2. Run: `python columbo.py --agent --verbose`
3. Compare output with: `python columbo.py` (no agents)

See the difference? That's AI enhancement in action!

