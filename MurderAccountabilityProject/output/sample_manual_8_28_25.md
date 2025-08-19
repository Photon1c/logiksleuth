```
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --estimate-llm --estimate-only
2025-08-17 16:07:01,223 INFO LLM classifier mode=off (no token spend)
LLM classifier mode=off: no token spend
```
Output:  

Preflight estimate (no LLM calls made):
  total records: 5000
  active records: 1516
  would consult LLM if enabled: 1408
  rule-trigger reasons:
    rules->watchlist_county: 108

```
 $env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --max-records 500 --heartbeat 100 --bisect --show 2 --top-restricted 5
2025-08-17 16:07:23,800 INFO LLM classifier mode=off (no token spend)
```

Output:  

LLM classifier mode=off: no token spend
... processed 100 records
... processed 200 records
... processed 300 records
... processed 400 records
... processed 500 records

Total ingested: 500
Research Lake:   500
Restricted Vault:0
Quarantine:      0

== Research Lake (showing up to 2) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
2. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 

== Restricted Vault (showing up to 2) ==

== Quarantine (showing up to 2) ==

Restricted routed by rules: 0
Restricted routed by LLM:   0

Breakdown (Research Lake):
  active: 168
  closed: 332
  linkable=True:  332
  linkable=False: 168

```
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --show 3 --top-restricted 10 --heartbeat 10000
```
Output:  


2025-08-18 18:51:11,247 INFO LLM classifier mode=off (no token spend)
LLM classifier mode=off: no token spend
... processed 10000 records
... processed 20000 records
... processed 30000 records
... processed 40000 records
... processed 50000 records
... processed 60000 records
... processed 70000 records
... processed 80000 records
... processed 90000 records
... processed 100000 records
... processed 110000 records
... processed 120000 records
... processed 130000 records
... processed 140000 records
... processed 150000 records
... processed 160000 records
... processed 170000 records
... processed 180000 records
... processed 190000 records
... processed 200000 records
... processed 210000 records
... processed 220000 records
... processed 230000 records
... processed 240000 records
... processed 250000 records
... processed 260000 records
... processed 270000 records
... processed 280000 records
... processed 290000 records
... processed 300000 records
... processed 310000 records
... processed 320000 records
... processed 330000 records
... processed 340000 records
... processed 350000 records
... processed 360000 records
... processed 370000 records
... processed 380000 records
... processed 390000 records
... processed 400000 records
... processed 410000 records
... processed 420000 records
... processed 430000 records
... processed 440000 records
... processed 450000 records
... processed 460000 records
... processed 470000 records
... processed 480000 records
... processed 490000 records
... processed 500000 records
... processed 510000 records
... processed 520000 records
... processed 530000 records
... processed 540000 records
... processed 550000 records
... processed 560000 records
... processed 570000 records
... processed 580000 records
... processed 590000 records
... processed 600000 records
... processed 610000 records
... processed 620000 records
... processed 630000 records
... processed 640000 records
... processed 650000 records
... processed 660000 records
... processed 670000 records
... processed 680000 records
... processed 690000 records
... processed 700000 records
... processed 710000 records
... processed 720000 records
... processed 730000 records
... processed 740000 records
... processed 750000 records
... processed 760000 records
... processed 770000 records
... processed 780000 records
... processed 790000 records
... processed 800000 records
... processed 810000 records
... processed 820000 records
... processed 830000 records
... processed 840000 records
... processed 850000 records
... processed 860000 records
... processed 870000 records
... processed 880000 records
... processed 890000 records
... processed 900000 records
... processed 910000 records
... processed 920000 records
... processed 930000 records
... processed 940000 records
... processed 950000 records
... processed 960000 records
... processed 970000 records
... processed 980000 records
... processed 990000 records
... processed 1000000 records
... processed 1010000 records
... processed 1020000 records
... processed 1030000 records
... processed 1040000 records

Total ingested: 1047185
Research Lake:   1031207
Restricted Vault:15978
Quarantine:      0

== Research Lake (showing up to 3) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
2. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
3. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...

