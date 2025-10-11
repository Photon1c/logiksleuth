# Synthetic, abstract scenario (no PII, no ops).
# Replace with your own synthetic cases or real cases WITH redactions.

from models import Graph, Actor, Edge, Evidence
from engine import run_analysis

def build_demo_graph() -> Graph:
    g = Graph()
    # Actors (synthetic ids)
    g.add_actor(Actor(id="A_inst", role="INSTIGATOR", notes="Unknown sponsor"))
    g.add_actor(Actor(id="A_fac1", role="AGENCY", notes="Security org Alpha"))
    g.add_actor(Actor(id="A_exec", role="EXECUTIONER", notes="Lone actor (caught)"))
    g.add_actor(Actor(id="A_vic", role="VICTIM", notes="Public figure"))

    # Edges (claims must be high-level; confidence/independence are analyst-set)
    g.add_edge("E1", Edge(src="A_inst", dst="A_fac1", etype="FUNDING",
                          claim="Indirect funding flows toward Alpha pre-event",
                          confidence=0.6, independence=0.5,
                          sources=["EV1","EV3"]))
    g.add_edge("E2", Edge(src="A_fac1", dst="A_exec", etype="COMMS",
                          claim="Ambiguous contact via intermediary",
                          confidence=0.4, independence=0.6,
                          sources=["EV2"]))
    g.add_edge("E3", Edge(src="A_fac1", dst="A_fac1", etype="STAND_DOWN",
                          claim="Operational posture downgraded on event day",
                          confidence=0.7, independence=0.7,
                          sources=["EV4","EV5"]))
    g.add_edge("E4", Edge(src="A_fac1", dst="A_inst", etype="COVERUP",
                          claim="Post-event narrative management",
                          confidence=0.5, independence=0.6,
                          sources=["EV6"]))

    # Evidence (abstract)
    g.add_evidence(Evidence(id="EV1", stype="FINREC",
                            summary="Unusual pre-event transfers"))
    g.add_evidence(Evidence(id="EV2", stype="COMMS",
                            summary="Metadata-only contact chain"))
    g.add_evidence(Evidence(id="EV4", stype="DOC",
                            summary="Duty roster change"))
    g.add_evidence(Evidence(id="EV5", stype="MEDIA",
                            summary="On-scene timeline discrepancies"))
    g.add_evidence(Evidence(id="EV6", stype="MEDIA",
                            summary="Briefing inconsistencies"))

    return g

if __name__ == "__main__":
    g = build_demo_graph()
    report = run_analysis(g)
    print("Actors:", [a.id+":"+a.role for a in report["actors"]])
    print("Edges:", report["edge_count"], "Evidence:", report["evidence_count"])
    print("Avg confidence:", report["avg_confidence"],
          "Avg independence:", report["avg_independence"])
    print("\nFindings:")
    for line in report["findings"]:
        print("-", line)
