# Homicide Clearance Risk Scan

**Generated:** 2025-09-30 22:22:38
**Filters:** csv=SHR65_23.csv, group=msa, focus_sex=female, threshold=0.33, min_total=10, min_decade=2010, solved_source=field

|   MURDGRP |   SEX | WEAPON_LABEL             |   TOTAL |   SOLVED | PERCENT   |   UNSOLVED | MSA_LABEL         |
|----------:|------:|:-------------------------|--------:|---------:|:----------|-----------:|:------------------|
|  52553518 |     2 | Firearm, type not stated |      47 |       15 | 31.9%     |         32 | Montgomery, AL    |
|  28744648 |     2 | Other or type unknown    |      17 |        5 | 29.4%     |         12 | Montgomery, AL    |
|  20901696 |     2 | Rifle                    |      10 |        3 | 30.0%     |          7 | Louisville, KY-IN |

## Analyst Insights
### Top by anomaly
- Montgomery, AL — Firearm, type not stated: UNSOLVED 32/47 (31.9%)
- Montgomery, AL — Other or type unknown: UNSOLVED 12/17 (29.4%)
- Louisville, KY-IN — Rifle: UNSOLVED 7/10 (30.0%)

### Top by unsolved
- Montgomery, AL — Firearm, type not stated: UNSOLVED 32/47 (31.9%)
- Montgomery, AL — Other or type unknown: UNSOLVED 12/17 (29.4%)
- Louisville, KY-IN — Rifle: UNSOLVED 7/10 (30.0%)

### Case-dump shortcuts (Windows)
`python map_cluster.py "SHR65_23.csv" --group msa --dump-msa "Montgomery, AL" --dump-weapon "Firearm, type not stated" --outdir out`
`python map_cluster.py "SHR65_23.csv" --group msa --dump-msa "Montgomery, AL" --dump-weapon "Other or type unknown" --outdir out`
`python map_cluster.py "SHR65_23.csv" --group msa --dump-msa "Louisville, KY-IN" --dump-weapon "Rifle" --outdir out`


## Map
Interactive per-ORI map: **[report_map.html](out\report_map.html)**