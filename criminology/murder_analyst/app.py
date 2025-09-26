import argparse
from config import DATA_CSV, OUTPUT_DIR, DEFAULTS
from data_loader import load_csv
from filters import apply_filters
from analytics import yearly_stats, integral_summary
from geo import county_choropleth
from charts import yearly_gap_chart, unsolved_share_bar
from report import write_report
from geo import county_choropleth, state_choropleth

def parse_args():
    p = argparse.ArgumentParser(description="MurderData SHR/UCR analyst")
    p.add_argument("--state", type=str)
    p.add_argument("--msa", type=str)
    p.add_argument("--year-min", type=int, default=DEFAULTS["year_min"])
    p.add_argument("--year-max", type=int, default=DEFAULTS["year_max"])
    p.add_argument("--vic-age-min", type=int)
    p.add_argument("--vic-age-max", type=int)
    p.add_argument("--vic-sex", type=str, choices=["Male","Female"])
    p.add_argument("--weapon", action="append", help="repeat for multiple (e.g., --weapon Strangulation)")
    p.add_argument("--solved", type=int, choices=[0,1])
    # add inside parse_args()
    p.add_argument("--preset", type=str, choices=["jonbenet", "seattle_green_river"])
    p.add_argument("--map-level", type=str, choices=["state", "county"], default="state")

    return p.parse_args()
    
def apply_preset(args):
    if args.preset == "jonbenet":
        args.state = "CO"
        args.year_min, args.year_max = 1996, 1996
        args.vic_age_min, args.vic_age_max = 6, 6
        args.vic_sex = "Female"
        args.weapon = ["Strangulation"]
        args.solved = None
    elif args.preset == "seattle_green_river":
        args.msa = "Seattle"
        args.vic_sex = "Female"
        args.weapon = ["Strangulation", "Other or Type Unknown"]
        args.year_min, args.year_max = 1980, args.year_max  # keep your current max
        args.solved = 0
    
    

def main():
    args = parse_args()
    args = parse_args()
    if args.preset:
        apply_preset(args)
    df = load_csv(DATA_CSV)
    q = apply_filters(
        df,
        state=args.state, msa=args.msa,
        year_min=args.year_min, year_max=args.year_max,
        vic_age_min=args.vic_age_min, vic_age_max=args.vic_age_max,
        vic_sex=args.vic_sex, weapon_in=args.weapon, solved=args.solved
    )
    print(f"[info] rows={len(q)}  states={q['State'].nunique()}  counties(non-null)={q['CNTYFIPS'].dropna().nunique()}")

    if q.empty and args.weapon:
        print("[warn] 0 rows with current filters. Retrying without weapon filter…")
        q = apply_filters(
            df,
            state=args.state, msa=args.msa,
            year_min=args.year_min, year_max=args.year_max,
            vic_age_min=args.vic_age_min, vic_age_max=args.vic_age_max,
            vic_sex=args.vic_sex, weapon_in=None, solved=args.solved
        )
    print(f"[info] rows after filter: {len(q)}")
    if q.empty:
        print("[error] No data matches the filters. Loosen criteria.")
        return
    
    ys = yearly_stats(q)
    ints = integral_summary(q)

    map_fig = state_choropleth(q, title="Unresolved Share by State") if args.map_level == "state" \
          else county_choropleth(q, title="Unresolved Rate by County")
    gap_fig = yearly_gap_chart(ys, "Total vs Solved (Shaded = Unsolved Gap)")
    share_fig = unsolved_share_bar(ys, "Unsolved Share by Year")

    report_path = write_report(
        OUTPUT_DIR, title="Homicide Pattern Report",
        map_fig=map_fig, gap_fig=gap_fig, share_fig=share_fig,
        integral=ints["clearance_gap_integral"], density=ints["unsolved_density"]
    )
    print(f"Report written: {report_path.resolve()}")

if __name__ == "__main__":
    main()
