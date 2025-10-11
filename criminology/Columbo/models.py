# Roles, edges, and evidence—abstract & case-agnostic.

from dataclasses import dataclass, field
from typing import List, Dict, Literal, Optional

Role = Literal["INSTIGATOR","FACILITATOR","EXECUTIONER","VICTIM",
               "WITNESS","AGENCY","ORG","UNKNOWN"]
EdgeType = Literal["FUNDING","COMMS","TASKING","STAND_DOWN",
                   "COVERUP","PROPAGANDA","OTHER"]
SourceType = Literal["DOC","MEDIA","TESTIMONY","TELEMETRY","FINREC","OTHER"]

@dataclass
class Actor:
    id: str                      # synthetic id (no PII)
    role: Role = "UNKNOWN"
    notes: str = ""

@dataclass
class Edge:
    src: str
    dst: str
    etype: EdgeType
    claim: str                   # short natural-language statement
    confidence: float            # 0.0–1.0
    independence: float          # 0.0–1.0  (source independence)
    sources: List[str] = field(default_factory=list)

@dataclass
class Evidence:
    id: str
    stype: SourceType
    summary: str
    url_or_ref: str = ""         # docket #, archive link, etc.
    integrity_score: float = 0.5 # hashing / provenance later
    contradicts: List[str] = field(default_factory=list) # Edge ids
    supports: List[str] = field(default_factory=list)    # Edge ids

@dataclass
class Graph:
    actors: Dict[str, Actor] = field(default_factory=dict)
    edges: Dict[str, Edge] = field(default_factory=dict) # key = edge_id
    evidence: Dict[str, Evidence] = field(default_factory=dict)

    def add_actor(self, a: Actor):
        self.actors[a.id] = a

    def add_edge(self, edge_id: str, e: Edge):
        self.edges[edge_id] = e

    def add_evidence(self, ev: Evidence):
        self.evidence[ev.id] = ev
