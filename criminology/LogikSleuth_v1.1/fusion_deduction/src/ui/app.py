from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

import pygame as pg

from ..game_state import GameState, Triplet
from .. import rules
from ..logic.question_bank import build_predicates
from .widgets import Button, Grid
from .palette import BRIGHT
from .assets import load_fonts


def run_app(gs: GameState) -> None:
    pg.init()
    screen = pg.display.set_mode((gs.settings["screen"]["w"], gs.settings["screen"]["h"]))
    pg.display.set_caption("Fusion Deduction")
    clock = pg.time.Clock()
    fonts = load_fonts()

    grid = Grid((40, 120), 40, gs.settings["board"]["size"])
    ai_preds = build_predicates(gs)  # changed: load AI predicates

    status_msg: str = "Welcome"
    show_instructions: bool = False
    show_cheat: bool = False
    auto_mode: bool = False
    action_cooldown_ms: int = 250
    next_action_time: int = 0
    game_over_since: Optional[int] = None

    def on_probe():
        nonlocal status_msg
        cell = grid.hover_cell
        if cell is None:
            status_msg = "Pick a cell"
            return
        print(f"[UI] Player action: Probe {cell}")
        hit, msg = rules.handle_probe(gs, cell)
        status_msg = msg
        if not gs.winner:
            rules.end_turn(gs)

    def on_ask():
        nonlocal status_msg
        # minimal demo predicate: is suspect name alphabetically before 'M'
        pred = ai_preds[0] if ai_preds else (lambda t: True)  # changed: use first question
        print("[UI] Player action: Ask question")
        ans, msg = rules.handle_question(gs, pred)
        status_msg = f"Q: {'Yes' if ans else 'No'}"
        if not gs.winner:
            rules.end_turn(gs)

    def on_accuse():
        nonlocal status_msg
        # naive accuse: top remaining
        s = gs.player_knowledge.remaining_suspects[0]
        i = gs.player_knowledge.remaining_items[0]
        l = gs.player_knowledge.remaining_locations[0]
        print(f"[UI] Player action: Accuse ({s}, {i}, {l})")
        win, msg = rules.handle_accuse(gs, s, i, l)
        status_msg = msg
        if not gs.winner:
            rules.end_turn(gs)

    def on_toggle_auto():
        nonlocal auto_mode, status_msg
        auto_mode = not auto_mode
        auto_btn.label = f"Auto: {'On' if auto_mode else 'Off'}"
        status_msg = f"Auto {'enabled' if auto_mode else 'disabled'}"
        print(f"[UI] Auto mode -> {auto_mode}")

    buttons = [
        Button(pg.Rect(40, 40, 160, 48), "Probe Grid", on_probe),
        Button(pg.Rect(210, 40, 160, 48), "Ask Question", on_ask),
        Button(pg.Rect(380, 40, 160, 48), "Accuse", on_accuse),
    ]
    auto_btn = Button(pg.Rect(550, 40, 160, 48), "Auto: Off", on_toggle_auto)
    buttons.append(auto_btn)
    # Optional Manhunt indicator button (no-op toggle placeholder)
    if bool(gs.settings.get("manhunt", {}).get("enabled", False)):
        def _noop():
            print("[UI] Manhunt mode is enabled via settings; using external data file")
        buttons.append(Button(pg.Rect(720, 40, 200, 48), "Manhunt: On (settings)", _noop))

    def auto_player_turn():
        # Smarter policy:
        # 1) Ask the question that splits player's posterior closest to 50/50
        # 2) Probe adjacent to any known hits (hunt mode), else random unprobed
        # 3) Accuse when top posterior exceeds threshold; else continue probing

        # Respect lock: skip action if player is locked
        if gs.turn.locks.get("player", 0) > 0:
            print("[Auto] Player: locked; skipping action")
            return "locked"

        def pick_question_for_player():
            if not ai_preds:
                return None
            post = gs.player_knowledge.posterior
            best_pred = None
            best_score = 1.0
            for p in ai_preds:
                yes = 0.0
                for (s, i, l), prob in post.items():
                    if p(Triplet(s, i, l)):
                        yes += prob
                split = abs(0.5 - yes)
                if split < best_score:
                    best_score = split
                    best_pred = p
            return best_pred

        def pick_probe_for_player():
            # Hunt around hits first
            hits = [cell for cell, val in gs.ai_board.probes.items() if val]
            unprobed = set(gs.ai_board.unprobed_cells())
            neighbors = []
            for (x, y) in hits:
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x + dx, y + dy
                    cand = (nx, ny)
                    if 0 <= nx < gs.ai_board.size and 0 <= ny < gs.ai_board.size and cand in unprobed:
                        neighbors.append(cand)
            if neighbors:
                return gs.rng.choice(neighbors)
            # else fallback to random unprobed
            rem = gs.ai_board.unprobed_cells()
            return gs.rng.choice(rem) if rem else None

        pk = gs.player_knowledge
        # Early accuse if sufficiently confident
        top_hyp, top_prob = max(pk.posterior.items(), key=lambda kv: kv[1])
        accuse_threshold = float(gs.settings.get("ai", {}).get("accuse_threshold", 0.85))
        if top_prob >= accuse_threshold:
            s, i, l = top_hyp
            print(f"[Auto] Player: accuse {(s, i, l)} p={top_prob:.2f}")
            won, _ = rules.handle_accuse(gs, s, i, l)
            return "accuse-win" if won else "accuse-fail"
        if pk.questions_left > 0:
            pred = pick_question_for_player()
            if pred is not None:
                print("[Auto] Player: ask best-split question")
                rules.handle_question(gs, pred)
                return "ask"
        cell = pick_probe_for_player()
        if cell is not None:
            grid.hover_cell = cell
            print(f"[Auto] Player: probe {cell}")
            rules.handle_probe(gs, cell)
            return "probe"
        # If no probes remain, auto-conclude instead of looping accusations
        no_player_probes = len(gs.ai_board.unprobed_cells()) == 0
        no_ai_probes = len(gs.player_board.unprobed_cells()) == 0
        if no_player_probes and no_ai_probes:
            true_key = (gs.true_triplet.suspect, gs.true_triplet.item, gs.true_triplet.location)
            p_top_key, p_top_prob = max(gs.player_knowledge.posterior.items(), key=lambda kv: kv[1])
            a_top_key, a_top_prob = max(gs.ai_knowledge.posterior.items(), key=lambda kv: kv[1])
            if p_top_key == true_key and a_top_key != true_key:
                gs.winner = "player"
            elif a_top_key == true_key and p_top_key != true_key:
                gs.winner = "ai"
            elif a_top_key == true_key and p_top_key == true_key:
                gs.winner = "player" if p_top_prob >= a_top_prob else "ai"
            else:
                p_true = gs.player_knowledge.posterior.get(true_key, 0.0)
                a_true = gs.ai_knowledge.posterior.get(true_key, 0.0)
                gs.winner = "player" if p_true >= a_true else "ai"
            print(f"[Auto] Concluded winner: {gs.winner}")
            return "conclude"
        # Fallback accuse if nothing else to do
        s, i, l = top_hyp
        print(f"[Auto] Player: accuse {(s, i, l)} p={top_prob:.2f}")
        won, _ = rules.handle_accuse(gs, s, i, l)
        return "accuse-win" if won else "accuse-fail"

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            for b in buttons:
                b.handle(event)
            if event.type == pg.MOUSEMOTION:
                c = grid.cell_at(event.pos)
                if c is not None:
                    grid.hover_cell = c
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_i:
                    show_instructions = not show_instructions
                    print(f"[UI] Instructions {'shown' if show_instructions else 'hidden'}")
                if event.key == pg.K_h:
                    show_cheat = not show_cheat
                    print(f"[UI] Cheat view {'shown' if show_cheat else 'hidden'}")
                if event.key == pg.K_ESCAPE:
                    running = False

        now = pg.time.get_ticks()
        if gs.winner and game_over_since is None:
            game_over_since = now
            status_msg = f"Game Over: {gs.winner} wins"

        # AI and Auto actions throttled to avoid flicker
        if not gs.winner and now >= next_action_time:
            if gs.turn.current == "ai":
                from ..ai_agent import take_turn
                act = take_turn(gs, ai_preds)
                gs.turn.last_ai_action = act
                rules.end_turn(gs)
                next_action_time = now + action_cooldown_ms
            elif gs.turn.current == "player" and auto_mode:
                act = auto_player_turn()
                gs.turn.last_ai_action = f"player-{act}"
                if not gs.winner:
                    rules.end_turn(gs)
                next_action_time = now + action_cooldown_ms

        # Auto-conclude if out of moves in auto mode
        if auto_mode and not gs.winner:
            no_player_probes = len(gs.ai_board.unprobed_cells()) == 0
            no_ai_probes = len(gs.player_board.unprobed_cells()) == 0
            # If both boards are fully probed, conclude regardless of remaining questions
            if no_player_probes and no_ai_probes:
                # Decide winner by correct top guess or higher probability on truth
                true_key = (gs.true_triplet.suspect, gs.true_triplet.item, gs.true_triplet.location)
                # Player
                p_top_key, p_top_prob = max(gs.player_knowledge.posterior.items(), key=lambda kv: kv[1])
                # AI
                a_top_key, a_top_prob = max(gs.ai_knowledge.posterior.items(), key=lambda kv: kv[1])
                if p_top_key == true_key and a_top_key != true_key:
                    gs.winner = "player"
                elif a_top_key == true_key and p_top_key != true_key:
                    gs.winner = "ai"
                elif a_top_key == true_key and p_top_key == true_key:
                    # Both guessed correctly; tie-break by who had higher confidence
                    gs.winner = "player" if p_top_prob >= a_top_prob else "ai"
                else:
                    # Neither guessed correctly; choose who assigned higher prob to the truth
                    p_true = gs.player_knowledge.posterior.get(true_key, 0.0)
                    a_true = gs.ai_knowledge.posterior.get(true_key, 0.0)
                    gs.winner = "player" if p_true >= a_true else "ai"
                status_msg = f"Auto concluded: {gs.winner} wins"
                game_over_since = pg.time.get_ticks()

        screen.fill(BRIGHT["bg"])
        # Panels
        pg.draw.rect(screen, BRIGHT["panel"], pg.Rect(20, 20, 720, 70), border_radius=8)
        for b in buttons:
            b.draw(screen, fonts["ui"])
        # Bottom HUD (avoid overlap with buttons)
        hud_text = f"Turn: {gs.turn.current} | Q left: {gs.player_knowledge.questions_left} | AI: {gs.turn.last_ai_action} | {status_msg} | I:Help H:Cheat Auto:{'On' if auto_mode else 'Off'} Manhunt:{'On' if bool(gs.settings.get('manhunt',{}).get('enabled', False)) else 'Off'}"
        bar_h = 36
        pg.draw.rect(screen, BRIGHT["panel"], pg.Rect(20, gs.settings["screen"]["h"] - bar_h - 10, gs.settings["screen"]["w"] - 40, bar_h), border_radius=8)
        screen.blit(
            fonts["ui"].render(hud_text, True, BRIGHT["text"]),
            (30, gs.settings["screen"]["h"] - bar_h - 10 + 8),
        )

        # Show player's probes on the AI board
        grid.draw(screen, gs.ai_board)

        # Optional cheat overlay to preview AI evidence cells
        if show_cheat:
            x0, y0 = grid.topleft
            for (cx, cy) in gs.ai_board._evidence_cells:
                rect = pg.Rect(
                    x0 + cx * grid.cell_size + 6,
                    y0 + cy * grid.cell_size + 6,
                    grid.cell_size - 12,
                    grid.cell_size - 12,
                )
                pg.draw.rect(screen, BRIGHT["accent2"], rect, width=2, border_radius=3)

        if show_instructions:
            overlay = pg.Surface((gs.settings["screen"]["w"], gs.settings["screen"]["h"]), pg.SRCALPHA)
            panel_rect = pg.Rect(100, 80, gs.settings["screen"]["w"] - 200, gs.settings["screen"]["h"] - 160)
            pg.draw.rect(overlay, (0, 0, 0, 180), panel_rect, border_radius=12)
            screen.blit(overlay, (0, 0))

            title = "How to Play (press I to close)"
            screen.blit(fonts["large"].render(title, True, (255, 255, 255)), (panel_rect.x + 20, panel_rect.y + 20))
            lines = [
                "Objective: Find the hidden (suspect, item, location) before the AI.",
                "Your turn: choose one action — Probe, Ask, or Accuse.",
                "- Probe Grid: Hover a cell then click to mark AI board (green/red).",
                "- Ask Question: Asks a yes/no question to narrow possibilities.",
                "- Accuse: Accuse when confident; wrong accusations lock your turns.",
                "Turns alternate automatically after your action.",
            ]
            y = panel_rect.y + 70
            for line in lines:
                screen.blit(fonts["ui"].render(line, True, (230, 235, 255)), (panel_rect.x + 20, y))
                y += 28

        # Game over overlay and auto-exit when auto mode is on
        if game_over_since is not None:
            overlay = pg.Surface((gs.settings["screen"]["w"], gs.settings["screen"]["h"]), pg.SRCALPHA)
            pg.draw.rect(overlay, (0, 0, 0, 200), pg.Rect(0, 0, gs.settings["screen"]["w"], gs.settings["screen"]["h"]))
            screen.blit(overlay, (0, 0))
            msg1 = f"Game Over - Winner: {gs.winner}"
            msg2 = "Press ESC to quit; report will be saved on exit"
            screen.blit(fonts["large"].render(msg1, True, (255, 255, 255)), (200, 300))
            screen.blit(fonts["ui"].render(msg2, True, (240, 240, 255)), (200, 340))
            if auto_mode and pg.time.get_ticks() - game_over_since > 2000:
                running = False

        pg.display.flip()
        clock.tick(gs.settings["screen"]["fps"])

    pg.quit()

