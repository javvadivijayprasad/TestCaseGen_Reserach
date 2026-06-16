# Git commit plan — Paper E v2 (logistics-app + 362 reqs + 4-SUT mutation)

**Date:** 2026-06-17
**Target:** push to https://github.com/javvadivijayprasad/TestCaseGen_Reserach (main)

---

## What we're committing

**4 new files / dirs:**
1. `repo/logistics-app/` — new SUT (192 LOC Python)
2. `datasets/logistics.json` — 50 new NL requirements
3. `WEDNESDAY_RUN.md` — handoff doc
4. `results/tables/` — fresh tables dir from run

**17 meaningful modifications:**
- `datasets/combined.json` — 312 → 362 reqs
- `scripts/baseline_tests.py` — hr-app password fix + run_logistics_tests
- `scripts/run_experiment.py` — DOMAINS + APP_FOR_DOMAIN + label dict
- `scripts/mutation_exec.py` — DOMAINS + APP_FOR_DOMAIN
- `scripts/mutation_exec_v2.py` — APPS list
- `scripts/rescore.py` — DOMAINS + APP_FOR_DOMAIN + label dict
- `scripts/stats_analysis.py` — DOMAINS
- `scripts/generate_all_figures.py` — DOMAIN_LABELS + per-domain lists
- `tables/aggregate_results.csv` — 4 conditions × n=362
- `tables/per_domain_results.csv` — 4 domains
- `tables/executable_mutation_per_app.csv` — 4 apps
- `tables/executable_mutation_by_operator.csv` — 4 apps
- `tables/statistics.csv` — n=362 bootstrap CIs + paired tests
- `tables/bootstrap_confidence_intervals.csv`
- `tables/per_domain_significance.csv`
- `results/mutation_exec_v2.json` — 4-SUT results
- `results/model_provenance.json` — model snapshots

**~943 noisy modifications in `zenodo/dist/raitg-v1.0.0/`:**
The published v1.0.0 release artifacts got touched when run_experiment.py wrote run logs into the dist dir. These shouldn't be in the commit. **We'll revert these to HEAD before committing.**

---

## Run these commands in cmd

```cmd
cd E:\EB1A_Research\EB1_Master\06_Authorship\Research\TestCaseGen_Reserach
```

### Step 1: Revert the noise (don't commit modifications to v1.0.0 release)

```cmd
git checkout HEAD -- zenodo/dist/raitg-v1.0.0/
```

**Expected:** 0 output, just resets those 943 files back to their published state.

### Step 2: Verify what's staged

```cmd
git status --short
```

**Expected:** ~21 files (4 new + 17 modified) — NO `zenodo/dist/raitg-v1.0.0/` lines.

### Step 3: Stage everything

```cmd
git add datasets/logistics.json datasets/combined.json
git add repo/logistics-app/
git add scripts/baseline_tests.py scripts/run_experiment.py scripts/mutation_exec.py scripts/mutation_exec_v2.py scripts/rescore.py scripts/stats_analysis.py scripts/generate_all_figures.py
git add tables/
git add results/mutation_exec_v2.json results/model_provenance.json
git add results_haiku/tables/
git add results/tables/
git add figures/map_integration.png figures/rule_class_contribution.png
git add WEDNESDAY_RUN.md
git add papers/paperE/cover_letter.pdf
```

If you want a shorter version that catches everything:

```cmd
git add -A
git restore --staged zenodo/dist/raitg-v1.0.0/
```

(adds everything, then unstages the v1.0.0 release artifacts noise)

### Step 4: Commit

```cmd
git commit -m "Paper E v2: add logistics-app (4th SUT) + 50 new requirements + 4-SUT mutation testing" -m "" -m "- New repo/logistics-app/ (192 LOC Python service)" -m "- 50 logistics NL requirements (datasets/logistics.json) -> combined.json now 362 reqs" -m "- Updated baseline_tests.py: fixed hr-app password test (ValidPw1 -> ValidPw12 for >=10 chars), added run_logistics_tests + logistics-app branch in run_app" -m "- 7 pipeline scripts patched for 4-domain logistics" -m "- Pipeline ran end-to-end: 1086 LLM calls (362 reqs x 3 conditions)" -m "- Mutation testing: 4 SUTs aggregate 82.42% (logistics 81.01%)" -m "- Stats: full vs ablation verification +22.1pp Cohens d=0.65 p<0.0001 n=362" -m "- New per-domain results: logistics 100% coverage, 12.0% symbolic, 98.0% verification"
```

### Step 5: Push

```cmd
git push origin main
```

---

## After git push succeeds — tell me, then we:

1. Build Zenodo v2.0.0 ZIP (I do)
2. You upload to Zenodo as "New version" → get new version DOI
3. I update paperE.tex + cover_letter.tex with new version DOI
4. Rebuild submission ZIP
5. Walk through Springer EM submission

---

## If git push prompts for credentials

If you see "Username for 'https://github.com':" → enter `javvadivijayprasad`
If you see "Password for ...:" → use your Personal Access Token (not password)
  - If you don't have a PAT: https://github.com/settings/tokens → "Generate new token (classic)" → check "repo" → create → copy → paste here

---

## Sanity check before pushing

After step 3 (staged), run:

```cmd
git status --short
```

Expected output:
```
A  WEDNESDAY_RUN.md
A  datasets/logistics.json
A  repo/logistics-app/app.py
A  repo/logistics-app/__pycache__/...
A  results/tables/...
M  datasets/combined.json
M  scripts/baseline_tests.py
M  scripts/generate_all_figures.py
M  scripts/mutation_exec.py
M  scripts/mutation_exec_v2.py
M  scripts/rescore.py
M  scripts/run_experiment.py
M  scripts/stats_analysis.py
M  tables/aggregate_results.csv
M  tables/bootstrap_confidence_intervals.csv
M  tables/executable_mutation_by_operator.csv
M  tables/executable_mutation_per_app.csv
M  tables/per_domain_results.csv
M  tables/per_domain_significance.csv
M  tables/statistics.csv
... etc
```

**If you see anything starting with `M  zenodo/dist/raitg-v1.0.0/`, run step 1 again to revert that noise.**
