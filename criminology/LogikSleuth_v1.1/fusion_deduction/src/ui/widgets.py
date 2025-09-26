from __future__ import annotations

from typing import Callable, Optional, Tuple

import pygame as pg

from .palette import BRIGHT


class Button:
    def __init__(self, rect: pg.Rect, label: str, on_click: Callable[[], None]):
        self.rect = rect
        self.label = label
        self.on_click = on_click

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        pg.draw.rect(surf, BRIGHT["accent"], self.rect, border_radius=8)
        text = font.render(self.label, True, (255, 255, 255))
        surf.blit(text, text.get_rect(center=self.rect.center))

    def handle(self, event: pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()


class Grid:
    def __init__(self, topleft: Tuple[int, int], cell_size: int, size: int):
        self.topleft = topleft
        self.cell_size = cell_size
        self.size = size
        self.hover_cell: Optional[Tuple[int, int]] = None

    def cell_at(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        x0, y0 = self.topleft
        x, y = pos
        if x < x0 or y < y0:
            return None
        cx = (x - x0) // self.cell_size
        cy = (y - y0) // self.cell_size
        if 0 <= cx < self.size and 0 <= cy < self.size:
            return int(cx), int(cy)
        return None

    def draw(self, surf: pg.Surface, board):
        x0, y0 = self.topleft
        for i in range(self.size + 1):
            pg.draw.line(
                surf,
                BRIGHT["grid_line"],
                (x0 + i * self.cell_size, y0),
                (x0 + i * self.cell_size, y0 + self.size * self.cell_size),
                1,
            )
            pg.draw.line(
                surf,
                BRIGHT["grid_line"],
                (x0, y0 + i * self.cell_size),
                (x0 + self.size * self.cell_size, y0 + i * self.cell_size),
                1,
            )
        for (cx, cy), val in board.probes.items():
            cx = int(cx)
            cy = int(cy)
            rect = pg.Rect(
                x0 + cx * self.cell_size + 2,
                y0 + cy * self.cell_size + 2,
                self.cell_size - 4,
                self.cell_size - 4,
            )
            color = BRIGHT["grid_hit"] if val else BRIGHT["grid_miss"]
            pg.draw.rect(surf, color, rect, border_radius=4)

