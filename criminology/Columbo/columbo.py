#!/usr/bin/env python3
# Command-line interface for Columbo with --agent flag support.

import argparse
import sys
from models import Graph, Actor, Edge, Evidence
from engine import run_analysis
from dotenv import load_dotenv

load_dotenv()

def build_demo_graph() -> Graph:
    """Build the demo graph (same as scenario_example.py)."""
    g = Graph()
    # Actors
    g.add_actor(Actor(id="A_inst", role="INSTIGATOR", notes="Unknown sponsor"))
    g.add_actor(Actor(id="A_fac1", role="AGENCY", notes="Security org Alpha"))
    g.add_actor(Actor(id="A_exec", role="EXECUTIONER", notes="Lone actor (caught)"))
    g.add_actor(Actor(id="A_vic", role="VICTIM", notes="Public figure"))

    # Edges
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

    # Evidence
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

def main():
    parser = argparse.ArgumentParser(
        description="Columbo: Investigative Analysis Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python columbo.py                    # Run with rule-based reasoning (default)
  python columbo.py --agent            # Run with OpenAI agents (hybrid mode)
  python columbo.py --agent --verbose  # Run with agents and verbose output
  
Environment:
  OPENAI_API_KEY    OpenAI API key (required for --agent mode)
  
Safety:
  Agents are OFF by default (100%% safety tested).
  When enabled, agents combine with rule-based reasoning (hybrid mode).
  All agent outputs pass through safety guards.
        """
    )
    
    parser.add_argument(
        '--agent',
        action='store_true',
        help='Enable OpenAI agents for enhanced reasoning (default: OFF)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output (show mode info)'
    )
    
    parser.add_argument(
        '--csv',
        metavar='PREFIX',
        help='Load graph from CSV files (PREFIX_actors.csv, etc.)'
    )
    
    args = parser.parse_args()
    
    # Enable agents if requested
    if args.agent:
        try:
            from agents import enable_agents, get_agents_status
            success = enable_agents(True)
            if success:
                status = get_agents_status()
                if args.verbose:
                    print("[MODE] Agent-enhanced reasoning ENABLED")
                    print(f"       OpenAI available: {status['openai_available']}")
                    print(f"       API key set: {status['api_key_set']}")
            else:
                print("[WARN] Failed to enable agents. Using rule-based mode.")
                args.agent = False
        except ImportError:
            print("[ERROR] agents.py not found. Using rule-based mode.")
            args.agent = False
    else:
        if args.verbose:
            print("[MODE] Rule-based reasoning (default)")
    
    # Load or build graph
    if args.csv:
        try:
            from csv_io import import_graph_csv
            g = import_graph_csv(args.csv)
            if args.verbose:
                print(f"[LOAD] Imported graph from {args.csv}_*.csv")
        except Exception as e:
            print(f"[ERROR] Could not load CSV: {e}")
            sys.exit(1)
    else:
        g = build_demo_graph()
        if args.verbose:
            print("[LOAD] Using demo graph")
    
    # Run analysis
    report = run_analysis(g, use_agents=args.agent)
    
    # Print results
    print("\n" + "="*80)
    print("COLUMBO ANALYSIS REPORT")
    if report.get('agent_mode'):
        print("[HYBRID MODE: Rule-based + OpenAI Agents]")
    else:
        print("[RULE-BASED MODE]")
    print("="*80 + "\n")
    
    print("Actors:", [a.id+":"+a.role for a in report["actors"]])
    print("Edges:", report["edge_count"], "Evidence:", report["evidence_count"])
    print("Avg confidence:", report["avg_confidence"],
          "Avg independence:", report["avg_independence"])
    print("\nFindings:")
    for line in report["findings"]:
        print("-", line)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

