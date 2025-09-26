import pandas as pd

REQUIRED = [
    "ID","CNTYFIPS","Ori","State","Agency","Agentype","Source","Solved",
    "Year","Month","Incident","ActionType","Homicide","Situation","VicAge",
    "VicSex","VicRace","VicEthnic","OffAge","OffSex","OffRace","OffEthnic",
    "Weapon","Relationship","Circumstance","Subcircum","VicCount","OffCount",
    "FileDate","MSA"
]

def load_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"CNTYFIPS": str})  # keep FIPS as zero-padded str

    df["Solved"] = (df["Solved"]
        .replace({True:1, False:0, "Y":1, "N":0, "Yes":1, "No":0,
                  "Solved":1, "Unsolved":0, "S":1, "U":0}))
    df["Solved"] = pd.to_numeric(df["Solved"], errors="coerce").fillna(0).astype(int)


    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    # Normalize
    df["Solved"] = pd.to_numeric(df["Solved"], errors="coerce").fillna(0).astype(int)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df["VicAge"] = pd.to_numeric(df["VicAge"], errors="coerce")
    df["Weapon"] = df["Weapon"].astype(str)
    df["State"] = df["State"].astype(str)
    df["MSA"] = df["MSA"].astype(str)
    return df
