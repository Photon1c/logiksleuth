# Extended scenario example demonstrating all add-ons.
# Run this to see CSV I/O, audit reports, independence checking, and optional Dash UI.

from models import Graph, Actor, Edge, Evidence
from engine import run_analysis
from csv_io import export_graph_csv, import_graph_csv
from audit import generate_claim_audit, print_audit_report
from independence import check_source_independence, print_independence_report
import os

def build_demo_graph() -> Graph:
    """Build the demo graph with proper evidence support/contradict relationships."""
    g = Graph()
    
    # Actors (synthetic ids)
    g.add_actor(Actor(id="A_inst", role="INSTIGATOR", notes="Unknown sponsor"))
    g.add_actor(Actor(id="A_fac1", role="AGENCY", notes="Security org Alpha"))
    g.add_actor(Actor(id="A_exec", role="EXECUTIONER", notes="Lone actor (caught)"))
    g.add_actor(Actor(id="A_vic", role="VICTIM", notes="Public figure"))

    # Evidence (abstract) - define BEFORE edges so we can reference them
    g.add_evidence(Evidence(
        id="EV1", 
        stype="FINREC",
        summary="Unusual pre-event transfers",
        supports=["E1"]  # Supports funding claim
    ))
    g.add_evidence(Evidence(
        id="EV2", 
        stype="COMMS",
        summary="Metadata-only contact chain",
        supports=["E2"]  # Supports comms claim
    ))
    g.add_evidence(Evidence(
        id="EV3",
        stype="FINREC", 
        summary="Additional financial anomalies",
        supports=["E1"]  # Also supports funding
    ))
    g.add_evidence(Evidence(
        id="EV4", 
        stype="DOC",
        summary="Duty roster change",
        supports=["E3"]  # Supports stand-down
    ))
    g.add_evidence(Evidence(
        id="EV5", 
        stype="MEDIA",
        summary="On-scene timeline discrepancies",
        supports=["E3"]  # Also supports stand-down
    ))
    g.add_evidence(Evidence(
        id="EV6", 
        stype="MEDIA",
        summary="Briefing inconsistencies",
        supports=["E4"]  # Supports coverup
    ))
    g.add_evidence(Evidence(
        id="EV7",
        stype="DOC",
        summary="Complete operational logs show normal procedures",
        contradicts=["E3"]  # Contradicts stand-down claim
    ))

    # Edges (claims must be high-level; confidence/independence are analyst-set)
    g.add_edge("E1", Edge(
        src="A_inst", 
        dst="A_fac1", 
        etype="FUNDING",
        claim="Indirect funding flows toward Alpha pre-event",
        confidence=0.6, 
        independence=0.5,
        sources=["EV1", "EV3"]
    ))
    g.add_edge("E2", Edge(
        src="A_fac1", 
        dst="A_exec", 
        etype="COMMS",
        claim="Ambiguous contact via intermediary",
        confidence=0.4, 
        independence=0.6,
        sources=["EV2"]
    ))
    g.add_edge("E3", Edge(
        src="A_fac1", 
        dst="A_fac1", 
        etype="STAND_DOWN",
        claim="Operational posture downgraded on event day",
        confidence=0.7, 
        independence=0.7,
        sources=["EV4", "EV5"]
    ))
    g.add_edge("E4", Edge(
        src="A_fac1", 
        dst="A_inst", 
        etype="COVERUP",
        claim="Post-event narrative management",
        confidence=0.5, 
        independence=0.6,
        sources=["EV6"]
    ))

    return g

def demo_csv_io(g: Graph):
    """Demonstrate CSV export and import."""
    print("\n" + "="*80)
    print("1. CSV I/O DEMONSTRATION")
    print("="*80)
    
    # Export
    print("\n>> Exporting graph to CSV files...")
    export_graph_csv(g, prefix="demo_export")
    
    # Import
    print("\n>> Re-importing graph from CSV files...")
    g_imported = import_graph_csv(prefix="demo_export")
    
    print(f"[OK] Import successful!")
    print(f"  Actors: {len(g_imported.actors)}")
    print(f"  Edges: {len(g_imported.edges)}")
    print(f"  Evidence: {len(g_imported.evidence)}")
    
    return g_imported

def demo_audit_report(g: Graph):
    """Demonstrate claim-audit report."""
    print("\n" + "="*80)
    print("2. CLAIM-AUDIT REPORT")
    print("="*80)
    
    audit_report = generate_claim_audit(g)
    print_audit_report(audit_report)

def demo_independence_check(g: Graph):
    """Demonstrate independence checking."""
    print("\n" + "="*80)
    print("3. INDEPENDENCE CHECKER")
    print("="*80)
    
    independence_report = check_source_independence(g)
    print_independence_report(independence_report)

def demo_basic_analysis(g: Graph):
    """Run basic analysis from original example."""
    print("\n" + "="*80)
    print("4. BASIC ANALYSIS (Original)")
    print("="*80 + "\n")
    
    report = run_analysis(g)
    print("Actors:", [a.id+":"+a.role for a in report["actors"]])
    print("Edges:", report["edge_count"], "Evidence:", report["evidence_count"])
    print("Avg confidence:", report["avg_confidence"],
          "Avg independence:", report["avg_independence"])
    print("\nFindings:")
    for line in report["findings"]:
        print("-", line)
    
    return report

def demo_dash_ui(g: Graph, report: dict):
    """Launch Dash UI (optional)."""
    print("\n" + "="*80)
    print("5. DASH UI (Optional)")
    print("="*80)
    
    try:
        from dash_ui import launch_ui, DASH_AVAILABLE
        
        if DASH_AVAILABLE:
            print("\n[UI] Dash UI is available!")
            response = input("   Launch UI? (y/n): ").strip().lower()
            if response == 'y':
                launch_ui(g, report, debug=False, port=8050)
        else:
            print("\n[WARN] Dash not installed.")
            print("   Install with: pip install dash plotly networkx")
    except Exception as e:
        print(f"\n[ERROR] Could not launch UI: {e}")

def cleanup_demo_files():
    """Clean up exported CSV files."""
    files = ["demo_export_actors.csv", "demo_export_edges.csv", "demo_export_evidence.csv"]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"  Cleaned up: {f}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("COLUMBO: Extended Scenario Demonstration")
    print("="*80)
    print("\nThis demo showcases all add-ons:")
    print("  1. CSV I/O for actors/edges/evidence")
    print("  2. Claim-audit report (pros/cons/falsifiers)")
    print("  3. Independence checker (source graph)")
    print("  4. Basic analysis output")
    print("  5. Minimal Dash UI (optional)")
    
    # Build demo graph
    g = build_demo_graph()
    
    # Run all demos
    g_imported = demo_csv_io(g)
    demo_audit_report(g_imported)
    demo_independence_check(g_imported)
    report = demo_basic_analysis(g_imported)
    
    # Optional: Launch UI
    demo_dash_ui(g_imported, report)
    
    # Cleanup
    print("\n" + "="*80)
    print("CLEANUP")
    print("="*80)
    cleanup_demo_files()
    
    print("\n[OK] Demo complete!")
    print("\n[TIP] Run 'python test_safety.py' to verify safety guard tests")

