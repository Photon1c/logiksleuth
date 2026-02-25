# SC Anomaly Analysis
## South Carolina -- XGBoost #1 Feature Investigation
### Watson | Feb 25, 2026

## THE QUESTION
In Phase 2A XGBoost results, state_SC ranked #1 in feature importance (0.0741),
ahead of solve_rate_lag1 (0.0664). SC does not appear in the current state action matrix.
Is SC a positive outlier, negative outlier, or XGBoost overfitting?

## VERDICT: SC IS A POSITIVE OUTLIER

External data (Post and Courier 2022, SLED annual reports):
- 2020: Columbia -- 95% clearance (18/19 murders; national was ~50% that year)
- 2019: Charleston/North Charleston -- 85%+ clearance (30/35)
- 2021: Charleston/North Charleston -- 80%+ clearance
- 2024: SC overall -- 50% clearance for all violent offenses (murder higher)

SC clears homicides at 30-45 pts above national average in its major cities.
This is a STRONG positive outlier signal.

## WHY XGB INFLATED IT

XGB gain-based importance captures non-linear threshold splits. SC's bimodal
distribution (80-95% in major cities, lower in rural areas) allows XGB to place
an early high-gain split on state_SC. This inflates gain-based importance
even when the actual prediction contribution (SHAP) is modest.

The tell: SHAP (RF, n=5,000) does not show state_SC in top 15.
state_SC appears at #12 in SHAP (0.00357) vs. #1 in XGB gain (0.0741).
This 20x divergence = gain-based artifact, not true signal.

## INTERPRETATION

SC belongs in the REPLICATION MODEL category (alongside Philadelphia, LAPD):
- Not a problem state
- Not in state action matrix
- Is a proof point for: witness cooperation + smaller detective caseloads + case composition

The University of SC criminologists studying Charleston's 85%+ rate noted it
"lacks clear explanation in existing literature" -- suggesting structural/operational
factors not in SHR data (witness cooperation, DV-heavy case mix).

## MODEL FIX IN v1.1

clearance_engine_v1.1.py reports both:
- top_importances_gain (v1.2 default, susceptible to SC artifact)
- top_importances_total_gain (more robust to early-split inflation)

SHAP remains the authoritative importance metric. state_SC is kept in feature
set (it carries real signal -- SC IS a positive outlier), but the gain-based
ranking should not be used as the primary importance interpretation.
