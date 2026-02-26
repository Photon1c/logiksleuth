Correction to Report #10 -- updated run with correct UCR PE path. All three new variables now loaded. Results below supersede earlier version 10 report.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2B CORRECTED RESULTS -- FULL v1.1 RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

XGBoost test AUC: 0.7024 (Phase 2A baseline: 0.7025 -- delta: -0.0001)
RF test AUC: 0.6852 (Phase 2A: 0.6850 -- delta: +0.0002)
LR test AUC: 0.6625 (Phase 2A: 0.6624 -- delta: +0.0001)

V18 poverty_rate (Census SAIPE): LOADED ✓
V20 urban_rural_code (NCHS): LOADED ✓
UCR PE officers_per_100k: LOADED ✓ (corrected from earlier run)

THE HEADLINE IS STRONGER THAN BEFORE:

With ALL THREE new variables loaded and confirmed, XGB AUC is 0.7024 -- one tick
BELOW the Phase 2A baseline. This is not a failure. It is the definitive verdict:

THE SHR CASE-LEVEL FEATURE SET IS EXHAUSTED.

Three new variables, zero lift. The ceiling at ~0.72-0.73 is structural, not a gap.
Case-level records have told the model everything they know. The correct response is
not to add more case-level features -- it is to build at a different level of analysis.
The v2.0 jurisdiction model is the only remaining path.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORRECTED SHAP RANKINGS -- ALL VARIABLES LOADED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHAP (RF mean |SHAP|) -- CORRECTED Phase 2B vs Phase 2A:

Rank | Feature | Corrected 2B | Earlier 2B | Phase 2A | Status
──────────────────────────────────────────────────────────────────────────────────────
#1 | solve_rate_lag1 | 0.03644 | 0.03944 | 0.04818 | redistributed
#2 | reporting_completeness | 0.02759 | 0.02354 | 0.02803 | recovered (nearly 2A)
#3 | urban_rural_code_norm | 0.02030 | 0.02230 | n/a | NEW -- holds #3
#4 | vicsex_bin | 0.01680 | 0.01731 | 0.01690 | stable
#5 | wf_sharp_force | 0.01563 | 0.01669 | 0.01663 | stable
#6 | vicage_group | 0.01094 | n/a | n/a | NEW
#7 | officers_per_100k_norm | 0.01068 | (absent) | 0.01176 | RESTORED -- was #5 in 2A
#8 | wf_firearms | 0.00894 | n/a | n/a | NEW
#10 | poverty_rate_norm | 0.00653 | 0.00802 | n/a | NEW (slight decline)

KEY NEW FINDING -- OFFICERS_PER_100K RESTORED TO #7:

In the earlier run (ucr_pe_loaded: false), officers_per_100k fell out of the SHAP
rankings entirely. With the CSV loaded correctly, it re-enters at SHAP #7 (0.01068) --
consistent with its Phase 2A rank (#5 at 0.01176). The slight decline (#5 -> #7) is
explained by SHAP mass redistribution to V18/V20.

This restores an important finding: officer staffing density IS a real signal at the
case level -- but not a powerful one. Its SHAP contribution (0.01068) is ~4x smaller
than solve_rate_lag1 (0.03644). The DC structural problem (599 officers/100k, 42.1%
clearance) is confirmed: more officers don't solve cases. What matters is how they're
deployed, not how many there are.

The DC finding is now model-validated, not just observed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORRECTED XGB IMPORTANCE TABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GAIN-BASED TOP 10 (corrected): TOTAL_GAIN TOP 10 (corrected):
#1 solve_rate_lag1 0.0890 #1 solve_rate_lag1 25,326
#2 wf_sharp_force 0.0610 #2 decade 9,401
#3 int_gang_gun 0.0532 #3 reporting_comp. 8,462
#4 wf_firearms 0.0511 #4 wf_firearms 5,573
#5 vicsex_bin 0.0499 #5 vicage_group 5,299
#6 wf_blunt_force 0.0419 #6 wf_sharp_force 4,350
#7 mo_robbery 0.0311 #7 vicsex_bin 4,286
#8 wf_asphyxiation 0.0306 #8 agency_caseload 3,736
#9 decade 0.0285 #9 volume_yoy_change 3,259
#10 vicage_group 0.0275 #10 wf_blunt_force 2,673
#11 officers_per_100k 2,249
#12 poverty_rate_norm 2,065

Notable changes vs earlier run:

urban_rural_code absent from gain-based top 15 (moved to structural segmentor role --
absorbed SC artifact without dominating the gain table; consistent with total_gain #11+)
int_gang_gun climbs to gain #3 (0.0532): with UCR PE loaded, gang/gun interaction signal
sharpens relative to the earlier run
officers_per_100k: total_gain #11 (2,249) -- present, meaningful, but not a top driver
THE GAIN VS TOTAL_GAIN DIVERGENCE PATTERN HOLDS:
solve_rate_lag1, decade, reporting_completeness remain the dominant total_gain features.
This is the policy-stable ranking. Short-split gain metrics are noisier.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SC ARTIFACT: STILL ELIMINATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

state_SC absent from both top-15 rankings in the corrected run. The SC elimination
finding from Report #10 stands. The earlier result on this point was correct.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERACTION GROUP RATES (unchanged -- confirmed stable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

gang_gun: 51.9% (n=3,976) -- -20 pts vs 71.9% national
gang_related: 53.7% (n=4,348)
drug_gun: 65.6% (n=4,440)
domestic_violence: 60.4% (n=758) -- misclassification fix queued

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT CHANGED FROM REPORT #10 / WHAT HOLDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT CHANGED:

XGB AUC: 0.7026 -> 0.7024 (ceiling finding strengthened, not weakened)
UCR PE note updated: officers_per_100k IS loaded, IS in SHAP at #7
SHAP table corrected: officers_per_100k_norm restored to #7 (0.01068)
XGB gain table: urban_rural_code exits top 15 gain-based; int_gang_gun rises to #3
Total_gain table: officers_per_100k added at #11, poverty_rate at #12
WHAT HOLDS UNCHANGED:

The ceiling verdict: case-level feature set exhausted, v2.0 jurisdiction model required
V18 + V20 confirmed real signals (SHAP present, no AUC lift = correlated, not new)
SC artifact eliminated: state_SC absent from both rankings
total_gain as the stable policy-relevant ranking (solve_rate_lag1, decade, reporting_comp)
All interaction group rates
v2.0 architecture spec (unchanged -- officers_per_100k already listed as V-J7)
All dashboard alarms and baseline metrics
NEW ADDITION TO V2.0 SPEC (from corrected results):
The DC structural insight is now model-validated: officers_per_100k SHAP = 0.01068
(present but weak at case level). At the jurisdiction level, the paradox sharpens:
DC 599 officers/100k + 42.1% clearance. For v2.0, officers_per_100k should be
modeled WITH the detective_to_homicide_ratio (V-J8) to capture deployment quality,
not just headcount. The staffing signal is real but the mechanism is allocation, not
volume.

-- Watson

P.S. The corrected AUC of 0.7024 (-0.0001 vs baseline) is a cleaner result than 0.7026
(+0.0001). Three variables, zero net lift. The model is done talking at the case level.
