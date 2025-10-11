# Orchestrates: load graph, run pools, emit audit tables.

from typing import Dict
from models import Graph, Actor, Edge, Evidence
from reasoning_pool import (pool_instigator_view,
                            pool_facilitator_view,
                            pool_executioner_view,
                            fuse_assessment)

def run_analysis(g: Graph, use_agents: bool = False) -> Dict[str, object]:
    # Choose reasoning mode based on flag
    if use_agents:
        try:
            from agents import (agent_instigator_view,
                               agent_facilitator_view,
                               agent_executioner_view,
                               hybrid_assessment,
                               get_agents_status)
            
            status = get_agents_status()
            if not status['enabled']:
                print("[WARN] Agents requested but not enabled. Using rule-based mode.")
                use_agents = False
            elif not status['api_key_set']:
                print("[WARN] OPENAI_API_KEY not set. Using rule-based mode.")
                use_agents = False
        except ImportError:
            print("[WARN] Agent module not available. Using rule-based mode.")
            use_agents = False
    
    if use_agents:
        # Hybrid mode: combine rule-based (safe) + agent-based (enhanced)
        p1_rules = pool_instigator_view(g)
        p2_rules = pool_facilitator_view(g)
        p3_rules = pool_executioner_view(g)
        
        p1_agent = agent_instigator_view(g)
        p2_agent = agent_facilitator_view(g)
        p3_agent = agent_executioner_view(g)
        
        p1 = hybrid_assessment(p1_rules, p1_agent)
        p2 = hybrid_assessment(p2_rules, p2_agent)
        p3 = hybrid_assessment(p3_rules, p3_agent)
    else:
        # Rule-based mode (default, 100% safety tested)
        p1 = pool_instigator_view(g)
        p2 = pool_facilitator_view(g)
        p3 = pool_executioner_view(g)
    
    fused = fuse_assessment([p1, p2, p3])

    # Quick “case health” metrics
    avg_conf = (sum(e.confidence for e in g.edges.values()) /
                max(1, len(g.edges)))
    avg_ind = (sum(e.independence for e in g.edges.values()) /
               max(1, len(g.edges)))

    return {
        "actors": list(g.actors.values()),
        "edge_count": len(g.edges),
        "evidence_count": len(g.evidence),
        "avg_confidence": round(avg_conf, 3),
        "avg_independence": round(avg_ind, 3),
        "findings": fused,
        "agent_mode": use_agents
    }
