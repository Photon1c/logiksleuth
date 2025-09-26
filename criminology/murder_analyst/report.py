from pathlib import Path
import base64, io

def _fig_to_png_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def _plotly_to_html_div(fig):
    return fig.to_html(include_plotlyjs="inline", full_html=False)

TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title></head>
<body>
<h2>{title}</h2>
<p><b>Integral (clearance gap):</b> {integral:.2f} &nbsp; | &nbsp; <b>Unsolved density:</b> {density:.4f}</p>
<div>{map_div}</div>
<h3>Yearly Total vs Solved</h3>
<img src="data:image/png;base64,{gap_png}" />
<h3>Yearly Unsolved Share</h3>
<img src="data:image/png;base64,{share_png}" />
</body></html>"""

def write_report(out_dir: Path, title: str, map_fig, gap_fig, share_fig, integral, density):
    map_div = _plotly_to_html_div(map_fig)
    gap_png = _fig_to_png_b64(gap_fig)
    share_png = _fig_to_png_b64(share_fig)
    html = TEMPLATE.format(title=title, map_div=map_div, gap_png=gap_png,
                           share_png=share_png, integral=integral, density=density)
    out = out_dir / "report.html"
    out.write_text(html, encoding="utf-8")
    return out
