import argparse
import json
from pathlib import Path

try:
    # When executed as a module: python -m fusion_deduction.main
    from .src.ui.app import run_app  # type: ignore
    from .src.game_state import GameState  # type: ignore
except ImportError:
    # When executed directly: python main.py (cwd=fusion_deduction)
    from src.ui.app import run_app
    from src.game_state import GameState


def load_settings(settings_path: str) -> dict:
    settings_file = Path(settings_path)
    if not settings_file.exists():
        raise FileNotFoundError(f"settings.json not found at {settings_file}")
    with settings_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Fusion Deduction")
    parser.add_argument("--dev", action="store_true", help="Enable deterministic dev mode")
    parser.add_argument("--settings", default=str(Path(__file__).parent / "settings.json"), help="Path to settings.json")
    args = parser.parse_args()

    settings = load_settings(args.settings)
    print(f"[Init] Loaded settings from {args.settings}")
    print(f"[Init] Dev mode: {args.dev}")
    gs = GameState.from_settings(settings, dev=args.dev)
    print(
        "[Init] Game initialized: board_size=%d evidence_nodes=%d suspects=%d items=%d locations=%d"
        % (
            gs.settings["board"]["size"],
            gs.settings["board"]["evidence_nodes"],
            len(gs.candidates),
            len(gs.items),
            len(gs.locations),
        )
    )
    try:
        run_app(gs)
    finally:
        # Write post-game report
        out_dir = Path(__file__).resolve().parent / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        # Dated filename and stable latest
        from datetime import datetime
        stamp = datetime.now().strftime("_%m%d%Y")
        dated = out_dir / f"last_game_report{stamp}.json"
        report_path = out_dir / "last_game_report.json"
        # Basic report: settings, outcome, probes summary
        player_hits = sum(1 for v in gs.ai_board.probes.values() if v)
        player_misses = sum(1 for v in gs.ai_board.probes.values() if not v)
        ai_hits = sum(1 for v in gs.player_board.probes.values() if v)
        ai_misses = sum(1 for v in gs.player_board.probes.values() if not v)
        report = {
            "dev": gs.dev,
            "settings": gs.settings,
            "winner": gs.winner,
            "true_triplet": {
                "suspect": gs.true_triplet.suspect,
                "item": gs.true_triplet.item,
                "location": gs.true_triplet.location,
            },
            "turns": gs.turn.turn_count,
            "player": {"hits": player_hits, "misses": player_misses, "probes": list(map(list, gs.ai_board.probes.items()))},
            "ai": {"hits": ai_hits, "misses": ai_misses, "probes": list(map(list, gs.player_board.probes.items()))},
            "timeline": gs.logs,
        }
        with dated.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[Report] Wrote post-game reports to {dated} and {report_path}")


if __name__ == "__main__":
    main()

