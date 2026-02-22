Good morning, Sherlock —

Report #2. Today's focus: full SHR schema deep dive — the complete
column map, feature logic, and trigger thresholds underlying your
codebase. Plus this week's forensic news is genuinely significant.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1 — METRICS DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NATIONAL CLEARANCE RATE (tracking same recovery trajectory)
  2022: 52.3%  ◄ historic low
  2023: 57.8%
  2024: 61.4%
  2025: ~64%   ◄ best in 15+ years
  Gap to 1980 baseline (72%): still 11 points

KEY ALARM INDICATORS (SHR 1976–2023, n=47,288):

🚨 CLEARANCE COLLAPSE — 12,339 cases
   Threshold: solved rate ≤ 30%, min 10 cases in cluster
   → Over 12,000 cases in clusters meeting the threshold for
'functional impunity.'
     Structural failure, not noise.

🚨 MO COHERENCE — 44,972 cases
   Threshold: 1-(unique_mo/cluster_size) ≥ 0.70, min 5 cases
   → Nearly 45,000 cases in methodologically coherent groups.
     Not random violence — organized, repeated, patterned behavior.

⚠️ VICTIMOLOGY COHERENCE — 8,530 cases
   Threshold: dominant_vic_fingerprint/cluster_size ≥ 0.60, min 8 cases
   → Consistent predatory targeting by age+sex combination.

⚠️ WEAPON RARITY — 8,387 cases
   Threshold: weapon_rarity ≥ 0.95 (top 5% rarest), min 3 cases

DETROIT GAMMA — PRIORITY CLUSTER (Holmes Risk: 0.687, highest in dataset):
  Weapon: Gas asphyxiation (100%)  |  Victims: Female, adults 13–64,
intimate partner
  Span: 2002–2016  |  Burst: 2015 (4 cases), 2016 (3 cases)
  Heating season: 20%  |  Unsolved rate: 42.8% / 0% intimate partner sub-series
  Status: High Serial Offender Likelihood | High Micro-Signature Potential

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2 — SHR SCHEMA DEEP DIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE RAW COLUMNS
  weapon, relationship, circumstance, situation
  vicage, vicsex, year, month, countyfips, msa, state
  solved (0=unsolved / 1=solved)
  pattern_cluster, st_cluster, anomaly_score, temporal_spike

ENGINEERED FEATURES (features.py)
  mo_text          weapon | relationship | circumstance | situation
(pipe-joined)
  mo_rarity        1.0 - (mo_freq / total_cases)
  vicage_group     0-17=juvenile | 18-34=young_adult |
35-54=middle_age | 55+=elderly
  vicsex_code      M→1 | F→2 | other→9
  vic_fingerprint  vicsex_code + '_' + vicage_group  (e.g. '2_young_adult')
  vic_rarity       1.0 - (vic_fingerprint_freq / total)
  weapon_rarity    1.0 - (weapon_freq / total)
  geo_rarity       1.0 - (county_count / total)
  temporal_rarity  1.0 / year_count
  decade           (year // 10) * 10
  year_month       'YYYY-MM'

TRIGGER THRESHOLDS (exact values from triggers.py)
  Clearance Collapse     mean(solved) ≤ 0.30,  min 10 cases
  MO Coherence           1-(unique_mo/size) ≥ 0.70,  min 5 cases
  Victimology Coherence  dominant_vic/size ≥ 0.60,  min 8 cases
  Weapon Rarity          weapon_rarity ≥ 0.95,  min 3 cases
  Spatiotemporal         ≥5 cases within 50km & ≤15yr span, OR
temporal_spike ≥ 2.0
  Pattern Anomaly        mean(anomaly_score) ≥ 2.0,  min 5 cases

WEAPON FAMILIES (partitioning.py)
  firearms       Handgun, Rifle, Shotgun, Firearm (unspecified), Other gun
  sharp_force    Knife, cutting instrument
  blunt_force    Blunt object, Personal weapons/beating
  asphyxiation   Strangulation, Asphyxiation, Suffocation, Hanging
  fire           Fire
  other          Other, Unknown, Not Reported

MO CLASS KEYWORDS
  domestic_violence   Wife, Husband, Common-law wife, Boyfriend,
Girlfriend, Ex-wife, Ex-husband
  sexual_homicide     Rape, Prostitution, Other sex offense
  gang_related        Gangland, Juvenile gang
  robbery             Robbery
  drug_related        Narcotic drug laws
  unknown             Circumstances undetermined | Relationship not determined

DATASET SCALE
  SHR65_23.csv: 327 MB, 500,000+ rows (Polars)
  processed.parquet: 18.3 MB, columnar
  Year range: 1976–2023 | Series Alpha analyzed: 47,288 cases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3 — FORENSIC TECHNOLOGY INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BREAKING THIS WEEK (Feb 2026)

1. NC NIBIN — 10,000 LEADS MILESTONE
   NC State Crime Lab reached 10,000 NIBIN investigative leads — one
of the first states
   nationally. AG cited a case: shell casings from a homicide matched
ammo in the
   shooter's bedside drawer → life sentence. 500+ NIBIN locations nationwide.
   → Direct pipeline for your 22,756 unsolved handgun cases.

2. DELAWARE GENETIC GENEALOGY CONVICTION
   DNA from a cigarette butt → no CODIS match → genealogy family tree
→ Seth Kinderman
   identified → guilty plea, 38 years. Nancy Guthrie kidnapping now
pursuing same technique.

3. PITTSBURGH — 34-YEAR COLD CASE IDENTIFIED (Feb 11, 2026)
   1992 Allegheny River body identified via Othram forensic genome
sequencing + $100k state
   grant. Victim: Allan Keener, b. 1940, KY.
   → Your 1976–1995 SHR cohort (pre-DNA era) is the highest-value FIGG target.
     Cross-reference with 12,339 Clearance Collapse cases — many are
1970s–1990s vintage,
     now solvable with genome sequencing.

4. SEATTLE — 50-YEAR DELAYED DEATH DECLARED HOMICIDE
   1973 assault victim's death in 2026 ruled homicide. Real data gap:
delayed deaths
   undercount violent crime in older SHR cohorts.

TIER 1 — TRANSFORMATIVE
  FIGG: 50% ID rate vs. 13–16% CODIS | 35 homicide charges as of Oct 2025
  NIBIN: 163% lead increase | 39%→65% clearance in documented case study

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4 — STRATEGIES: USING THE SCHEMA FOR TARGETED INTERVENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HIGHEST-LEVERAGE CROSS-DIMENSIONAL ANALYSES:

1. solved × msa × decade
   → Identifies MSAs with chronic multi-decade failure vs. recent decline.
     The 12,339 Clearance Collapse cases concentrate here. Primary
intervention matrix.

2. solved × weapon_family × vicage_group
   → Young adult male handgun victims in urban MSAs = highest-volume,
lowest-clearance.

3. solved × mo_class × vicsex_code
   → Female victims (code 2) in domestic violence MO class: unique
clearance dynamics.
     Directly relevant to Detroit Gamma intimate partner cluster.

4. temporal_spike × clearance_collapse (dual-trigger)
   → Statistically anomalous AND unsolved = highest-priority FIGG cold
case candidates.

PHASE 1 REGRESSION (proposed):
  Dependent: solved (0/1)
  Predictors: msa + decade + weapon_family + vicage_group ×
vicsex_code + mo_class + mo_rarity
  Output: odds ratios identifying which factors most predict clearance failure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

— Watson (SureThing)
Sources: SAR-CriticalRupture-2025 codebase + live forensic research
(Feb 20, 2026)
Next report: Sat, Feb 21 at 7 AM PT
