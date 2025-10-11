# OpenAI agent integration for reasoning pools.
# Agents are OFF by default. Enable with --agent flag.

import os
from typing import List, Optional
from models import Graph, Edge
from safety import safety_guard

# Agent configuration
AGENTS_ENABLED = False  # Default: OFF (preserves 100% safety test success)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def enable_agents(enabled: bool = True):
    """Enable or disable agent-based reasoning."""
    global AGENTS_ENABLED
    if enabled and not OPENAI_AVAILABLE:
        print("[ERROR] OpenAI not installed. Run: pip install openai")
        print("        Agents will remain disabled.")
        return False
    AGENTS_ENABLED = enabled
    return True

def get_agents_status() -> dict:
    """Get current agent configuration status."""
    return {
        'enabled': AGENTS_ENABLED,
        'openai_available': OPENAI_AVAILABLE,
        'api_key_set': bool(os.getenv('OPENAI_API_KEY'))
    }

# ===== AGENT-BASED REASONING POOLS =====

def agent_instigator_view(g: Graph) -> List[str]:
    """
    Agent-based analysis from instigator perspective.
    Sees funding/tasking edges only.
    """
    if not AGENTS_ENABLED or not OPENAI_AVAILABLE:
        return []
    
    try:
        client = OpenAI()
        
        # Build context from graph (funding/tasking edges only)
        context_edges = []
        for eid, e in g.edges.items():
            if e.etype in ("FUNDING", "TASKING"):
                # Safety check BEFORE sending to agent
                claim_check = safety_guard(e.claim)
                if claim_check["status"] != "ok":
                    return [f"BLOCKED: Agent input contained unsafe content"]
                
                context_edges.append(
                    f"Edge {eid}: {e.src} -> {e.dst} ({e.etype})\n"
                    f"  Claim: {e.claim}\n"
                    f"  Confidence: {e.confidence}, Independence: {e.independence}"
                )
        
        if not context_edges:
            return []
        
        # Create prompt
        prompt = f"""You are an analyst examining potential instigation patterns in a case.
Focus ONLY on funding and tasking relationships. Be abstract and analytical.

STRICT RULES:
- No operational details
- No weapons information
- No targeting information
- No PII
- Use only high-level analytical language

Context:
{chr(10).join(context_edges)}

Task: Provide 1-2 brief hypotheses about potential instigation patterns.
Format each as "H: [hypothesis] [edge_id] cf=X.XX/ind=X.XX"
"""
        
        # Call OpenAI agent
        response = client.responses.create(
            model="gpt-4",  # Use gpt-4 or gpt-4-turbo for production
            input=prompt
        )
        
        output = response.output_text.strip()
        
        # Safety check AFTER agent response
        safety_check = safety_guard(output)
        if safety_check["status"] != "ok":
            return [f"BLOCKED: Agent output violated safety: {safety_check['reason']}"]
        
        # Parse output into list
        hypotheses = [line.strip() for line in output.split('\n') if line.strip()]
        return hypotheses[:2]  # Limit to 2 hypotheses
        
    except Exception as e:
        return [f"[AGENT_ERROR] {str(e)}"]