== Restricted Vault (showing up to 3) ==
1. status=active, access=research, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...
2. status=active, access=research, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...
3. status=active, access=research, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...

== Quarantine (showing up to 3) ==

Restricted routed by rules: 15978
Restricted routed by LLM:   0

Top Restricted by county (top 10):
  Cook: 4175
  Los Angeles: 2518
  Harris: 1993
  Philadelphia: 1961
  Jefferson: 1800
  Baltimore city: 1792
  Wayne: 1739

Top Restricted by state (top 10):
  Illinois: 4183
  California: 2518
  Texas: 2076
  Pennsylvania: 1969
  Maryland: 1792
  Michigan: 1662
  Kentucky: 709
  Alabama: 638
  Louisiana: 145

Top review_reason in Restricted (top 10):
  recent>= 2015 & watchlist_county=cook: 4175
  recent>= 2015 & watchlist_county=los angeles: 2518
  recent>= 2015 & watchlist_county=harris: 1993
  recent>= 2015 & watchlist_county=philadelphia: 1961
  recent>= 2015 & watchlist_county=jefferson: 1800
  recent>= 2015 & watchlist_county=baltimore city: 1792
  recent>= 2015 & watchlist_county=wayne: 1739

Breakdown (Research Lake):
  active: 345254
  closed: 685953
  linkable=True:  685953
  linkable=False: 345254

```
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --from-year 2015 --show 3 --top-restricted 15 --heartbeat 10000
```
2025-08-18 21:16:53,664 INFO LLM classifier mode=off (no token spend)
LLM classifier mode=off: no token spend
... processed 130000 records
... processed 140000 records
... processed 200000 records
... processed 230000 records
... processed 250000 records
... processed 340000 records
... processed 540000 records
... processed 600000 records
... processed 640000 records
... processed 740000 records
... processed 770000 records
... processed 800000 records
... processed 840000 records
... processed 850000 records
... processed 960000 records
... processed 980000 records
... processed 1020000 records
... processed 1040000 records

Total ingested: 1047185
Research Lake:   151391
Restricted Vault:15978
Quarantine:      0
Processed 1,047,185 in 23.5s (~44,575 rec/s)

== Research Lake (showing up to 3) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
2. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
3. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...

== Restricted Vault (showing up to 3) ==
1. status=active, access=restricted, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...
2. status=active, access=restricted, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...
3. status=active, access=restricted, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...

== Quarantine (showing up to 3) ==

Restricted routed by rules: 15978
Restricted routed by LLM:   0

Top Restricted by county (top 15):
  Cook: 4175
  Los Angeles: 2518
  Harris: 1993
  Philadelphia: 1961
  Jefferson: 1800
  Baltimore city: 1792
  Wayne: 1739

Top Restricted by state (top 15):
  Illinois: 4183
  California: 2518
  Texas: 2076
  Pennsylvania: 1969
  Maryland: 1792
  Michigan: 1662
  Kentucky: 709
  Alabama: 638
  Louisiana: 145
  Arkansas: 131
  North Carolina: 37
  Colorado: 25
  New York: 19
  Georgia: 13

Top review_reason in Restricted (top 15):
  recent>= 2015 & watchlist_county=cook: 4175
  recent>= 2015 & watchlist_county=los angeles: 2518
  recent>= 2015 & watchlist_county=harris: 1993
  recent>= 2015 & watchlist_county=philadelphia: 1961
  recent>= 2015 & watchlist_county=jefferson: 1800
  recent>= 2015 & watchlist_county=baltimore city: 1792
  recent>= 2015 & watchlist_county=wayne: 1739

Breakdown (Research Lake):
  closed: 93882
  linkable=True:  93882
  linkable=False: 57509

 python -m eagle_scanner .\data\ucr_incidents.jsonl --year-range 2018-2025 --top 20

Scanned: 1,047,185 records | ACTIVE 2018-2025: 51,931

