import pandas as pd
import re

def apply_filters(df: pd.DataFrame, **kw) -> pd.DataFrame:
    q = df.copy()
    if kw.get("state"):
        # Accept either USPS code (e.g., "CO") or full state name (e.g., "Colorado")
        s = str(kw["state"]).strip()
        code_to_name = {
            "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California",
            "CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia",
            "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa",
            "KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
            "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri",
            "MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey",
            "NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio",
            "OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina",
            "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont",
            "VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
            "DC":"District of Columbia"
        }
        state_name = code_to_name.get(s.upper(), s)
        q = q[q["State"].astype(str).str.strip().str.casefold() == state_name.strip().casefold()]
    if kw.get("msa"):
        q = q[q["MSA"].str.contains(kw["msa"], case=False, na=False)]
    y0, y1 = kw.get("year_min"), kw.get("year_max")
    if y0 is not None: q = q[q["Year"] >= y0]
    if y1 is not None: q = q[q["Year"] <= y1]
    a0, a1 = kw.get("vic_age_min"), kw.get("vic_age_max")
    if a0 is not None: q = q[q["VicAge"] >= a0]
    if a1 is not None: q = q[q["VicAge"] <= a1]
    if kw.get("vic_sex"):
        # Normalize VicSex filter to accept 'M'/'F' or 'Male'/'Female'
        v = str(kw["vic_sex"]).strip().lower()
        alias = {"m":"male","f":"female"}
        v = alias.get(v, v)
        q = q[q["VicSex"].astype(str).str.strip().str.lower().replace({"m":"male","f":"female"}).eq(v)]
    weapons = kw.get("weapon_in")
    if weapons:
        pattern = "|".join(re.escape(w) for w in weapons)  # partial, case-insensitive match
        q = q[q["Weapon"].astype(str).str.contains(pattern, case=False, na=False)]
    if kw.get("solved") in (0,1):
        q = q[q["Solved"].eq(kw["solved"])]
    return q
