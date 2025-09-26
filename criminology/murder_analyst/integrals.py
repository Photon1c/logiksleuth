import numpy as np
import pandas as pd

def clearance_gap_integral(df: pd.DataFrame) -> float:
    """
    Integral over time of (homicides - solved). Assumes yearly aggregation.
    Use trapezoid rule on the red 'unsolved' gap.
    """
    g = (df
         .groupby("Year", dropna=True)
         .agg(total=("Homicide","count"), solved=("Solved","sum"))
         .reset_index()
         .sort_values("Year"))
    g["gap"] = g["total"] - g["solved"]
    # Trapezoid: sum ((y_i + y_{i+1})/2) * Δt ; here Δt=1
    y = g["gap"].to_numpy(dtype=float)
    if len(y) < 2:
        return float(y.sum())
    return float(np.trapz(y, dx=1.0))

def weighted_unsolved_density(df: pd.DataFrame, weight_col="VicCount") -> float:
    """
    Placeholder for more advanced continuous models (kernels, hazard, etc.).
    Returns a simple unsolved-weight density proxy for now.
    """
    w = (df["Solved"].eq(0)).astype(int) * df.get(weight_col, 1)
    return float(w.sum()) / max(len(df), 1)
