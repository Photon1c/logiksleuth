# MAP - Add-Ons Core Engine

These scripts are for educational and research use.

The datasets used are open data (publicly accessible), but may have their own licenses/terms—review and comply.

The PII screening layer defaults to a strict, privacy-first policy (deny by default). Loosening controls must be an explicit, documented choice (e.g., for LEA environments).

Limitations stem from avoiding paywalled or restricted sources; coverage and freshness may vary.

🕵 Instructions

```powershell
# Mock data (optional, deterministic)
python -m mock_data_generator --seed 42

# Convert UCR codes → normalized JSONL (example path)
python -m ucr_adapter .\data\raw_ucr.csv -o .\data\ucr_incidents.jsonl

# Quickcheck (LLM off by default here)
$env:LLM_MODE='off'
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --show 3 --heartbeat 10000
```

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
python -m mock_data_generator --seed 42
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
  - Default comes from `policies.yaml` → `classifier.model` (pinned recommended: `gpt-4o-mini-2025-05-xx`)
  - Override: set `LLM_CLASSIFIER_MODEL` (e.g., `gpt-4o-mini-2025-05-xx`)

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
$env:LLM_CLASSIFIER_MODEL='gpt-4o-mini-2025-05-xx'
$env:LLM_MAX_TOKENS='2000'
Remove-Item .llm_budget.log -ErrorAction SilentlyContinue
python -m ingest_quickcheck .\data\ucr_incidents.sample.jsonl --max-records 200 --show 2 --heartbeat 100
```

Tip: switch back to no-spend mode any time with `LLM_MODE=off`.


## Preprocessing pipeline (what happens to records)

1) Status resolution → `active | closed | unknown`
2) PII scan (regex-based) → risk score and matches
3) Active cases: minimization (drop sensitive fields, add `week_band`, coarsen geo)
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

Hangs or slow runs → use `--heartbeat`, limit with `--max-records`, or `--bisect` to find poison rows (exit 2).
Model 404/401 → 404: invalid model (use a pinned name like `gpt-4o-mini-2025-05-xx`); 401: check `OPENAI_API_KEY`.
Budget exceeded → increase `LLM_MAX_TOKENS` or remove `.llm_budget.log`.
BOM/encoding → reader uses `utf-8-sig`; re-run the command.

Log hygiene: Do not log raw prompts or PII. Only usage counts/totals are logged.

Exit codes: 0 success, 2 poison row found via `--bisect`, 78 config/env error.

## Licensing & Data Terms

- Code license: see `LICENSE`.
- Datasets: treat as open data with separate licenses/terms. Create and maintain a simple provenance table for your sources.
 - All data documentation and downloads are consolidated here: [MAP Data & Docs](https://www.murderdata.org/p/data-docs.html).

### Data Provenance (example)

| Source                       | URL                                                           | Accessed    | License/Terms        | Refresh |
|------------------------------|---------------------------------------------------------------|-------------|----------------------|---------|
| UCR-derived incidents (demo) | https://www.murderdata.org/p/data-docs.html                  | 2025-08-17  | Public (see site)    | Ad hoc  |

## Lean schema for `ucr_incidents.jsonl`

| Field        | Type         | Notes                                   |
|--------------|--------------|-----------------------------------------|
| case_status  | active/closed/unknown | Minimalized downstream for active |
| date         | ISO date     | e.g., 2021-05-12                        |
| state, county| string       | Trimmed/normalized                       |
| geo_precision| state/county/hex7 | Coarsened geo for privacy           |
| mo_tags      | array<string>| Curated minimal MO tags                  |
| access       | research/restricted | Assigned by pipeline              |
| linkable     | bool         | True only if safe to cross-ref           |

## Safety posture

Defaults are non-linkable, county-level or coarser geo, and rules-only routing. Enabling linkability or finer geo should be a conscious, documented decision (e.g., via policy profile and review).

Misuse policy: no doxxing or targeting individuals. Research/ethics first.

## Eagle Scanner (watchlist discovery)

Find ACTIVE hotspots by state/county to seed watchlists:

```powershell
python -m eagle_scanner .\data\ucr_incidents.sample.jsonl --recent-year 2015 --top 15
python -m eagle_scanner .\data\ucr_incidents.sample.jsonl --year-range 2010-2015 --top 15
python -m ingest_quickcheck .\data\ucr_incidents.jsonl --from-year 2020 --show 3 --top-restricted 10 --heartbeat 10000

Notes:
- `--recent-year` is an inclusive lower bound (same as `--from-year`).
```

It prints top states and counties since the given year and shows copy‑paste
environment suggestions for:
- `CLASSIFIER_FORCE_REVIEW_STATES`
- `CLASSIFIER_WATCHLIST_COUNTIES`
- `CLASSIFIER_RECENT_YEAR`


- 404 Not Found from OpenAI → model name invalid; set a valid `LLM_CLASSIFIER_MODEL` (e.g., `gpt-5`)
- 401 Unauthorized → check `OPENAI_API_KEY`
- Budget exceeded → either increase `LLM_MAX_TOKENS` or remove `.llm_budget.log`
- JSON BOM error → the reader now uses `utf-8-sig`; re-run the command