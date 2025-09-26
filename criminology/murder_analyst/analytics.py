import pandas as pd
from integrals import clearance_gap_integral, weighted_unsolved_density

def yearly_stats(df: pd.DataFrame) -> pd.DataFrame:

    grp = df.groupby("Year", dropna=True)
    g = (grp.size().rename("total").to_frame()
           .join(grp["Solved"].sum().rename("solved"))
           .reset_index()
           .sort_values("Year"))
    g["unsolved"] = g["total"] - g["solved"]
    g["solve_rate"] = (g["solved"] / g["total"]).round(4)
    return g


def county_unsolved_rate(df: pd.DataFrame) -> pd.DataFrame:

    grp = df.groupby("CNTYFIPS")
    g = (grp.size().rename("total").to_frame()
           .join(grp["Solved"].sum().rename("solved"))
           .reset_index())
    g["unsolved"] = g["total"] - g["solved"]
    g["unsolved_rate"] = (g["unsolved"] / g["total"]).fillna(0.0)
    return g


def integral_summary(df: pd.DataFrame) -> dict:
    return {
        "clearance_gap_integral": clearance_gap_integral(df),
        "unsolved_density": weighted_unsolved_density(df),
        "rows": len(df)
    }
