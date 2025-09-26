import pandas as pd
import plotly.express as px
from analytics import county_unsolved_rate
from config import COUNTY_GEOJSON
import re

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
    geojson = COUNTY_GEOJSON or "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

    fig = px.choropleth(
        rate, geojson=geojson, locations="fips", color="unsolved_rate",
        scope="usa", color_continuous_scale="Reds",
        hover_data={"fips": False, "unsolved_rate":":.2%", "total":True, "unsolved":True},
        title=title
    )
    fig.update_layout(margin=dict(l=0,r=0,t=50,b=0))
    return fig


    
def state_choropleth(df: pd.DataFrame, title: str):
    g = (df.groupby("State").size().rename("total").to_frame()
           .join(df.groupby("State")["Solved"].sum().rename("solved"))
           .reset_index())
    g["unsolved"] = g["total"] - g["solved"]
    g["unsolved_rate"] = (g["unsolved"] / g["total"]).fillna(0.0)
    g["state_code"] = g["State"].astype(str).str.strip().str.upper()  # expect 2-letter codes

    fig = px.choropleth(
        g, locations="state_code", locationmode="USA-states",
        color="unsolved_rate", scope="usa", color_continuous_scale="Reds",
        hover_data={"State": True, "total": True, "unsolved": True, "unsolved_rate": ":.2%"},
        title=title
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
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
