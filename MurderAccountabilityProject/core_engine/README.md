# MAP - Add-Ons Core Engine

These scripts are solely for educational and research purposes.

The data sets that they user are 100% open-source, making this repository open-source too.

The PII screening layer is strictly set until more lax parameters are set by users, such as law enforcement agencies (LEAs).

Any limitations of this project is largely due to working outside of paywalls and gatekeeped data access points.

🕵 Instructions

First, ingest the proper data inputs. If you do not have any available, run ```python mock_data_generator.py```.

Once input data has been created or saved in /data folder, run ```python ucr_converter.py``` to convert incident codes.

Then, run ```python ingest_quickcheck.py data/ucr_incidents.jsonl```, this should give output similar to the output below:

```
Total ingested: 1047185
Research Lake:   1047185
Restricted Vault:0
Quarantine:      0

== Research Lake (showing up to 3) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
2. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
3. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...

== Restricted Vault (showing up to 3) ==

== Quarantine (showing up to 3) ==

```

These scripts essentially aim to "clean" and weed out PII from the starting data set. The UCR dataset candidates meet all requirements to proceed with analysis. Future entries can be flagged and discarded per the logic diagram in this project's start ([located here](../media/golden_sparrow.png))


## Quickstart (safe, deterministic)

- Generate mock data if needed:
```powershell
python mock_data_generator.py
```

- Run a zero-spend preflight to see how many ACTIVE records would consult the LLM (no tokens used):
```powershell
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --estimate-llm --estimate-only
```

- Ingest a sample safely (LLM off), with small output:
```powershell
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --show 2 --top-restricted 5 --heartbeat 1000
```


## LLM usage: modes, budgets, and visibility

- Unified switch (one source of truth):
  - `LLM_MODE=off` → rules-only, no LLM calls
  - `LLM_MODE=estimate` → route as usual but never call the LLM
  - `LLM_MODE=on` → allow LLM calls (subject to budget and timeouts)

- Model selection:
  - Default comes from `policies.yaml` → `classifier.model` (current default: `gpt-5`)
  - Override: set `LLM_CLASSIFIER_MODEL` (e.g., `gpt-5`)

- Token budget (multi-process safe):
  - `LLM_MAX_TOKENS` caps total tokens; raises if exceeded
  - `LLM_BUDGET_FILE` (default `.llm_budget.log`) tracks cumulative usage (remove between runs if needed)

- Network timeout and retries:
  - The OpenAI client uses a hard timeout; calls fail fast rather than hanging

- Print effective config (no calls made):
```powershell
python -m agent_classifier --print-config
```


## Run with the LLM (tiny budget)

```powershell
$env:LLM_MODE='on'
$env:LLM_CLASSIFIER_MODEL='gpt-5'
$env:LLM_MAX_TOKENS='2000'
Remove-Item .llm_budget.log -ErrorAction SilentlyContinue
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --max-records 200 --show 2 --heartbeat 100
```

Tip: switch back to no-spend mode any time with `LLM_MODE=off`.


## Preprocessing pipeline (what happens to records)

1) Status resolution → `active | closed | unknown`
2) PII scan (regex-based) → risk score and matches
3) Active cases: minimalization (drop sensitive fields, add `week_band`, coarsen geo)
4) Rule-first routing for ACTIVE: recency, watchlisted counties, force-review states, and MO keywords
5) Optional LLM check (when `LLM_MODE=on`) for ACTIVE records that did not match rules
6) Sinks:
   - Research Lake (default for closed and most active after minimalization)
   - Restricted Vault (when rules/LLM decide review)
   - Quarantine (if high PII risk)


## Guardrails for large runs

- `--max-records N` → process only the first N records
- `--heartbeat N` → print a progress line every N records
- `--bisect` → stop on the first failing line, print index and traceback

Examples:
```powershell
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --max-records 1000 --heartbeat 200 --show 2
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --bisect --max-records 500
```


## Deterministic tests (avoid environment drift)

```powershell
$env:LLM_MODE='off'
$env:CLASSIFIER_MO_KEYWORDS=''
$env:CLASSIFIER_WATCHLIST_COUNTIES=''
$env:CLASSIFIER_FORCE_REVIEW_STATES=''
python -m pytest -q
```

Optionally neutralize recency:
```powershell
$env:LLM_MODE='off'
$env:CLASSIFIER_RECENT_YEAR='2100'
python -m pytest -q
```


## Troubleshooting

- 404 Not Found from OpenAI → model name invalid; set a valid `LLM_CLASSIFIER_MODEL` (e.g., `gpt-5`)
- 401 Unauthorized → check `OPENAI_API_KEY`
- Budget exceeded → either increase `LLM_MAX_TOKENS` or remove `.llm_budget.log`
- JSON BOM error → the reader now uses `utf-8-sig`; re-run the command
