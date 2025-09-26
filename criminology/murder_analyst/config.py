from pathlib import Path

DATA_CSV = Path("C:/workingcauldron/brewery/criminology/logicsleuth032/fusion_deduction/data/SHR65_23.csv")  # <-- set your path
# If you have a local file, set it here; otherwise leave as None
COUNTY_GEOJSON = "C:/workingcauldron/geo/counties-10m.json"  # or None

OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Optional: local GeoJSON for US counties if you have one (kept None to rely on Plotly built-ins)
COUNTY_GEOJSON = None

DEFAULTS = {
    "state": None,           # e.g., "CO"
    "msa": None,             # e.g., "Seattle-Tacoma-Bellevue, WA"
    "year_min": 1980,
    "year_max": 2025,
    "vic_age_min": None,
    "vic_age_max": None,
    "vic_sex": None,         # "Male"/"Female"
    "weapon_in": None,       # list like ["Strangulation","Other or Type Unknown"]
    "solved": None,          # 0 unsolved, 1 solved, None both
}
