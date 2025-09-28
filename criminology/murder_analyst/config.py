from pathlib import Path

DATA_CSV = Path("D:\SereneOcean\csint_suite\criminology\inputs\criminology\SHR65_23.csv")  # <-- set your path
# If you have a local file, set it here; otherwise leave as None
COUNTY_GEOJSON = "D:\SereneOcean\csint_suite\criminology\inputs\criminology\counties-10m.json"  # or None

OUTPUT_DIR = Path("./output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Optional: prefer local GeoJSON if the path exists; otherwise None to use Plotly default
from os import path as _os_path
if isinstance(COUNTY_GEOJSON, str) and not _os_path.exists(COUNTY_GEOJSON):
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
