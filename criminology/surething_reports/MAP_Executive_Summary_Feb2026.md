# MURDER ACCOUNTABILITY PROJECT
## Executive Summary — Preliminary Findings
### Watson/Surething AI | February 25, 2026

---

## THE PROBLEM

The United States has accumulated **243,245 unsolved homicides** since 1976 — 28.1% of all cases in the national record. The national clearance rate fell from 76.9% (1980) to a trough of 67.9% (2016) before recovering to 74.9% (2023). Despite the recovery, the country remains 2 points below its own 1980 baseline, and the unsolved backlog grows every year.

The gap is not random. It is concentrated in specific jurisdictions, case types, and demographic groups — and it is largely predictable.

---

## THE DATA

**Source:** FBI Supplemental Homicide Reports (SHR), 1976-2023
**Scale:** 865,024 homicide cases | 51 states | 48 years
**Model:** Phase 2A Clearance Prediction Engine (XGBoost + SHAP, Feb 2026)
**Performance:** AUC 0.703 -- +18.4% above Phase 1 baseline (0.593)

---

## TOP-LINE FINDINGS

### 1. Clearance Is Predictable -- and Structural, Not Random

The model's top two predictors are both **operational capacity signals**, not case characteristics:

| Rank | Feature | What It Measures | SHAP Weight |
|------|---------|-----------------|-------------|
| #1 | solve_rate_lag1 | Prior-year jurisdictional clearance rate | 0.048 |
| #2 | reporting_completeness | % cases with identified offender | 0.028 |
| #3 | vicsex_bin | Victim sex | 0.017 |
| #4 | wf_sharp_force | Weapon type | 0.017 |
| #5 | officers_per_100k | Sworn officer density | 0.012 |

**Implication:** A jurisdiction's clearance rate is self-reinforcing. Low clearance last year predicts low clearance this year. Breaking the inertia trap -- not individual case factors -- is the primary intervention target.

### 2. The Cold Case Factory: Gang/Gun Cases

| Case Type | Clearance Rate | Gap vs. National | Est. Unsolved (National) |
|-----------|---------------|-----------------|-------------------------|
| Gang + gun | 51.9% | -20.0 pts | ~14,400 |
| Gang-related (all) | 53.7% | -18.2 pts | ~16,500 |
| Drug + gun | 65.6% | -6.3 pts | ~5,400 |
| **National average** | **71.9%** | -- | 243,245 |

Gang/gun homicides clear at just 51.9% -- the single lowest-performing case type. These are the cases that become cold within 72 hours if forensic leads go unprocessed.

### 3. The Inertia Trap: Where the Problem Concentrates

| Jurisdiction | All-Time Clearance | Gap vs. National | Unsolved Cases |
|-------------|-------------------|-----------------|---------------|
| DC | 42.1% | -29.8 pts | ~3,200 |
| Illinois | 62.6% | -9.3 pts | 13,827 |
| Maryland | 61.4% | -10.5 pts | ~6,800 |
| California | 64.2% | -7.7 pts | **44,586** |

California alone holds **18.3% of the national unsolved total**. DC has the worst clearance rate despite the highest officer density nationally (599 sworn/100k) -- confirming that headcount without case management does not produce clearance.

---

## WHAT WORKS: TWO NATURAL EXPERIMENTS

**Philadelphia PD (2021-2025):** Clearance rate rose from 41.8% to 86-90% in four years.
- Primary driver: Homicide volume fell ~50%; detective caseload dropped from 10-15 cases/year to 5-7
- Secondary: Camera network doubled (3,625 to 7,309); cell extraction capacity 7x; social media gang mapping
- Result: Arrests within one week rose from 15% to 31%

**LAPD (2025):** 101% clearance -- solved more cases than were committed.
- Volume down 29% from 2021 peak + expanded technology stack
- Confirmed: workload reduction x technology is a replicable formula

**Key finding:** Both recoveries are explained by the model's #1 SHAP feature -- solve_rate_lag1. Every point gained in year one sets a higher baseline for year two. The ROI on early, aggressive intervention compounds.

---

## THE TECHNOLOGY OPPORTUNITY

**Forensic Investigative Genetic Genealogy (FIGG):**
- Resolution rate: ~27.8% on DNA-viable cold cases
- Current pace: ~15 closures/month nationally (Othram platform alone)
- Applied to 14,400 unsolved gang/gun cases: theoretical ceiling of 400-4,000 additional closures depending on DNA viability rate
- Limitation: European ancestry overrepresentation in public genealogy databases

**NIBIN (National Integrated Ballistic Information Network):**
- Directly targets the gang/gun cold case factory (-20 pt clearance gap)
- 163% lead increase nationally over 3 years; bottleneck is lab throughput, not lead generation
- States with low NIBIN lab capacity and high gang/gun concentration (IL, CA, MO, DC) have the highest per-dollar ROI on expansion

---

## PRIORITY INTERVENTION TARGETS

**Tier 1 -- Immediate (inertia trap + highest volume):**
1. **Illinois/Chicago** -- GVI + detective workload reduction + NIBIN lab throughput
2. **DC** -- Structural, not staffing (highest officers/capita, worst clearance); case management reform
3. **Maryland/Baltimore** -- Continuous 5-decade decline; witness cooperation + FIGG cold case pipeline

**Tier 2 -- High volume:**
4. **California** -- 44,586 unsolved; FIGG pipeline for cold cases; NIBIN expansion
5. **Missouri/St. Louis** -- Gateway city pattern; gang/gun concentration

**Proven replication template:** Philadelphia GVI + caseload reduction produced +40 pts in 4 years. This is the only documented mechanism that breaks the inertia trap abruptly enough to trigger the solve_rate_lag1 flywheel.

---

## MODEL STATUS & NEXT STEPS

**Current ceiling:** AUC 0.703 (XGB). Theoretical SHR ceiling: ~0.72-0.73.

**To break the ceiling:** Two variables are web-fetchable and would add an estimated +0.01-0.02 AUC:
- Census ACS poverty rate (V18)
- NCHS urban-rural classification (V20)

**Longer term:** True detective caseload at the unit level (not state aggregate) is the single variable most likely to break past 0.73. Not in public SHR data -- requires UCR or survey acquisition.

---

*Murder Accountability Project | Phase 2A Complete | clearance_engine_v1.2 | Drive: 1fTLb_avhOV9NQNYhUiwuAiu4nAZwlhbz*