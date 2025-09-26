from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Board:
    size: int
    rng: any
    evidence_nodes: int = 3
    probes: Dict[Tuple[int, int], bool] = field(default_factory=dict)
    _evidence_cells: List[Tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        cells = [(x, y) for x in range(self.size) for y in range(self.size)]
        self._evidence_cells = [self.rng.choice(cells) for _ in range(self.evidence_nodes)]

    def probe(self, cell: Tuple[int, int]) -> bool:
        if cell in self.probes:
            return self.probes[cell]
        hit = cell in self._evidence_cells
        self.probes[cell] = hit
        return hit

    def unprobed_cells(self) -> List[Tuple[int, int]]:
        return [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if (x, y) not in self.probes
        ]

    @classmethod
    def from_save(cls, size: int, rng: any, evidence_cells: List[Tuple[int, int]], probes: Dict[Tuple[int, int], bool], evidence_nodes: int = 3) -> "Board":
        b = cls(size=size, rng=rng, evidence_nodes=evidence_nodes)
        b._evidence_cells = list(map(lambda t: (int(t[0]), int(t[1])), evidence_cells))  # changed: restore evidence cells
        b.probes = { (int(x), int(y)): bool(v) for (x, y), v in probes.items() }
        return b

