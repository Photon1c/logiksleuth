import pandas as pd
import plotly.express as px
from analytics import county_unsolved_rate
from config import COUNTY_GEOJSON
import re
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

def _clean_fips(series):
    # strip non-digits and left-pad to 5 (e.g., '8031' -> '08031', '8,031' -> '08031')
    return series.astype(str).str.replace(r"\D", "", regex=True).str.zfill(5)


def county_choropleth(df: pd.DataFrame, title: str):
    rate = county_unsolved_rate(df)
    rate = rate[rate["CNTYFIPS"].notna() & (rate["CNTYFIPS"].astype(str).str.len() > 0)]
    if rate.empty:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_layout(title=title + " (no county FIPS available after filters)")
        return fig

    rate["fips"] = _clean_fips(rate["CNTYFIPS"])
    # Ensure we embed the GeoJSON in the HTML (avoid runtime network fetches)
    geojson_source = COUNTY_GEOJSON or "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    if isinstance(geojson_source, dict):
        geojson = geojson_source
    else:
        src = str(geojson_source)
        try:
            parsed = urlparse(src)
            if parsed.scheme in {"http", "https"}:
                with urlopen(src) as r:
                    geojson = json.load(r)
            else:
                with open(Path(src), "r", encoding="utf-8") as f:
                    geojson = json.load(f)
        except Exception:
            # Fallback to Plotly-hosted if local read fails
            with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as r:
                geojson = json.load(r)

    fig = px.choropleth(
        rate, geojson=geojson, locations="fips", color="unsolved_rate",
        scope="usa", color_continuous_scale="Reds",
        featureidkey="id",
        hover_data={"fips": False, "unsolved_rate":":.2%", "total":True, "unsolved":True},
        title=title
    )
    fig.update_layout(margin=dict(l=0,r=0,t=50,b=0), height=600)
    return fig


    
def state_choropleth(df: pd.DataFrame, title: str):
    g = (df.groupby("State").size().rename("total").to_frame()
           .join(df.groupby("State")["Solved"].sum().rename("solved"))
           .reset_index())
    g["unsolved"] = g["total"] - g["solved"]
    g["unsolved_rate"] = (g["unsolved"] / g["total"]).fillna(0.0)

    # Normalize to 2-letter USPS codes for Plotly
    _name_to_code = {
        "ALABAMA":"AL","ALASKA":"AK","ARIZONA":"AZ","ARKANSAS":"AR","CALIFORNIA":"CA",
        "COLORADO":"CO","CONNECTICUT":"CT","DELAWARE":"DE","FLORIDA":"FL","GEORGIA":"GA",
        "HAWAII":"HI","IDAHO":"ID","ILLINOIS":"IL","INDIANA":"IN","IOWA":"IA",
        "KANSAS":"KS","KENTUCKY":"KY","LOUISIANA":"LA","MAINE":"ME","MARYLAND":"MD",
        "MASSACHUSETTS":"MA","MICHIGAN":"MI","MINNESOTA":"MN","MISSISSIPPI":"MS","MISSOURI":"MO",
        "MONTANA":"MT","NEBRASKA":"NE","NEVADA":"NV","NEW HAMPSHIRE":"NH","NEW JERSEY":"NJ",
        "NEW MEXICO":"NM","NEW YORK":"NY","NORTH CAROLINA":"NC","NORTH DAKOTA":"ND","OHIO":"OH",
        "OKLAHOMA":"OK","OREGON":"OR","PENNSYLVANIA":"PA","RHODE ISLAND":"RI","SOUTH CAROLINA":"SC",
        "SOUTH DAKOTA":"SD","TENNESSEE":"TN","TEXAS":"TX","UTAH":"UT","VERMONT":"VT",
        "VIRGINIA":"VA","WASHINGTON":"WA","WEST VIRGINIA":"WV","WISCONSIN":"WI","WYOMING":"WY",
        "DISTRICT OF COLUMBIA":"DC",
        # tolerate common misspelling in source data
        "RHODES ISLAND":"RI"
    }
    s = g["State"].astype(str).str.strip()
    s_up = s.str.upper()
    # if already 2-letter code, keep; otherwise map by name
    g["state_code"] = s_up.where(s_up.str.len().eq(2), s_up.map(_name_to_code))
    # drop rows we couldn't map
    g = g[g["state_code"].notna()]

    fig = px.choropleth(
        g, locations="state_code", locationmode="USA-states",
        color="unsolved_rate", scope="usa", color_continuous_scale="Reds",
        hover_data={"State": True, "total": True, "unsolved": True, "unsolved_rate": ":.2%"},
        title=title
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), height=600)
    return fig

    
    

def state_bar(df: pd.DataFrame, title: str):
    g = (df.groupby("State")
           .agg(total=("Homicide","count"),
                solved=("Solved","sum"))
           .reset_index())
    g["unsolved"] = g["total"] - g["solved"]
    g = g.sort_values("unsolved", ascending=False).head(20)
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8,6))
    plt.barh(g["State"], g["unsolved"])
    plt.title(title)
    plt.xlabel("Unsolved cases")
    plt.tight_layout()
    return fig
