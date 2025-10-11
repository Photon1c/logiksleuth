# CSV import/export for actors, edges, and evidence.

import csv
from typing import List
from models import Graph, Actor, Edge, Evidence

# ===== EXPORT =====

def export_actors_csv(actors: List[Actor], filename: str):
    """Export actors to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'role', 'notes'])
        for a in actors:
            writer.writerow([a.id, a.role, a.notes])

def export_edges_csv(edges: List[tuple], filename: str):
    """Export edges to CSV. edges = [(edge_id, Edge), ...]"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['edge_id', 'src', 'dst', 'etype', 'claim', 
                        'confidence', 'independence', 'sources'])
        for edge_id, e in edges:
            sources_str = ';'.join(e.sources)
            writer.writerow([edge_id, e.src, e.dst, e.etype, e.claim,
                           e.confidence, e.independence, sources_str])

def export_evidence_csv(evidence: List[Evidence], filename: str):
    """Export evidence to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'stype', 'summary', 'url_or_ref', 
                        'integrity_score', 'contradicts', 'supports'])
        for ev in evidence:
            contradicts_str = ';'.join(ev.contradicts)
            supports_str = ';'.join(ev.supports)
            writer.writerow([ev.id, ev.stype, ev.summary, ev.url_or_ref,
                           ev.integrity_score, contradicts_str, supports_str])

def export_graph_csv(g: Graph, prefix: str = "export"):
    """Export entire graph to 3 CSV files."""
    export_actors_csv(list(g.actors.values()), f"{prefix}_actors.csv")
    export_edges_csv(list(g.edges.items()), f"{prefix}_edges.csv")
    export_evidence_csv(list(g.evidence.values()), f"{prefix}_evidence.csv")
    print(f"Exported: {prefix}_{{actors,edges,evidence}}.csv")

# ===== IMPORT =====

def import_actors_csv(filename: str) -> List[Actor]:
    """Import actors from CSV."""
    actors = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            actors.append(Actor(
                id=row['id'],
                role=row['role'],
                notes=row['notes']
            ))
    return actors

def import_edges_csv(filename: str) -> List[tuple]:
    """Import edges from CSV. Returns [(edge_id, Edge), ...]"""
    edges = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources = row['sources'].split(';') if row['sources'] else []
            edge = Edge(
                src=row['src'],
                dst=row['dst'],
                etype=row['etype'],
                claim=row['claim'],
                confidence=float(row['confidence']),
                independence=float(row['independence']),
                sources=sources
            )
            edges.append((row['edge_id'], edge))
    return edges

def import_evidence_csv(filename: str) -> List[Evidence]:
    """Import evidence from CSV."""
    evidence = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contradicts = row['contradicts'].split(';') if row['contradicts'] else []
            supports = row['supports'].split(';') if row['supports'] else []
            evidence.append(Evidence(
                id=row['id'],
                stype=row['stype'],
                summary=row['summary'],
                url_or_ref=row.get('url_or_ref', ''),
                integrity_score=float(row.get('integrity_score', 0.5)),
                contradicts=contradicts,
                supports=supports
            ))
    return evidence

def import_graph_csv(prefix: str = "export") -> Graph:
    """Import entire graph from 3 CSV files."""
    g = Graph()
    
    # Import actors
    actors = import_actors_csv(f"{prefix}_actors.csv")
    for a in actors:
        g.add_actor(a)
    
    # Import edges
    edges = import_edges_csv(f"{prefix}_edges.csv")
    for edge_id, e in edges:
        g.add_edge(edge_id, e)
    
    # Import evidence
    evidence = import_evidence_csv(f"{prefix}_evidence.csv")
    for ev in evidence:
        g.add_evidence(ev)
    
    print(f"Imported: {len(g.actors)} actors, {len(g.edges)} edges, {len(g.evidence)} evidence")
    return g


