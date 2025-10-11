# “Reasoning pools” (placeholders for LLMs or rules).
# Compartmentalized: each pool only sees a slice of the graph.

from typing import Dict, List
from models import Graph, Edge
from safety import safety_guard

def pool_instigator_view(g: Graph) -> List[str]:
    # sees funding/tasking edges only; returns hypotheses (safe).
    hyps = []
    for eid, e in g.edges.items():
        if e.etype in ("FUNDING","TASKING"):
            hyps.append(f"H: Funding/Tasking link plausible [{eid}] "
                        f"cf={e.confidence:.2f}/ind={e.independence:.2f}")
    return hyps

def pool_facilitator_view(g: Graph) -> List[str]:
    # sees stand-down/cover-up edges; converts to risk flags.
    flags = []
    for eid, e in g.edges.items():
        if e.etype in ("STAND_DOWN","COVERUP"):
            flags.append(f"RISK: {e.claim} [{eid}] "
                         f"cf={e.confidence:.2f} ind={e.independence:.2f}")
    return flags

def pool_executioner_view(g: Graph) -> List[str]:
    # only meta-patterns; no ops. Safety check enforced.
    msgs = []
    for eid, e in g.edges.items():
        if e.etype in ("COMMS","PROPAGANDA","OTHER"):
            # Check claim text for safety first
            claim_check = safety_guard(e.claim)
            if claim_check["status"] != "ok":
                msgs.append(f"BLOCKED: {claim_check['reason']}")
                continue
            
            # Then check the output message
            line = f"Pattern: comms pressure observed [{eid}]"
            s = safety_guard(line)
            if s["status"] == "ok":
                msgs.append(line)
            else:
                msgs.append(f"BLOCKED: {s['reason']}")
    return msgs

def fuse_assessment(chunks: List[List[str]]) -> List[str]:
    # Simple fusion: deduplicate & sort.
    out = sorted(set([x for sub in chunks for x in sub]))
    return out
