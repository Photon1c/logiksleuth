# Claim-audit report: pros/cons, falsifiers, and audit trail.

from typing import Dict, List
from models import Graph, Edge, Evidence

def generate_claim_audit(g: Graph) -> Dict[str, object]:
    """
    Generate a claim-audit report for each edge:
    - Pros (supporting evidence)
    - Cons (contradicting evidence)
    - Falsifiers (what would disprove the claim)
    - Confidence/independence assessment
    """
    audits = []
    
    for edge_id, edge in g.edges.items():
        # Find supporting and contradicting evidence
        supporting = []
        contradicting = []
        
        for ev_id in edge.sources:
            if ev_id in g.evidence:
                ev = g.evidence[ev_id]
                if edge_id in ev.supports:
                    supporting.append((ev_id, ev))
                elif edge_id in ev.contradicts:
                    contradicting.append((ev_id, ev))
                else:
                    # Default: if it's in sources, it supports
                    supporting.append((ev_id, ev))
        
        # Check all evidence for contradictions not in edge.sources
        for ev_id, ev in g.evidence.items():
            if ev_id not in edge.sources and edge_id in ev.contradicts:
                contradicting.append((ev_id, ev))
        
        # Generate falsifiers (what would disprove this claim)
        falsifiers = generate_falsifiers(edge)
        
        # Quality assessment
        quality = assess_claim_quality(edge, len(supporting), len(contradicting))
        
        audit = {
            'edge_id': edge_id,
            'claim': edge.claim,
            'edge_type': edge.etype,
            'src': edge.src,
            'dst': edge.dst,
            'confidence': edge.confidence,
            'independence': edge.independence,
            'supporting_count': len(supporting),
            'contradicting_count': len(contradicting),
            'supporting_evidence': [
                {'id': ev_id, 'type': ev.stype, 'summary': ev.summary}
                for ev_id, ev in supporting
            ],
            'contradicting_evidence': [
                {'id': ev_id, 'type': ev.stype, 'summary': ev.summary}
                for ev_id, ev in contradicting
            ],
            'falsifiers': falsifiers,
            'quality_flags': quality
        }
        audits.append(audit)
    
    return {
        'total_claims': len(audits),
        'audits': audits
    }

def generate_falsifiers(edge: Edge) -> List[str]:
    """
    Generate potential falsifiers for a claim based on edge type.
    These are conditions that would disprove the claim.
    """
    falsifiers = []
    
    if edge.etype == "FUNDING":
        falsifiers = [
            "Definitive financial records showing no transfers",
            "Audited accounts proving separation",
            "Third-party forensic analysis showing no connection"
        ]
    elif edge.etype == "COMMS":
        falsifiers = [
            "Complete communication logs showing no contact",
            "Geolocation data proving physical separation",
            "Network analysis showing no common intermediaries"
        ]
    elif edge.etype == "TASKING":
        falsifiers = [
            "Documentary evidence of independent action",
            "Witness testimony contradicting direction",
            "Timeline analysis showing no opportunity for tasking"
        ]
    elif edge.etype == "STAND_DOWN":
        falsifiers = [
            "Duty logs showing normal operations",
            "Multiple independent witnesses confirming standard posture",
            "Communication records showing no abnormal orders"
        ]
    elif edge.etype == "COVERUP":
        falsifiers = [
            "Complete transparency in all communications",
            "Independent investigation with full access",
            "Contemporaneous records matching public statements"
        ]
    else:
        falsifiers = [
            "Direct contradictory evidence",
            "Alternative explanation with stronger support",
            "Timeline inconsistency"
        ]
    
    return falsifiers

def assess_claim_quality(edge: Edge, support_count: int, contradict_count: int) -> List[str]:
    """
    Assess the quality of a claim based on confidence, independence, and evidence.
    Returns a list of quality flags/warnings.
    """
    flags = []
    
    # Check confidence
    if edge.confidence < 0.3:
        flags.append("LOW_CONFIDENCE: Claim has very low confidence score")
    elif edge.confidence > 0.8:
        flags.append("HIGH_CONFIDENCE: Strong claim")
    
    # Check independence
    if edge.independence < 0.3:
        flags.append("ECHO_RISK: Low source independence, potential echo chamber")
    elif edge.independence > 0.8:
        flags.append("INDEPENDENT_SOURCES: Highly independent sources")
    
    # Check evidence balance
    if support_count == 0:
        flags.append("NO_SUPPORT: No supporting evidence listed")
    if contradict_count > support_count:
        flags.append("CONTRADICTED: More contradicting than supporting evidence")
    
    # Check source count
    if len(edge.sources) < 2:
        flags.append("SINGLE_SOURCE: Relies on only one source")
    elif len(edge.sources) >= 3:
        flags.append("MULTI_SOURCE: Multiple sources support claim")
    
    return flags

def print_audit_report(audit_report: Dict):
    """Pretty-print the audit report."""
    print(f"\n{'='*80}")
    print(f"CLAIM AUDIT REPORT")
    print(f"{'='*80}")
    print(f"Total claims analyzed: {audit_report['total_claims']}\n")
    
    for audit in audit_report['audits']:
        print(f"\n{'-'*80}")
        print(f"Claim [{audit['edge_id']}]: {audit['claim']}")
        print(f"  Type: {audit['edge_type']} | {audit['src']} -> {audit['dst']}")
        print(f"  Confidence: {audit['confidence']:.2f} | Independence: {audit['independence']:.2f}")
        
        print(f"\n  PROS ({audit['supporting_count']}):")
        if audit['supporting_evidence']:
            for ev in audit['supporting_evidence']:
                print(f"    + [{ev['id']}] {ev['type']}: {ev['summary']}")
        else:
            print("    (none)")
        
        print(f"\n  CONS ({audit['contradicting_count']}):")
        if audit['contradicting_evidence']:
            for ev in audit['contradicting_evidence']:
                print(f"    - [{ev['id']}] {ev['type']}: {ev['summary']}")
        else:
            print("    (none)")
        
        print(f"\n  FALSIFIERS (what would disprove this):")
        for i, falsifier in enumerate(audit['falsifiers'], 1):
            print(f"    {i}. {falsifier}")
        
        if audit['quality_flags']:
            print(f"\n  QUALITY FLAGS:")
            for flag in audit['quality_flags']:
                print(f"    ! {flag}")
    
    print(f"\n{'='*80}\n")

