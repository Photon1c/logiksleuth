# Minimal Dash UI: left = graph visualization, right = findings panel.

try:
    import dash
    from dash import dcc, html, Input, Output
    import plotly.graph_objects as go
    import networkx as nx
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("[WARN] Dash not installed. Run: pip install dash plotly networkx")

from typing import Dict
from models import Graph

def create_network_figure(g: Graph) -> go.Figure:
    """Create a Plotly network graph from the Graph object."""
    
    # Build NetworkX graph for layout
    G = nx.DiGraph()
    
    # Add nodes
    for actor_id, actor in g.actors.items():
        G.add_node(actor_id, role=actor.role, notes=actor.notes)
    
    # Add edges
    for edge_id, edge in g.edges.items():
        G.add_edge(edge.src, edge.dst, 
                   edge_id=edge_id,
                   etype=edge.etype,
                   claim=edge.claim,
                   confidence=edge.confidence)
    
    # Use spring layout for positioning
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create edge traces
    edge_traces = []
    for edge_id, edge in g.edges.items():
        x0, y0 = pos[edge.src]
        x1, y1 = pos[edge.dst]
        
        # Color by confidence
        conf = edge.confidence
        color = f'rgba({int(255*(1-conf))}, {int(255*conf)}, 100, 0.6)'
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=2 + 3*conf, color=color),
            hoverinfo='text',
            text=f"{edge_id}: {edge.etype}<br>{edge.claim}<br>conf={conf:.2f}",
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    role_colors = {
        'INSTIGATOR': '#ff6b6b',
        'FACILITATOR': '#feca57', 
        'EXECUTIONER': '#ee5a6f',
        'VICTIM': '#48dbfb',
        'AGENCY': '#ff9ff3',
        'WITNESS': '#54a0ff',
        'ORG': '#00d2d3',
        'UNKNOWN': '#cccccc'
    }
    
    for actor_id, actor in g.actors.items():
        x, y = pos[actor_id]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{actor_id}<br>Role: {actor.role}<br>{actor.notes}")
        node_color.append(role_colors.get(actor.role, '#cccccc'))
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[a.id for a in g.actors.values()],
        textposition='top center',
        marker=dict(
            size=25,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        hoverinfo='text',
        hovertext=node_text,
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        title="Investigative Graph",
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='white')
    )
    
    return fig

def create_dash_app(g: Graph, report: Dict) -> dash.Dash:
    """Create and configure the Dash application."""
    
    if not DASH_AVAILABLE:
        raise ImportError("Dash is not installed. Run: pip install dash plotly networkx")
    
    app = dash.Dash(__name__)
    
    # Create network figure
    fig = create_network_figure(g)
    
    # Build findings HTML
    findings_html = []
    findings_html.append(html.H3("Analysis Report", style={'color': '#4ecdc4'}))
    
    findings_html.append(html.Div([
        html.H4("Case Metrics", style={'color': '#ffe66d'}),
        html.P(f"Actors: {len(report['actors'])}"),
        html.P(f"Edges: {report['edge_count']}"),
        html.P(f"Evidence: {report['evidence_count']}"),
        html.P(f"Avg Confidence: {report['avg_confidence']:.3f}"),
        html.P(f"Avg Independence: {report['avg_independence']:.3f}"),
    ], style={'margin-bottom': '20px', 'padding': '10px', 
              'background-color': '#2d2d2d', 'border-radius': '5px'}))
    
    findings_html.append(html.H4("Findings", style={'color': '#ffe66d'}))
    
    for finding in report['findings']:
        # Color code by prefix
        color = '#ffffff'
        if finding.startswith('H:'):
            color = '#4ecdc4'  # Hypothesis - cyan
        elif finding.startswith('RISK:'):
            color = '#ff6b6b'  # Risk - red
        elif finding.startswith('Pattern:'):
            color = '#feca57'  # Pattern - yellow
        elif finding.startswith('BLOCKED:'):
            color = '#ee5a6f'  # Blocked - dark red
        
        findings_html.append(
            html.P(f"• {finding}", style={'color': color, 'margin': '5px 0'})
        )
    
    # Layout
    app.layout = html.Div([
        html.H1("Columbo: Investigative Analysis", 
                style={'textAlign': 'center', 'color': '#4ecdc4', 'margin': '20px'}),
        
        html.Div([
            # Left panel: Graph
            html.Div([
                dcc.Graph(
                    id='network-graph',
                    figure=fig,
                    style={'height': '80vh'}
                )
            ], style={'width': '60%', 'display': 'inline-block', 
                     'vertical-align': 'top', 'padding': '10px'}),
            
            # Right panel: Findings
            html.Div([
                html.Div(findings_html, 
                        style={'padding': '20px', 'background-color': '#2d2d2d',
                               'border-radius': '10px', 'height': '80vh',
                               'overflow-y': 'auto'})
            ], style={'width': '38%', 'display': 'inline-block',
                     'vertical-align': 'top', 'padding': '10px'})
        ], style={'background-color': '#1e1e1e'}),
        
        html.Div([
            html.P("[DISCLAIMER] This is a synthetic analysis tool. No real PII or operational data.",
                  style={'textAlign': 'center', 'color': '#888', 'margin': '20px'})
        ])
        
    ], style={'background-color': '#1e1e1e', 'color': '#ffffff', 
             'font-family': 'Arial, sans-serif'})
    
    return app

def launch_ui(g: Graph, report: Dict, debug: bool = False, port: int = 8050):
    """Launch the Dash UI."""
    if not DASH_AVAILABLE:
        print("[ERROR] Cannot launch UI: Dash not installed")
        print("   Install with: pip install dash plotly networkx")
        return
    
    app = create_dash_app(g, report)
    print(f"\n[LAUNCH] Starting Columbo UI at http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    app.run_server(debug=debug, port=port)