Top states (ACTIVE):
  California    5,111
  Texas    4,631
  Illinois    3,749
  Florida    2,578
  Ohio    2,520
  Pennsylvania    2,506
  Michigan    2,002
  Louisiana    1,989
  Georgia    1,966
  North Carolina    1,878
  Tennessee    1,840
  Maryland    1,725
  Missouri    1,581
  Indiana    1,549
  New York    1,484
  Virginia    1,259
  Alabama    1,050
  South Carolina    1,032
  Arizona      841
  New Mexico      841

Top counties (ACTIVE):
  Cook                        2,722
  Los Angeles                 1,756
  Philadelphia                1,517
  Harris                      1,460
  Jefferson                   1,368
  Baltimore city              1,190
  Wayne                       1,070
  Shelby                      1,046
  Marion                        904
  Cuyahoga                      765
  Orleans                       693
  District of Columbia          680
  St. Louis city                666
  Miami-Dade                    644
  New York                      633
  Franklin                      605
  Bexar                         589
  Duval                         543
  Jackson                       534

```
set CLASSIFIER_FORCE_REVIEW_STATES=California,Texas,Illinois,Florida,Ohio,Pennsylvania,Michigan,Louisiana,Georgia,North Carolina,Tennessee,Maryland,Missouri,Indiana,New York,Virginia,Alabama,South Carolina,Arizona,New Mexico
set CLASSIFIER_WATCHLIST_COUNTIES=Cook,Los Angeles,Philadelphia,Harris,Jefferson,Baltimore city,Wayne,Shelby
set CLASSIFIER_RECENT_YEAR=2018
```
```
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --from-year 2015 --show 1 --top-restricted 10
```

Output:  

2025-08-18 21:21:55,268 INFO LLM classifier mode=off (no token spend)
LLM classifier mode=off: no token spend

Total ingested: 1047185
Research Lake:   151391
Restricted Vault:15978
Quarantine:      0
Processed 1,047,185 in 14.8s (~70,679 rec/s)

== Research Lake (showing up to 1) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 
'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...

== Restricted Vault (showing up to 1) ==
1. status=active, access=restricted, linkable=False, geo=hex7, keys=['access', 'case_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags', 'pii_risk']...

== Quarantine (showing up to 1) ==

Restricted routed by rules: 15978
Restricted routed by LLM:   0

Top Restricted by county (top 10):
  Cook: 4175
  Los Angeles: 2518
  Harris: 1993
  Philadelphia: 1961
  Jefferson: 1800
  Baltimore city: 1792
  Wayne: 1739

Top Restricted by state (top 10):
  Illinois: 4183
  California: 2518
  Texas: 2076
  Pennsylvania: 1969
  Maryland: 1792
  Michigan: 1662
  Kentucky: 709
  Alabama: 638
  Arkansas: 131

Top review_reason in Restricted (top 10):
  recent>= 2015 & watchlist_county=cook: 4175
  recent>= 2015 & watchlist_county=los angeles: 2518
  recent>= 2015 & watchlist_county=harris: 1993
  recent>= 2015 & watchlist_county=philadelphia: 1961
  recent>= 2015 & watchlist_county=jefferson: 1800
  recent>= 2015 & watchlist_county=baltimore city: 1792
  recent>= 2015 & watchlist_county=wayne: 1739

Breakdown (Research Lake):
  active: 57509
  closed: 93882
  linkable=True:  93882
  linkable=False: 57509

```
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --from-year 2023 --estimate-llm --estimate-only
```

Output:  

2025-08-18 21:22:37,114 INFO LLM classifier mode=off (no token spend)
LLM classifier mode=off: no token spend

Preflight estimate (no LLM calls made):
  total records: 1047185
  active records: 361232
  would consult LLM if enabled: 6443
  rule-trigger reasons:
    rules->watchlist_county: 1782

```
##LLM Mode On
#Tiny-budget LLM sanity (observe usage logs, then stop)
$env:LLM_MODE='on'
$env:LLM_CLASSIFIER_MODEL='gpt-4o-mini-2025-05-xx'
$env:LLM_MAX_TOKENS='200'
Remove-Item .llm_budget.log -ErrorAction SilentlyContinue
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --max-records 200 --show 1 --heartbeat 50
# Expect: usage totals printed; budget enforced. Switch back to off after.
```
