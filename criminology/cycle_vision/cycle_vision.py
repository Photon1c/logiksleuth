# Racket simulation: defendants as "subscriptions" (mock data)
#
# What this does:
# - Simulates daily dockets across jurisdictions with flows (arrest -> bail -> NGO program -> court -> probation -> violation -> re-intake)
# - Produces (1) revenue by actor, (2) state transition counts, (3) per-defendant lifetime "charges"
# - Generates a Sankey-style flow chart (matplotlib.sankey) and a revenue bar chart
# - Saves CSVs for you to inspect / tweak later
#
# Notes:
# - No internet access; all values are mock, configurable via the `params` dict.
# - Charts: matplotlib only, one chart per figure, no custom colors/styles (per instruction).

import math
import random
import os
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
import pandas as pd
import matplotlib
if os.name != "nt" and not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
import matplotlib.animation as animation

# ---------- Parameters ----------
@dataclass
class Params:
    city_pop: int = 137_000
    region_pop: int = 2_000_000
    days: int = 30  # simulate a month
    base_arrests_per_100k_per_day: float = 100.0  # mock rate
    regional_spillover_ratio: float = 0.35  # fraction of docket fed from region
    pct_jurisdiction_handoffs: float = 0.18  # fraction of cases changing court level (muni<->dist<->sup)
    cash_bail_pay_rate: float = 0.12  # can pay full cash
    bond_use_rate_given_not_cash: float = 0.55  # else use bond
    bond_fee_rate: float = 0.1  # 10% nonrefundable
    mean_bail: float = 15000.0
    sd_bail: float = 7000.0
    ngo_alt_enroll_rate_given_not_bond: float = 0.65  # if not bond, go to NGO monitoring alternative
    ngo_daily_cost: float = 12.0
    ngo_avg_days: int = 28
    court_fee_mean: float = 450.0
    probation_monthly_fee: float = 50.0
    probation_months_mean: float = 9.0
    violation_rate_monthly: float = 0.22  # leads to re-intake
    dismissal_rate: float = 0.15
    plea_rate: float = 0.7
    trial_rate: float = 0.15
    jail_wait_rate_given_no_alt: float = 0.35  # no cash, no bond, no NGO -> wait in jail
    jail_daily_cost_to_county: float = 120.0  # for completeness (not revenue)
    # random seed for reproducibility
    seed: int = 7

