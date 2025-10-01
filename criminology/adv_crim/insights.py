# insights.py
# Minimal helpers to compute an anomaly score and render an "Analyst Insights" section.

import math
import pandas as pd


def _pick_loc_column(df: pd.DataFrame, group: str) -> str | None:
    if group == 'msa':
        return 'MSA_LABEL' if 'MSA_LABEL' in df.columns else ('MSA_NUM' if 'MSA_NUM' in df.columns else None)
    return 'CNTY_LABEL' if 'CNTY_LABEL' in df.columns else ('CNTY' if 'CNTY' in df.columns else None)


def add_anomaly_score(df: pd.DataFrame) -> pd.DataFrame:
    """Score higher when clearance is low, cluster is large, and reporting gaps are high."""
    d = df.copy()
    if not {'PERCENT','TOTAL'}.issubset(d.columns):
        return d
    gap = d['REPORT_GAP_IDX'] if 'REPORT_GAP_IDX' in d.columns else 0
    if not isinstance(gap, pd.Series):
        gap = pd.Series([gap]*len(d), index=d.index)
    d['anomaly_score'] = (1 - d['PERCENT']).clip(lower=0) * d['TOTAL'].map(math.log1p) * (0.5 + gap.fillna(0)/2)
    return d


def _fmt_row(r: pd.Series, loc_col: str | None) -> str:
    loc = f"{r.get(loc_col)} — " if loc_col and loc_col in r else ""
    pct = f"{r['PERCENT']:.1%}" if pd.notna(r.get('PERCENT')) else "n/a"
    return f"- {loc}{r.get('WEAPON_LABEL','?')}: UNSOLVED {int(r.get('UNSOLVED',0))}/{int(r.get('TOTAL',0))} ({pct})"


def render_markdown(df: pd.DataFrame, group: str, top: int = 3) -> str:
    d = add_anomaly_score(df)
    loc_col = _pick_loc_column(d, group)
    blocks = []

    if 'anomaly_score' in d.columns:
        a = d.sort_values('anomaly_score', ascending=False).head(top)
        blocks.append("### Top by anomaly\n" + "\n".join(_fmt_row(r, loc_col) for _, r in a.iterrows()))

    if 'UNSOLVED' in d.columns:
        u = d.sort_values('UNSOLVED', ascending=False).head(top)
        blocks.append("### Top by unsolved\n" + "\n".join(_fmt_row(r, loc_col) for _, r in u.iterrows()))

    if 'REPORT_GAP_IDX' in d.columns:
        g = d[d['REPORT_GAP_IDX'] >= 0.6].sort_values('REPORT_GAP_IDX', ascending=False).head(top)
        if not g.empty:
            blocks.append("### Data-gap watchlist (REPORT_GAP_IDX ≥ 0.6)\n" +
                          "\n".join(_fmt_row(r, loc_col) for _, r in g.iterrows()))

    return "\n\n".join(b for b in blocks if b)


def render_html(df: pd.DataFrame, group: str, top: int = 3) -> str:
    """Simple HTML bullets; keep it dependency-free."""
    md = render_markdown(df, group, top)
    html = md.replace("### ", "<h3>")
    html = html.replace("\n- ", "<li>")
    html = html.replace("\n\n", "</ul><br/>")
    html = html.replace("\n", "</li>")
    if "<h3>" in html:
        html = html.replace("<h3>", "</ul><h3>")
    return "<div>" + html + "</div>"


