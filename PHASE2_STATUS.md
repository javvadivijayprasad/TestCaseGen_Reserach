# Paper E OSS Benchmark — Phase 2 Status

Date: 2026-08-19
Working dir: `paperE_oss_benchmark/`

## What ran successfully

**Step 2b — Cloning + verification** — DONE for all 4 SUTs.
- `sut3_flaskr/` cloned from `pallets/flask@examples/tutorial` via sparse
  checkout. `flaskr` package installed editable; **24/24 pytest green**.
- `sut4_fastapi_task_manager/` cloned from `lafarch/fastapi-task-manager`;
  requirements installed; **7/7 pytest green**.
- Existing `sut1_httpbin/` kept as-is (65/67 pytest green, 2 pre-existing
  Werkzeug incompatibilities).
- `sut2_fastapi_restful/` re-verified: 24/25 green (one pre-existing red
  case surfaced on this environment, `test_request_put_player_squadnumber
  _existing_response_status_no_content`).
- Old `sut3_fastapi_users_OLD_UNUSED/` and `sut4_flask_vue_crud_OLD_UNUSED/`
  archived (renamed) to preserve trace.

**Step 3 — Requirements corpus** — DONE, 172 requirements total.
Files at `requirements/sut<N>_..._requirements.json`, schema matches
`EB1_Master/06_Authorship/Research/TestCaseGen_Reserach/datasets/`
(id, domain, layer, category, title, statement, actors, preconditions,
triggers, expected_outcomes, error_pathways, target_app,
target_endpoint_or_screen).
Per SUT: 49 / 40 / 43 / 40. Below the 200-300 stretch goal by ~30, above
the per-SUT floor of 40.

**Step 4 — Mutation** — DONE, 293 mutants total.
Vijay's `scripts/mutation_exec_v2.py` was too RAITG-coupled to re-use
directly, so I wrote a stand-alone `scripts/generate_mutants.py` (~190
lines) that applies the exact same five operators (`cmp`, `bool`,
`const`, `ret-none`, `bool_const`) plus a `--allowed-ranges` filter
(used for the SUT 1 httpbin endpoint subset).
Per-SUT + operator breakdown lives in `BENCHMARK_MANIFEST.md`.
Frozen JSON at `mutants/sut<N>_mutants.json`.

**Step 5 — Manual baseline scoring** — DONE.
For every mutant: overwrite source, run `pytest --tb=no -q`, parse
`FAILED`/`ERROR` lines, subtract baseline failures, mark killed iff any
*new* failure appeared (or `TIMEOUT`). Source restored after each run,
including on exception paths.
Per-mutant results in `results/sut<N>_manual_baseline.csv`; aggregate in
`results/manual_baseline_summary.csv`.

## Real per-SUT Manual baseline kill rates (headline)

| # | SUT                          | Mutants | Killed | Kill rate |
|---|------------------------------|---------|--------|-----------|
| 1 | httpbin (scoped)             | 161     | 91     | **56.52 %** |
| 2 | fastapi-restful              |  46     | 15     | **32.61 %** |
| 3 | flaskr                       |  32     | 31     | **96.88 %** |
| 4 | fastapi-task-manager         |  54     | 16     | **29.63 %** |
| — | **Aggregate**                | 293     | 153    | **52.22 %** |

The spread is intentional and informative:
- **flaskr** (96.88 %) is the gold-standard tutorial suite — dense
  coverage of a tiny surface.
- **httpbin** (56.52 %) is respectable given the 65-test suite has to
  cover 640+ SLOC of scoped endpoints + helpers.
- **fastapi-restful** (32.61 %) leaves most schema mutants alive
  (`bool_const` swaps on Pydantic Config, unused `ret-none` in service
  methods) — tests don't exercise those code paths.
- **fastapi-task-manager** (29.63 %) has a 7-test smoke suite that
  can't hope to reach schema / model constant mutations.

## Blockers / caveats