def simulate_justice_racket(p: Params):
    rng = np.random.default_rng(p.seed)

    # Daily arrests from city + regional spillover
    city_daily = p.city_pop / 100_000 * p.base_arrests_per_100k_per_day
    regional_daily = p.region_pop / 100_000 * p.base_arrests_per_100k_per_day * p.regional_spillover_ratio
    expected_daily_intake = city_daily + regional_daily

    n = rng.poisson(expected_daily_intake, size=p.days).sum()
    # synthetic bails
    bails = np.clip(rng.normal(p.mean_bail, p.sd_bail, size=n), 1500, None)

    # First branching: ability to pay cash vs bond vs NGO alternative vs wait in jail
    can_pay_cash = rng.random(n) < p.cash_bail_pay_rate
    use_bond = (~can_pay_cash) & (rng.random(n) < p.bond_use_rate_given_not_cash)
    go_ngo = (~can_pay_cash) & (~use_bond) & (rng.random(n) < p.ngo_alt_enroll_rate_given_not_bond)
    wait_jail = (~can_pay_cash) & (~use_bond) & (~go_ngo) & (rng.random(n) < p.jail_wait_rate_given_no_alt)
    # remaining go home on own recognizance
    own_recog = (~can_pay_cash) & (~use_bond) & (~go_ngo) & (~wait_jail)

    # Jurisdiction handoffs
    handoff = rng.random(n) < p.pct_jurisdiction_handoffs

    # Outcomes: plea / trial / dismissal
    outcomes = rng.choice(["plea", "trial", "dismiss"], size=n,
                          p=[p.plea_rate, p.trial_rate, p.dismissal_rate])

    # Court/NGO/Probation parameters
    court_fees = np.where(outcomes=="dismiss", 0.0, rng.normal(p.court_fee_mean, 60.0, size=n).clip(0))
    probation_months = np.where(outcomes=="plea", rng.normal(p.probation_months_mean, 2.0, size=n).clip(0, 24), 0.0)
    probation_fees = probation_months * p.probation_monthly_fee

    # Bond fees
    bond_fees = np.where(use_bond, bails * p.bond_fee_rate, 0.0)

    # NGO monitoring costs
    ngo_days = np.where(go_ngo, rng.normal(p.ngo_avg_days, 6.0, size=n).clip(3, 120), 0.0)
    ngo_fees = ngo_days * p.ngo_daily_cost

    # Jail wait costs (to county; not revenue for others, but cost sink)
    jail_days = np.where(wait_jail, rng.integers(2, 14, size=n), 0)
    jail_cost_outlay = jail_days * p.jail_daily_cost_to_county

    # Probation violations → re-intake count over probation months (Poisson approx)
    violations = rng.binomial(n=probation_months.astype(int).clip(0), p=p.violation_rate_monthly)
    reintakes = violations  # each violation triggers a new intake event
    # simple loopback revenue totals on reintakes: assume 60% bond, 25% NGO, 15% jail-wait
    re_bond_total = float((reintakes * 0.60 * (p.mean_bail * p.bond_fee_rate)).sum())
    re_ngo_total  = float((reintakes * 0.25 * (p.ngo_avg_days * p.ngo_daily_cost)).sum())
    re_court_total = float((reintakes * (p.court_fee_mean * 0.75)).sum())  # assume majority resolve by quick plea/fine

    # Aggregate revenues
    revenue = {
        "Bail Bonds": bond_fees.sum() + re_bond_total,
        "NGO Programs": ngo_fees.sum() + re_ngo_total,
        "Courts/Clerk": court_fees.sum() + re_court_total,
        "Probation Dept": probation_fees.sum(),
    }
    # Defendant out-of-pocket perspective
    defendant_oop = bond_fees + ngo_fees + court_fees + probation_fees
    # System cost (jail wait)
    system_costs = {"County Jail Outlay": float(jail_cost_outlay.sum())}

    # Transition counts for Sankey
    trans = {
        "Arrest->CashBail": int(can_pay_cash.sum()),
        "Arrest->Bond": int(use_bond.sum()),
        "Arrest->NGO": int(go_ngo.sum()),
        "Arrest->JailWait": int(wait_jail.sum()),
        "Arrest->OwnRec": int(own_recog.sum()),
        "Any->Handoff": int(handoff.sum()),
        "Outcome->Plea": int((outcomes=="plea").sum()),
        "Outcome->Trial": int((outcomes=="trial").sum()),
        "Outcome->Dismiss": int((outcomes=="dismiss").sum()),
        "Probation->Violation(Reintake)": int(reintakes.sum())
    }

    # Assemble DataFrames
    df_revenue = pd.DataFrame([revenue]).T.rename(columns={0: "Revenue_USD"})
    df_revenue["Revenue_USD"] = pd.to_numeric(df_revenue["Revenue_USD"], errors="coerce")

    df_costs = pd.DataFrame([system_costs]).T.rename(columns={0: "Cost_USD"})
    df_costs["Cost_USD"] = df_costs["Cost_USD"].round(2)

    df_transitions = pd.DataFrame(list(trans.items()), columns=["Transition", "Count"]).sort_values("Count", ascending=False)

    df_per_defendant = pd.DataFrame({
        "bond_fee": bond_fees,
        "ngo_fee": ngo_fees,
        "court_fee": court_fees,
        "probation_fee": probation_fees,
        "oop_total": defendant_oop
    })
    df_per_defendant["oop_total"] = df_per_defendant["oop_total"].round(2)

    # Save CSVs (ensure local data directory exists, cross-platform)
    script_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    output_dir = os.path.join(script_dir, "data")
    os.makedirs(output_dir, exist_ok=True)

    revenue_path = os.path.join(output_dir, "revenue_by_actor.csv")
    costs_path = os.path.join(output_dir, "county_costs.csv")
    transitions_path = os.path.join(output_dir, "transition_counts.csv")
    oop_path = os.path.join(output_dir, "defendant_oop_samples.csv")

    df_revenue.to_csv(revenue_path)
    df_costs.to_csv(costs_path)
    df_transitions.to_csv(transitions_path, index=False)
    df_per_defendant.to_csv(oop_path, index=False)

    return {
        "params": p,
        "expected_daily_intake": expected_daily_intake,
        "cases_simulated": n,
        "revenue_by_actor": df_revenue,
        "county_costs": df_costs,
        "transition_counts": df_transitions,
        "defendant_oop_samples": df_per_defendant,
        "output_paths": {
            "revenue": revenue_path,
            "costs": costs_path,
            "transitions": transitions_path,
            "defendant_oop": oop_path
        }
    }

