import os
import pandas as pd


# Minimal ORI→(lat, lon) hints; add as needed
GEO_HINTS = {
    'AL00301': (32.3668, -86.2999),   # Montgomery PD
    'AL00401': (32.4640, -86.4597),   # Prattville
    'AL02900': (32.5970, -86.1430),   # Elmore County
    'AL04500': (32.2730, -86.6510),   # Lowndes County
}


def _attach_coords(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if {'LAT','LON'}.issubset(d.columns):
        return d
    d['LAT'] = d['Ori'].map(lambda x: GEO_HINTS.get(str(x), (None, None))[0])
    d['LON'] = d['Ori'].map(lambda x: GEO_HINTS.get(str(x), (None, None))[1])
    return d


def build_map_from_per_ori(csv_path: str, outdir: str) -> str | None:
    try:
        import folium
    except Exception:
        return None

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None

    needed = {'Ori','Agency','UNSOLVED','TOTAL','PERCENT'}
    if not needed.issubset(df.columns):
        return None

    df = _attach_coords(df)
    df = df.dropna(subset=['LAT','LON'])
    if df.empty:
        return None

    lat0, lon0 = df['LAT'].mean(), df['LON'].mean()
    m = folium.Map(location=[lat0, lon0], zoom_start=7, control_scale=True)

    def color_for(p):
        try:
            if p <= 0.25:
                return '#d73027'
            if p <= 0.33:
                return '#fc8d59'
            return '#91cf60'
        except Exception:
            return '#aaaaaa'

    for _, r in df.iterrows():
        try:
            radius = max(4, min(18, float(r['UNSOLVED']) * 0.6))
        except Exception:
            radius = 6
        folium.CircleMarker(
            location=(r['LAT'], r['LON']),
            radius=radius,
            color=color_for(r['PERCENT']),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>{r.get('Agency','')}</b><br/>ORI: {r.get('Ori','')}<br/>"
                f"Unsolved: {int(r.get('UNSOLVED',0))}/{int(r.get('TOTAL',0))}<br/>"
                f"Clearance: {float(r.get('PERCENT',0))*100:.1f}%", max_width=300)
        ).add_to(m)

    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, 'report_map.html')
    try:
        m.save(out)
    except Exception:
        return None
    return out


