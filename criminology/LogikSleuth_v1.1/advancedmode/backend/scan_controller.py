from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
import threading
import time

from .data_loader import stream_cases
from .features import FeatureEncoder
from .matcher import SimilarityMatcher
from .graph_engine import GraphEngine


@dataclass
class ScanConfig:
    csv_path: str
    duration_hours: float
    similarity_threshold: float
    year_window: int
    geo_window: Optional[int] = None


class ScanController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stop = False
        self._status: Dict[str, object] = {"stage": "Idle"}
        self._results: Dict[str, object] = {}
        self._cases_index: Dict[str, dict] = {}

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict[str, object]:
        with self._lock:
            return dict(self._status)

    def results(self, view: str = "summary") -> Dict[str, object]:
        with self._lock:
            return dict(self._results)

    def get_case(self, case_id: str) -> Optional[dict]:
        return self._cases_index.get(case_id)

    def run(self, cfg: ScanConfig) -> None:
        with self._lock:
            self._status = {"stage": "Scanning", "progress": 0}
        self._stop = False
        t_end = time.time() + max(60, cfg.duration_hours * 3600)

        encoder = FeatureEncoder()
        matcher = SimilarityMatcher()
        graph = GraphEngine(threshold=cfg.similarity_threshold)

        total = 0
        for batch in stream_cases(cfg.csv_path, batch_size=2000):
            if time.time() > t_end or self._stop:
                break
            total += len(batch)
            for row in batch:
                cid = row.get("ID") or row.get("Incident") or str(total)
                self._cases_index[str(cid)] = row
            X = encoder.fit_transform_partial(batch)
            matcher.add_block(X, ids=[row.get("ID") or row.get("Incident") or str(i) for i, row in enumerate(batch)])
            # Progress update (approximate)
            with self._lock:
                self._status = {"stage": "Scanning", "progress": total}

        # Compute similarities in blocks
        with self._lock:
            self._status = {"stage": "Matches"}
        pairs = matcher.find_matches(threshold=cfg.similarity_threshold)

        # Build graph and clusters
        with self._lock:
            self._status = {"stage": "Links"}
        graph.build(pairs, cases_index=self._cases_index, year_window=cfg.year_window, geo_window=cfg.geo_window)
        with self._lock:
            self._status = {"stage": "Clusters"}
        clusters = graph.cluster()
        # Extract top cluster edges for visualization
        top = clusters[:1]
        edges: List[Tuple[str, str, float]] = []
        if top:
            edges = graph.edges_for_nodes(top[0]["nodes"])[: min(500, len(top[0]["nodes"]) * 8)]

        with self._lock:
            self._status = {"stage": "Report"}
            labels, matrix = matcher.sample_matrix(limit=48)
            self._results = {
                "counts": {"cases": total, "matches": len(pairs), "clusters": len(clusters)},
                "top_clusters": clusters[:10],
                "threshold": cfg.similarity_threshold,
                "year_window": cfg.year_window,
                "geo_window": cfg.geo_window,
                "edges": edges,
                "labels": labels,
                "matrix": matrix,
            }
            self._status = {"stage": "Idle"}


