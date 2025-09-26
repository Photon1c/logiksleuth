import pandas as pd
import re

def apply_filters(df: pd.DataFrame, **kw) -> pd.DataFrame:
    q = df.copy()
    if kw.get("state"):
        q = q[q["State"].eq(kw["state"])]
    if kw.get("msa"):
        q = q[q["MSA"].str.contains(kw["msa"], case=False, na=False)]
    y0, y1 = kw.get("year_min"), kw.get("year_max")
    if y0 is not None: q = q[q["Year"] >= y0]
    if y1 is not None: q = q[q["Year"] <= y1]
    a0, a1 = kw.get("vic_age_min"), kw.get("vic_age_max")
    if a0 is not None: q = q[q["VicAge"] >= a0]
    if a1 is not None: q = q[q["VicAge"] <= a1]
    if kw.get("vic_sex"):
        q = q[q["VicSex"].astype(str).str.strip().str.lower().eq(kw["vic_sex"].lower())]
    weapons = kw.get("weapon_in")
    if weapons:
        pattern = "|".join(re.escape(w) for w in weapons)  # partial, case-insensitive match
        q = q[q["Weapon"].astype(str).str.contains(pattern, case=False, na=False)]
    if kw.get("solved") in (0,1):
        q = q[q["Solved"].eq(kw["solved"])]
    return q
