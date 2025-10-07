import os, datetime as dt
import pandas as pd
from insights import add_anomaly_score, render_markdown as insights_md, render_html as insights_html
from mapviz import build_map_from_per_ori


def _pick_loc_column(df, group):
    if group == 'msa':
        return 'MSA_LABEL' if 'MSA_LABEL' in df.columns else ('MSA_NUM' if 'MSA_NUM' in df.columns else None)
    else:
        return 'CNTY_LABEL' if 'CNTY_LABEL' in df.columns else ('CNTY' if 'CNTY' in df.columns else None)


def _format_display(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for c in ['PERCENT', 'REL_UNK_RATE', 'CIRC_UNK_RATE', 'REPORT_GAP_IDX']:
        if c in d.columns:
            d[c] = (d[c] * 100).round(1).astype(str) + '%'
    return d

def _style_html_table(df: pd.DataFrame) -> str:
    """Return styled HTML table with color cues; falls back to plain .to_html on error."""
    try:
        d = add_anomaly_score(df.copy())
        sty = d.style

        fmt_map = {}
        for c in ['PERCENT','REL_UNK_RATE','CIRC_UNK_RATE','REPORT_GAP_IDX']:
            if c in d.columns:
                fmt_map[c] = '{:.1%}'
        sty = sty.format(fmt_map)

        if 'UNSOLVED' in d.columns:
            sty = sty.background_gradient(subset=['UNSOLVED'])
        if 'anomaly_score' in d.columns:
            sty = sty.background_gradient(subset=['anomaly_score'])

        if 'PERCENT' in d.columns:
            def band(s):
                out = []
                for v in s:
                    if pd.isna(v):
                        out.append('')
                    elif v <= 0.25:
                        out.append('background-color:#f8d7da')
                    elif v <= 0.33:
                        out.append('background-color:#fff3cd')
                    else:
                        out.append('background-color:#d4edda')
                return out
            sty = sty.apply(band, subset=['PERCENT'])

        # Hide index for cleaner display (try modern then legacy API)
        try:
            sty = sty.hide(axis='index')
        except Exception:
            try:
                sty = sty.hide_index()
            except Exception:
                pass
        return sty.to_html()
    except Exception:
        return df.to_html(index=False)

def _build_dump_commands(df: pd.DataFrame, group: str, run_params: dict, max_rows: int = 3) -> tuple[str, str]:
    """Return (md_text, html_text) with up to top N dump commands (CMD and PowerShell)."""
    if group != 'msa' or 'MSA_LABEL' not in df.columns or 'WEAPON_LABEL' not in df.columns:
        return ("", "")
    rows = df[['MSA_LABEL','WEAPON_LABEL']].head(max_rows)
    if rows.empty:
        return ("", "")
    csv_path = run_params.get('csv', 'data.csv')
    cmd_lines = []
    ps_lines = []
    for _, r in rows.iterrows():
        msa = str(r['MSA_LABEL']).replace('"', '\\"')
        weapon = str(r['WEAPON_LABEL']).replace('"', '\\"')
        cmd = f"python map_cluster.py \"{csv_path}\" --group msa --dump-msa \"{msa}\" --dump-weapon \"{weapon}\" --outdir out"
        ps = cmd  # same quoting works in PowerShell
        cmd_lines.append(cmd)
        ps_lines.append(ps)
    md = "### Case-dump shortcuts (Windows)\n" + "\n".join(f"`{c}`" for c in cmd_lines)
    html = "<h3>Case-dump shortcuts (Windows)</h3>" + "<br/>".join(f"<code>{c}</code>" for c in ps_lines)
    return (md, html)


def write_report(view: pd.DataFrame, group: str, outdir: str, fmt: str='md',
                 filepath: str|None=None, title: str='Report', top: int=10, run_params: dict|None=None,
                 per_ori_csv: str|None=None, include_map: bool=True) -> str:
    os.makedirs(outdir, exist_ok=True)
    if filepath is None:
        filepath = os.path.join(outdir, f"report_{group}.{fmt}")
    if per_ori_csv is None:
        candidate = os.path.join(outdir, 'dump_cases_per_ori.csv')
        per_ori_csv = candidate if os.path.exists(candidate) else None

    loc_col = _pick_loc_column(view, group)
    base_cols = ['MURDGRP', 'SEX', 'WEAPON_LABEL', 'TOTAL', 'SOLVED', 'PERCENT', 'UNSOLVED']
    opt_cols  = ['DECADE', loc_col, 'REL_UNK_RATE', 'REL_TOP1', 'CIRC_UNK_RATE', 'CIRC_TOP1', 'REPORT_GAP_IDX']
    cols = [c for c in (base_cols + opt_cols) if c and c in view.columns]

    # Sort by least solved percentage ascending, tie-break by UNSOLVED descending
    if 'PERCENT' in view.columns:
        sort_cols = ['PERCENT'] + (['UNSOLVED'] if 'UNSOLVED' in view.columns else [])
        sort_asc  = [True] + ([False] if 'UNSOLVED' in view.columns else [])
        sorted_view = view.sort_values(sort_cols, ascending=sort_asc, na_position='last')
    else:
        sorted_view = view

    head = sorted_view[cols].head(top) if len(cols) else sorted_view.head(top)
    disp = _format_display(head)

    ts = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header_lines = [f"# {title}",
                    "",
                    f"**Generated:** {ts}",
                    "**Filters:** " + ", ".join(f"{k}={v}" for k,v in (run_params or {}).items() if v not in [None, False, '']),
                    ""]
    # Clean HTML header for HTML outputs
    header_html = (
        f"<h1>{title}</h1>"
        f"<p><strong>Generated:</strong> {ts}</p>"
        f"<p><strong>Filters:</strong> "
        + ", ".join(f"{k}={v}" for k,v in (run_params or {}).items() if v not in [None, False, ''])
        + "</p>"
    )

    # attempt to build map (optional)
    map_path = None
    if include_map and per_ori_csv:
        map_path = build_map_from_per_ori(per_ori_csv, outdir)

    if fmt == 'md':
        try:
            body = disp.to_markdown(index=False)
        except Exception:
            html_path = filepath[:-2] + "html" if filepath.endswith(".md") else filepath + ".html"
            html_table = _style_html_table(head)
            # Use relative forward-slashed path for iframe
            map_src = None
            if map_path:
                try:
                    map_src = os.path.relpath(map_path, start=os.path.dirname(html_path)).replace("\\", "/")
                except Exception:
                    map_src = map_path.replace("\\", "/")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(header_html + html_table)
                if map_src:
                    f.write(f'<h2>Map</h2><iframe src="{map_src}" width="100%" height="520" frameborder="0"></iframe>')
                else:
                    f.write('<h2>Map</h2><p><em>Map not generated (no folium or no coordinates).</em></p>')
                f.write("<h2>Analyst Insights</h2>")
                f.write(insights_html(head, group, top=min(3, len(head))))
                md_cmds, html_cmds = _build_dump_commands(head, group, run_params or {}, max_rows=3)
                f.write(html_cmds)
            return html_path
        md_text = "\n".join(header_lines) + "\n" + body + "\n\n## Analyst Insights\n"
        md_text += insights_md(head, group, top=min(3, len(head))) or "_No insights available for the current slice._"
        md_cmds, html_cmds = _build_dump_commands(head, group, run_params or {}, max_rows=3)
        if md_cmds:
            md_text += "\n\n" + md_cmds + "\n"
        if map_path:
            try:
                map_rel_md = os.path.relpath(map_path, start=os.path.dirname(filepath)).replace("\\", "/")
            except Exception:
                map_rel_md = map_path.replace("\\", "/")
            md_text += f"\n\n## Map\nInteractive per-ORI map: **[{os.path.basename(map_rel_md)}]({map_rel_md})**"
        else:
            md_text += "\n\n## Map\n_Map not generated (no folium or no coordinates)._"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_text)
        # also write styled HTML alongside .md
        try:
            html_mirror = os.path.splitext(filepath)[0] + ".html"
            html_table = _style_html_table(head)
            # relative forward-slashed map src
            map_src = None
            if map_path:
                try:
                    map_src = os.path.relpath(map_path, start=os.path.dirname(html_mirror)).replace("\\", "/")
                except Exception:
                    map_src = map_path.replace("\\", "/")
            html_full = header_html + html_table
            if html_cmds:
                html_full += html_cmds
            if map_src:
                html_full += f'<h2>Map</h2><iframe src="{map_src}" width="100%" height="520" frameborder="0"></iframe>'
            else:
                html_full += "<h2>Map</h2><p><em>Map not generated (no folium or no coordinates).</em></p>"
            html_full += "<h2>Analyst Insights</h2>" + insights_html(head, group, top=min(3, len(head)))
            with open(html_mirror, 'w', encoding='utf-8') as h:
                h.write(html_full)
        except Exception:
            pass
        return filepath

    elif fmt == 'html':
        html_table = _style_html_table(head)
        # relative forward-slashed map src
        map_src = None
        if map_path:
            try:
                map_src = os.path.relpath(map_path, start=os.path.dirname(filepath)).replace("\\", "/")
            except Exception:
                map_src = map_path.replace("\\", "/")
        html = header_html + html_table
        if map_src:
            html += f'<h2>Map</h2><iframe src="{map_src}" width="100%" height="520" frameborder="0"></iframe>'
        else:
            html += "<h2>Map</h2><p><em>Map not generated (no folium or no coordinates).</em></p>"
        html += "<h2>Analyst Insights</h2>" + insights_html(head, group, top=min(3, len(head)))
        md_cmds, html_cmds = _build_dump_commands(head, group, run_params or {}, max_rows=3)
        if html_cmds:
            html += html_cmds
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath

    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in header_lines:
                f.write(f"# {line}\n")
        disp.to_csv(filepath, mode='a', index=False)
        # write insights sidecar
        try:
            side = os.path.splitext(filepath)[0] + "_insights.txt"
            with open(side, 'w', encoding='utf-8') as g:
                g.write("Analyst Insights\n\n")
                g.write((insights_md(head, group, top=min(3, len(head))) or "No insights.") + "\n\n")
                md_cmds, _ = _build_dump_commands(head, group, run_params or {}, max_rows=3)
                if md_cmds:
                    g.write(md_cmds)
        except Exception:
            pass
        return filepath