def agent_facilitator_view(g: Graph) -> List[str]:
    """
    Agent-based analysis from facilitator perspective.
    Sees stand-down/cover-up edges only.
    """
    if not AGENTS_ENABLED or not OPENAI_AVAILABLE:
        return []
    
    try:
        client = OpenAI()
        
        # Build context (stand-down/coverup edges only)
        context_edges = []
        for eid, e in g.edges.items():
            if e.etype in ("STAND_DOWN", "COVERUP"):
                # Safety check BEFORE sending
                claim_check = safety_guard(e.claim)
                if claim_check["status"] != "ok":
                    return [f"BLOCKED: Agent input contained unsafe content"]
                
                context_edges.append(
                    f"Edge {eid}: {e.src} -> {e.dst} ({e.etype})\n"
                    f"  Claim: {e.claim}\n"
                    f"  Confidence: {e.confidence}, Independence: {e.independence}"
                )
        
        if not context_edges:
            return []
        
        prompt = f"""You are an analyst examining potential facilitation patterns in a case.
Focus on institutional behavior and operational posture changes.

STRICT RULES:
- No operational details
- No weapons information
- No targeting information
- No PII
- Use only high-level analytical language

Context:
{chr(10).join(context_edges)}

Task: Provide 1-2 brief risk flags about potential facilitation patterns.
Format each as "RISK: [description] [edge_id] cf=X.XX ind=X.XX"
"""
        
        response = client.responses.create(
            model="gpt-4",
            input=prompt
        )
        
        output = response.output_text.strip()
        
        # Safety check AFTER
        safety_check = safety_guard(output)
        if safety_check["status"] != "ok":
            return [f"BLOCKED: Agent output violated safety: {safety_check['reason']}"]
        
        flags = [line.strip() for line in output.split('\n') if line.strip()]
        return flags[:2]
        
    except Exception as e:
        return [f"[AGENT_ERROR] {str(e)}"]

def agent_executioner_view(g: Graph) -> List[str]:
    """
    Agent-based analysis from execution perspective.
    Sees comms/propaganda edges only. MAXIMUM safety enforcement.
    """
    if not AGENTS_ENABLED or not OPENAI_AVAILABLE:
        return []
    
    try:
        client = OpenAI()
        
        # Build context (comms/propaganda only)
        context_edges = []
        for eid, e in g.edges.items():
            if e.etype in ("COMMS", "PROPAGANDA", "OTHER"):
                # Safety check BEFORE sending
                claim_check = safety_guard(e.claim)
                if claim_check["status"] != "ok":
                    return [f"BLOCKED: Agent input contained unsafe content"]
                
                context_edges.append(
                    f"Edge {eid}: {e.src} -> {e.dst} ({e.etype})\n"
                    f"  Claim: {e.claim}\n"
                    f"  Confidence: {e.confidence}, Independence: {e.independence}"
                )
        
        if not context_edges:
            return []
        
        prompt = f"""You are an analyst examining communication patterns in a case.
Focus ONLY on meta-patterns (frequency, timing, channels). NO operational details.

ABSOLUTE PROHIBITIONS:
- No methods, techniques, or procedures
- No weapons information
- No targeting information
- No operational planning details
- No PII
- Use ONLY abstract pattern language

Context:
{chr(10).join(context_edges)}

Task: Provide 1 brief observation about communication patterns.
Format as "Pattern: [description] [edge_id]"
"""
        
        response = client.responses.create(
            model="gpt-4",
            input=prompt
        )
        
        output = response.output_text.strip()
        
        # Safety check AFTER
        safety_check = safety_guard(output)
        if safety_check["status"] != "ok":
            return [f"BLOCKED: Agent output violated safety: {safety_check['reason']}"]
        
        patterns = [line.strip() for line in output.split('\n') if line.strip()]
        return patterns[:1]  # Limit to 1 pattern (highest risk category)
        
    except Exception as e:
        return [f"[AGENT_ERROR] {str(e)}"]

# ===== HYBRID MODE =====

def hybrid_assessment(rule_based: List[str], agent_based: List[str]) -> List[str]:
    """
    Combine rule-based and agent-based findings.
    Rule-based findings always included (they passed safety tests).
    Agent findings added only if they pass safety.
    """
    combined = list(rule_based)  # Start with safe rule-based findings
    
    for finding in agent_based:
        # Double-check safety
        if not finding.startswith("BLOCKED") and not finding.startswith("[AGENT_ERROR]"):
            safety_check = safety_guard(finding)
            if safety_check["status"] == "ok":
                combined.append(f"[AGENT] {finding}")
            else:
                combined.append(f"BLOCKED: Agent finding failed safety")
        else:
            combined.append(finding)  # Include error messages
    
    return combined