1. **httpbin scoping choice.** Rather than extract a separate
   `scoped/httpbin_scoped.py` (which would have broken helper imports
   and forced a rewrite of `test_httpbin.py`), I kept the original file
   untouched and constrained mutation to the 14 endpoint line ranges in
   `core.py` (plus all of `helpers.py`, since the scoped endpoints
   exercise most helpers). Documented in `BENCHMARK_MANIFEST.md` under
   SUT 1.
2. **Two pre-existing red tests in each of SUT 1 (Werkzeug) and SUT 2
   (put_squadnumber).** These are filtered out of the baseline failure
   set so they never wrongly credit a mutant as "killed."
3. **pytest is expensive on httpbin (~7 s per invocation)** — 161
   mutants ran in nine ~2-minute bash-tool batches. Test selector `-k
   "..."` narrows to relevant test names (still ~all 65 tests) so the
   selector does not censor kills. Kill counts per batch aggregated in
   `results/sut1_batch<N>.csv` then merged into `sut1_manual_baseline.csv`.
4. **Requirement count 172 is under the 200-300 stretch goal** but each
   SUT is at or above the 40 floor. Padding further would produce
   low-information requirements; I stopped where the endpoints stopped
   generating natural statements.
5. **No mutants were unscorable / errored.** No AST syntax breakage, no
   timeouts recorded. The `errored` column in every SUT summary is 0.

## What's ready for Step 6 (RAITG)

- `requirements/sut<N>_*.json` — feed as-is to RAITG.
- `mutants/sut<N>_mutants.json` — the frozen mutant sets to score RAITG
  against.
- `scripts/score_mutants.py` — same scoring wrapper you can point at any
  new test suite; supports `--pytest-args` (shlex-parsed),
  `--sut-dir`, and `--start/--end` for batching.
- `results/manual_baseline_summary.csv` — Manual baseline column of the
  headline table.
- SUT dirs remain intact (no source corruption); backups verified.

You (Vijay) still need to:
- Point RAITG at each `requirements/sut<N>_*.json`.
- Save RAITG's generated tests into e.g. `raitg_tests/sut<N>/`.
- Run `python3 scripts/score_mutants.py --sut-dir <dir> --pytest-args
  "raitg_tests/sut<N>/"` to get the RAITG kill rate for the same 293
  mutants.
- Repeat with Sonnet vs. GPT-4o-mini (or whichever LLM pair the RAITG
  ablation calls for).

## File tree summary

```
paperE_oss_benchmark/
├── BENCHMARK_MANIFEST.md            (updated)
├── PHASE2_STATUS.md                 (this file)
├── sut1_httpbin/                    (unchanged clone; scoped for mutation)
├── sut2_fastapi_restful/            (unchanged clone)
├── sut3_flaskr/                     (new: pallets/flask examples/tutorial)
├── sut4_fastapi_task_manager/       (new: lafarch/fastapi-task-manager)
├── sut3_fastapi_users_OLD_UNUSED/   (archived)
├── sut4_flask_vue_crud_OLD_UNUSED/  (archived)
├── scripts/
│   ├── generate_mutants.py          (190 LOC AST mutator)
│   ├── score_mutants.py             (150 LOC pytest scorer)
│   └── build_requirements.py        (requirement seed data)
├── mutants/
│   ├── sut1_mutants.json  (161)
│   ├── sut2_mutants.json  (46)
│   ├── sut3_mutants.json  (32)
│   ├── sut4_mutants.json  (54)
│   └── (per-file split files also present)
├── requirements/
│   ├── sut1_httpbin_requirements.json               (49)
│   ├── sut2_fastapi_restful_requirements.json       (40)
│   ├── sut3_flaskr_requirements.json                (43)
│   └── sut4_fastapi_task_manager_requirements.json  (40)
└── results/
    ├── sut1_manual_baseline.csv     (161 rows)
    ├── sut2_manual_baseline.csv     (46 rows)
    ├── sut3_manual_baseline.csv     (32 rows)
    ├── sut4_manual_baseline.csv     (54 rows)
    ├── sut1_batch{1..9}.csv         (batch source files, kept for audit)
    ├── sut2_manual_baseline_p{1,2}.csv (batch source files)
    └── manual_baseline_summary.csv
```
