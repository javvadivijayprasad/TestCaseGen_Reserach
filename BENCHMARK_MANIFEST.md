# Paper E OSS Benchmark — 4 SUTs Manifest (FINAL — Phase 2)

Generated: 2026-08-18 (Phase 1), Updated: 2026-08-19 (Phase 2).

All numbers below come from actual `wc -l`, `grep -vE '^\s*($|#)'` (SLOC),
`grep -crE '^(async )?def test_'` (test counts), and `python3 -m pytest`
runs executed against the freshly cloned trees under
`/sessions/eloquent-nifty-johnson/mnt/outputs/paperE_oss_benchmark/`.

---

## SUT 1 — httpbin

- **Upstream:** https://github.com/postmanlabs/httpbin
- **License:** ISC (verified from `sut1_httpbin/LICENSE`; note the
  `setup.py` reads `MIT` inconsistently — flag for citation).
- **Clone path:** `paperE_oss_benchmark/sut1_httpbin/`
- **Full core SLOC (untouched clone):** 1,998 SLOC
- **Scoped subset for mutation:** endpoint routes plus `helpers.py`.
  The scoped endpoint set is:
  `/get`, `/post`, `/put`, `/patch`, `/delete`, `/status/<code>`,
  `/headers`, `/basic-auth/<user>/<passwd>`, `/redirect/<n>`,
  `/redirect-to`, `/cookies`, `/cookies/set`, `/cookies/set/<n>/<v>`,
  `/cookies/delete`.
  - `core.py` line ranges mutated (14 route handlers): 333-345, 367-379,
    415-429, 433-447, 451-465, 469-483, 538-563, 573-644, 732-777,
    825-846, 857-879, 883-910, 914-941, 945-969 (≈356 lines).
  - `helpers.py` (372 SLOC) mutated in full because these endpoints
    exercise nearly all helper paths.
  - **Effective scoped SLOC:** ≈ 640 (356 core routes + ~285 helpers used).
- **Tests:** `test_httpbin.py` — 67 tests; **65 / 67 passing**
  (2 pre-existing `KeyError: 'Content-Length'` failures — Werkzeug 2.0.x
  omits `Content-Length` under test client for `/get` and `/anything`).
- **Test selector used for scoring:** `-k "get or post or put or patch or
  delete or headers or status or redirect or basic_auth or cookies or
  bearer or digest or gzip or drip or brotli or forwarded or ip or uuid
  or anything or stream or response_headers or relative or absolute or
  deny or html or bytes or etag or range or forms or user_agent or cors
  or index or robots or base64 or xml"` (matches virtually all tests but
  keeps each pytest invocation ~7 s versus ~12 s otherwise).
- **Mutants generated:** **161** (49 core + 112 helpers) across cmp, bool,
  const, ret-none, bool_const families.
- **Manual baseline kill rate:** **91 / 161 = 56.52 %**.

---

## SUT 2 — fastapi-restful (nanotaboada)

- **Upstream:** https://github.com/nanotaboada/python-samples-fastapi-restful
- **License:** MIT.
- **Clone path:** `paperE_oss_benchmark/sut2_fastapi_restful/`
- **Core SLOC:** 643 (routes + services + models + schemas + db + main).
- **Tests:** `tests/test_main.py` (22) + `tests/test_migrations.py` (3)
  = **25 tests total**.  **24 / 25 passing** after the fresh
  `pip install -r requirements.txt` — the migrations test file has one
  pre-existing red case that occurred on this environment
  (`test_request_put_player_squadnumber_existing_response_status_no_content`).
- **Mutants generated:** **46** (11 route + 18 service + 2 model +
  15 schema).
- **Manual baseline kill rate:** **15 / 46 = 32.61 %**
  (13 route/service + 2 schema killed; models untouched by tests).

---

## SUT 3 — flaskr (Pallets tutorial)

- **Upstream:** https://github.com/pallets/flask (subtree
  `examples/tutorial`, cloned via sparse-checkout).
