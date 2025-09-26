from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class GraphEngine:
    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold
        self.adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

    def build(
        self,
        pairs: List[Tuple[str, str, float]],
        cases_index: Optional[Dict[str, dict]] = None,
        year_window: Optional[int] = None,
        geo_window: Optional[int] = None,
    ) -> None:
        self.adj.clear()
        for a, b, w in pairs:
            if cases_index is not None:
                ra = cases_index.get(str(a), {})
                rb = cases_index.get(str(b), {})
                if year_window is not None:
                    try:
                        ya = int(ra.get("Year", 0))
                        yb = int(rb.get("Year", 0))
                        if abs(ya - yb) > year_window:
                            continue
                    except Exception:
                        pass
                if geo_window is not None:
                    ca = ra.get("CNTYFIPS")
                    cb = rb.get("CNTYFIPS")
                    ok = False
                    try:
                        if ca is not None and cb is not None:
                            if abs(int(ca) - int(cb)) <= int(geo_window):
                                ok = True
                    except Exception:
                        ok = False
                    if not ok:
                        msa_ok = (ra.get("MSA") and rb.get("MSA") and ra.get("MSA") == rb.get("MSA"))
                        state_ok = (ra.get("State") and rb.get("State") and ra.get("State") == rb.get("State"))
                        if not (msa_ok or state_ok):
                            continue
            self.adj[a].append((b, w))
            self.adj[b].append((a, w))

    def cluster(self) -> List[Dict[str, object]]:
        visited = set()
        clusters: List[Dict[str, object]] = []
        for node in self.adj.keys():
            if node in visited:
                continue
            stack = [node]
            comp = []
            visited.add(node)
            while stack:
                u = stack.pop()
                comp.append(u)
                for v, _ in self.adj.get(u, []):
                    if v not in visited:
                        visited.add(v)
                        stack.append(v)
            clusters.append({"nodes": comp, "size": len(comp)})
        clusters.sort(key=lambda c: c["size"], reverse=True)
        return clusters

    def edges_for_nodes(self, nodes: List[str]) -> List[Tuple[str, str, float]]:
        include = set(nodes)
        edges: List[Tuple[str, str, float]] = []
        seen = set()
        for a in nodes:
            for b, w in self.adj.get(a, []):
                if b in include:
                    key = tuple(sorted((a, b)))
                    if key in seen:
                        continue
                    seen.add(key)
                    edges.append((a, b, w))
        return edges


