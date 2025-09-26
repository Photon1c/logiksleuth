from __future__ import annotations

import pygame as pg


def load_fonts() -> dict:
    return {
        "ui": pg.font.SysFont("DejaVu Sans", 20),  # changed: more available font
        "large": pg.font.SysFont("DejaVu Sans", 28, bold=True),  # changed: more available font
    }

