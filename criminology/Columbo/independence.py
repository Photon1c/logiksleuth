# Independence checker: detect echo chambers via source graph analysis.

from typing import Dict, List, Set, Tuple
from models import Graph, Edge
from collections import defaultdict

def check_source_independence(g: Graph) -> Dict[str, object]:
    """
    Analyze source independence across claims to detect echo chambers.
    Returns a report with:
    - Source overlap matrix
    - Echo chamber warnings
    - Independence scores adjusted for overlap
    """
    
    # Build source graph: which edges share which evidence
    source_to_edges = defaultdict(set)
    edge_to_sources = {}
    
    for edge_id, edge in g.edges.items():
        edge_to_sources[edge_id] = set(edge.sources)
        for src in edge.sources:
            source_to_edges[src].add(edge_id)
    
    # Calculate pairwise edge overlap
    overlaps = []
    edge_ids = list(g.edges.keys())
    
    for i, e1 in enumerate(edge_ids):
        for e2 in edge_ids[i+1:]:
            sources1 = edge_to_sources.get(e1, set())
            sources2 = edge_to_sources.get(e2, set())
            
            if sources1 and sources2:
                intersection = sources1 & sources2
                union = sources1 | sources2
                
                if intersection:
                    overlap_ratio = len(intersection) / len(union)
                    overlaps.append({
                        'edge1': e1,
                        'edge2': e2,
                        'shared_sources': list(intersection),
                        'overlap_ratio': overlap_ratio,
                        'edge1_sources': list(sources1),
                        'edge2_sources': list(sources2)
                    })
    
    # Detect echo chambers (high overlap clusters)
    echo_warnings = detect_echo_chambers(overlaps, threshold=0.5)
    
    # Calculate adjusted independence scores
    adjusted_scores = calculate_adjusted_independence(g, source_to_edges, edge_to_sources)
    
    # Identify most-used sources (potential bias vectors)
    source_usage = {src: len(edges) for src, edges in source_to_edges.items()}
    overused_sources = [(src, count) for src, count in source_usage.items() if count > 2]
    overused_sources.sort(key=lambda x: x[1], reverse=True)
    
    return {
        'total_sources': len(g.evidence),
        'total_edges': len(g.edges),
        'source_overlap_count': len(overlaps),
        'overlaps': overlaps,
        'echo_warnings': echo_warnings,
        'adjusted_independence': adjusted_scores,
        'overused_sources': overused_sources,
        'source_to_edges': {src: list(edges) for src, edges in source_to_edges.items()}
    }

def detect_echo_chambers(overlaps: List[Dict], threshold: float = 0.5) -> List[str]:
    """
    Detect echo chambers where multiple claims rely heavily on same sources.
    """
    warnings = []
    
    # Group by high overlap
    high_overlap = [o for o in overlaps if o['overlap_ratio'] >= threshold]
    
    if high_overlap:
        warnings.append(
            f"ECHO_CHAMBER: {len(high_overlap)} edge pairs share >{threshold*100:.0f}% of sources"
        )
        
        for o in high_overlap:
            warnings.append(
                f"  - {o['edge1']} ↔ {o['edge2']}: {o['overlap_ratio']*100:.0f}% overlap "
                f"(shared: {', '.join(o['shared_sources'])})"
            )
    
    return warnings

def calculate_adjusted_independence(
    g: Graph,
    source_to_edges: Dict[str, Set[str]],
    edge_to_sources: Dict[str, Set[str]]
) -> Dict[str, float]:
    """
    Calculate adjusted independence scores accounting for source reuse.
    If a source is used by many edges, it's less independent.
    """
    adjusted = {}
    
    for edge_id, edge in g.edges.items():
        original_ind = edge.independence
        
        # Penalty for using heavily-reused sources
        sources = edge_to_sources.get(edge_id, set())
        if sources:
            reuse_penalties = []
            for src in sources:
                reuse_count = len(source_to_edges.get(src, set()))
                # Penalty increases with reuse: 1 use = 0%, 2 = 10%, 3 = 20%, etc.
                penalty = min(0.3, (reuse_count - 1) * 0.1)
                reuse_penalties.append(penalty)
            
            avg_penalty = sum(reuse_penalties) / len(reuse_penalties)
            adjusted_ind = max(0.0, original_ind - avg_penalty)
        else:
            adjusted_ind = original_ind
        
        adjusted[edge_id] = round(adjusted_ind, 3)
    
    return adjusted

def print_independence_report(report: Dict):
    """Pretty-print the independence report."""
    print(f"\n{'='*80}")
    print(f"SOURCE INDEPENDENCE REPORT")
    print(f"{'='*80}")
    print(f"Total sources: {report['total_sources']}")
    print(f"Total claims: {report['total_edges']}")
    print(f"Source overlaps detected: {report['source_overlap_count']}")
    
    if report['overused_sources']:
        print(f"\n[ALERT] OVERUSED SOURCES (used in 3+ claims):")
        for src, count in report['overused_sources']:
            edges = report['source_to_edges'].get(src, [])
            print(f"  [{src}] used {count} times in: {', '.join(edges)}")
    
    if report['echo_warnings']:
        print(f"\n[WARN] ECHO CHAMBER WARNINGS:")
        for warning in report['echo_warnings']:
            print(f"  {warning}")
    
    print(f"\n[SCORES] ADJUSTED INDEPENDENCE SCORES:")
    print(f"  (Adjusted down when sources are reused across multiple claims)")
    for edge_id, adj_ind in report['adjusted_independence'].items():
        orig_ind = None
        # We'd need to pass the graph to get original, but for display:
        print(f"  [{edge_id}] adjusted independence: {adj_ind:.3f}")
    
    if report['source_overlap_count'] > 0:
        print(f"\n[LINKS] SOURCE OVERLAPS:")
        for overlap in report['overlaps']:
            print(f"  {overlap['edge1']} <-> {overlap['edge2']}: "
                  f"{overlap['overlap_ratio']*100:.0f}% overlap")
            print(f"    Shared: {', '.join(overlap['shared_sources'])}")
    
    print(f"\n{'='*80}\n")