- **License:** BSD-3-Clause (`sut3_flaskr/LICENSE`).
- **Clone path:** `paperE_oss_benchmark/sut3_flaskr/`
- **Core SLOC:** 251 across `flaskr/__init__.py` (25), `auth.py` (86),
  `blog.py` (100), `db.py` (40).
- **Tests:** `tests/` — 24 tests across `test_auth.py`, `test_blog.py`,
  `test_db.py`, `test_factory.py`. **24 / 24 passing** in ~3 s.
- **Mutants generated:** **32** (10 auth + 16 blog + 1 db + 5 factory).
- **Manual baseline kill rate:** **31 / 32 = 96.88 %** — the canonical
  Flaskr suite is famously thorough.

---

## SUT 4 — fastapi-task-manager (lafarch)

- **Upstream:** https://github.com/lafarch/fastapi-task-manager
- **License:** MIT (`sut4_fastapi_task_manager/LICENSE`).
- **Clone path:** `paperE_oss_benchmark/sut4_fastapi_task_manager/`
- **Core SLOC:** 196 across `app/main.py` (96), `crud.py` (51),
  `schemas.py` (23), `models.py` (12), `database.py` (17).
- **Tests:** `tests/test_main.py` — **7 tests, 7 / 7 passing** in ~2 s.
- **Mutants generated:** **54** (16 main + 16 crud + 14 schemas +
  8 models).
- **Manual baseline kill rate:** **16 / 54 = 29.63 %** — the small
  smoke-test suite is weak against mutants inside schemas and models.

---

## Aggregate summary — MANUAL BASELINE (Step 5)

| # | SUT                      | LOC  | Tests | Green?     | Mutants | Killed | Kill rate |
|---|--------------------------|------|-------|------------|---------|--------|-----------|
| 1 | httpbin (scoped)         | ~640 | 67    | 65/67      | 161     | 91     | **56.52 %** |
| 2 | fastapi-restful          | 643  | 25    | 24/25      | 46      | 15     | **32.61 %** |
| 3 | flaskr                   | 251  | 24    | 24/24      | 32      | 31     | **96.88 %** |
| 4 | fastapi-task-manager     | 196  | 7     | 7/7        | 54      | 16     | **29.63 %** |

**Aggregate Manual baseline:** 153 / 293 = **52.22 %**.

Files:
- Per-mutant CSV: `results/sut<N>_manual_baseline.csv`
  (columns: `mutant_id, operator, file, line, killed, failing_tests`).
- Summary CSV: `results/manual_baseline_summary.csv`.

---

## Requirements corpus (Step 3)

| SUT | File | Count |
|---|---|---|
| 1 | `requirements/sut1_httpbin_requirements.json` | 49 |
| 2 | `requirements/sut2_fastapi_restful_requirements.json` | 40 |
| 3 | `requirements/sut3_flaskr_requirements.json` | 43 |
| 4 | `requirements/sut4_fastapi_task_manager_requirements.json` | 40 |
| **Total** | | **172** |

Schema (id, domain, layer, category, title, statement, actors,
preconditions, triggers, expected_outcomes, error_pathways, target_app,
target_endpoint_or_screen) is identical to
`EB1_Master/06_Authorship/Research/TestCaseGen_Reserach/datasets/*.json`.

---

## Mutation operator distribution

Aggregated across all 4 SUTs:

| Operator     | Count |
|--------------|-------|
| cmp          | 27    |
| bool         | 11    |
| const        | 112   |
| ret-none     | 101   |
| bool_const   | 42    |
| **Total**    | **293** |

---

## Environment / caveats

- Python 3.10.12 on the shared workspace (no per-SUT venvs — all deps in
  `/sessions/.../.local/`).
- Werkzeug 2.0.x pinned for SUT 1 to preserve `from werkzeug.wrappers
  import BaseResponse`.
- SUT 2 uses latest FastAPI/SQLAlchemy despite pyproject asking for
  Python ≥3.13 — pins are advisory.
- SUT 3 installed as editable via `pip install -e .` (needed for pytest
  to pick up `flaskr`).
- SUT 4 uses `fastapi[standard]≥0.115` from `requirements.txt`.
- Scoring wrapper: `scripts/score_mutants.py`; generator:
  `scripts/generate_mutants.py`.