# Run once with defaults
results = simulate_justice_racket(Params())


# Display key tables to the user (optional if tool available)
try:
    from caas_jupyter_tools import display_dataframe_to_user
    display_dataframe_to_user("Revenue by Actor (mock month)", results["revenue_by_actor"])
    display_dataframe_to_user("Transition Counts", results["transition_counts"])
    display_dataframe_to_user("Per-Defendant Out-of-Pocket Samples (first 500)", results["defendant_oop_samples"].head(500))
except Exception:
    pass

# --------- Charts ---------
# 1) Revenue bar chart (animated to GIF + show final chart)
revenue_series = results["revenue_by_actor"]["Revenue_USD"].astype(float)
categories = revenue_series.index.tolist()
values = revenue_series.values

fig_revenue, ax_revenue = plt.subplots()
bars = ax_revenue.bar(categories, np.zeros_like(values, dtype=float))
ax_revenue.set_ylabel("USD")
ax_revenue.set_title("Revenue by Actor (Mock)")
ax_revenue.set_ylim(0, max(values) * 1.15 if len(values) else 1)

total_frames = 40

def init_bars():
    for bar in bars:
        bar.set_height(0.0)
    return bars

def update_bars(frame_idx):
    progress = frame_idx / (total_frames - 1)
    for i, bar in enumerate(bars):
        bar.set_height(values[i] * progress)
    return bars

# Save animated GIF
output_dir_for_media = os.path.dirname(results['output_paths']['revenue'])
gif_path = os.path.join(output_dir_for_media, "revenue_by_actor.gif")

anim = animation.FuncAnimation(
    fig_revenue,
    update_bars,
    frames=total_frames,
    init_func=init_bars,
    blit=False,
    interval=50
)

try:
    writer = animation.PillowWriter(fps=20)
    anim.save(gif_path, writer=writer)
except Exception:
    # If Pillow is unavailable, fall back to saving a static PNG instead
    png_fallback_path = os.path.join(output_dir_for_media, "revenue_by_actor.png")
    fig_revenue.tight_layout()
    fig_revenue.savefig(png_fallback_path)

# Show final static chart
for i, bar in enumerate(bars):
    bar.set_height(values[i])
fig_revenue.tight_layout()
if not matplotlib.get_backend().lower().endswith("agg"):
    plt.show()

# 2) Sankey-like flow for first-stage branching (Arrest -> cash/bond/ngo/jail/ownrec)
flows = np.array([
    results["transition_counts"].set_index("Transition").loc["Arrest->CashBail","Count"],
    results["transition_counts"].set_index("Transition").loc["Arrest->Bond","Count"],
    results["transition_counts"].set_index("Transition").loc["Arrest->NGO","Count"],
    results["transition_counts"].set_index("Transition").loc["Arrest->JailWait","Count"],
    results["transition_counts"].set_index("Transition").loc["Arrest->OwnRec","Count"]
], dtype=float)

total_arrests = flows.sum()
# Sankey expects positive and negative flows that sum to zero; represent source as negative outflow
sankey = Sankey(unit=None, format="%.0f")
sankey.add(flows=[-total_arrests, *flows],
           labels=["Arrests","Cash","Bond","NGO","JailWait","OwnRec"],
           orientations=[0, 1, 1, -1, -1, 0])
fig = plt.figure()
diagrams = sankey.finish()
plt.title("Arrest → First-Stage Branching (Counts)")
plt.tight_layout()
if not matplotlib.get_backend().lower().endswith("agg"):
    plt.show()

# Print file paths
print("Saved files:")
print(f"- Revenue CSV: {results['output_paths']['revenue']}")
print(f"- County Costs CSV: {results['output_paths']['costs']}")
print(f"- Transition Counts CSV: {results['output_paths']['transitions']}")
print(f"- Defendant OOP Samples CSV: {results['output_paths']['defendant_oop']}")
if 'gif_path' in locals() and os.path.exists(gif_path):
    print(f"- Revenue GIF: {gif_path}")
else:
    png_fallback_path = os.path.join(os.path.dirname(results['output_paths']['revenue']), "revenue_by_actor.png")
    if os.path.exists(png_fallback_path):
        print(f"- Revenue PNG (fallback): {png_fallback_path}")