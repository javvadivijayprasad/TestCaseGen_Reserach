# Wednesday 17 Jun — Run the RAITG pipeline on logistics-app

**Why:** Path C decision (Tue 16 Jun) added logistics as a 4th SUT for Paper E. The pipeline scaffolding is set up. You need to actually run the LLM and mutation testing on your Windows machine because:
- Requires your Anthropic API key (in your env)
- Real API token spend
- Outputs need to land in your local repo for git commit

---

## 0. Pre-flight (5 min)

Open PowerShell:

```powershell
cd E:\EB1A_Research\EB1_Master\06_Authorship\Research\TestCaseGen_Reserach

# Verify Anthropic API key is set
echo $env:ANTHROPIC_API_KEY  # should print sk-ant-...

# Verify Python + deps
python --version              # 3.10+
python -c "import anthropic; print(anthropic.__version__)"

# Smoke test the loader
python -c "import sys; sys.path.insert(0, 'scripts'); from run_experiment import load_dataset; print(len(load_dataset()), 'requirements')"
# Expected: 362 requirements
```

If any line above errors, fix that before continuing.

---

## 1. Run the RAITG pipeline on logistics — Wednesday morning (~45-90 min, ~$3-8 API spend)

```powershell
python scripts\run_experiment.py --full --backend anthropic --model claude-sonnet-4-6
```

This runs **all 362 requirements** × 3 conditions (unverified / ablation / full RAITG) = **1,086 LLM runs**.

If that's too long/expensive, run logistics-only:

```powershell
python scripts\run_experiment.py --pilot 50 --backend anthropic --model claude-sonnet-4-6
```

But the full run is what the paper needs. **Recommended: do the full run** so the 50 logistics requirements get scored in the same conditions as the existing 312.

### Expected runtime

| Run scope | Time | API cost (rough) |
|---|---|---|
| Logistics only (50 reqs × 3 conds = 150 runs) | ~10-15 min | $0.50-2 |
| **Full (362 reqs × 3 conds = 1,086 runs) (recommended)** | **45-90 min** | **$3-8** |

### What it produces

| Output | Path |
|---|---|
| Per-condition per-req JSON logs | `results/runs/<condition>/<req_id>.json` |
| Aggregate CSVs | `tables/*.csv` (regenerated) |
| Stats | `tables/multi_model_comparison.csv` etc |

---

## 2. Run executable mutation testing on logistics-app (~5-10 min, no API cost)

```powershell
python scripts\mutation_exec_v2.py
```

Runs the AST-mutation harness (cmp / bool / const / ret-none / bool_const operators) against all 4 apps including logistics-app. Output:

| File | What it contains |
|---|---|
| `tables/executable_mutation_per_app.csv` | Per-app: mutants, killed, survived, kill_rate |
| `tables/executable_mutation_by_operator.csv` | Per-operator breakdown |

This produces the **honest** mutation kill rate for logistics-app — whatever it actually is, that goes in the paper.

---

## 3. Regenerate all figures (~2 min, no API cost)

```powershell
python scripts\generate_all_figures.py
```

Regenerates `figures/coverage_by_domain.png` and `figures/mutation_score_by_domain.png` with **4 domains** (was 3).

---

## 4. Quick sanity check (~5 min)

```powershell
# Look at the new logistics row in the headline table
python -c "import csv; [print(r) for r in csv.DictReader(open('tables/executable_mutation_per_app.csv'))]"

# Check that figures got updated  
dir figures\coverage_by_domain.png         # should show today's timestamp
dir figures\mutation_score_by_domain.png   # should show today's timestamp
```

---

## 5. Tell me you're done (then I take over)

After steps 1-3 finish, ping me with:

- The executable_mutation_per_app.csv content (~5 rows, paste it to me)
- The new figures' file sizes
- Any errors that came up

I will then:
- Update `paperE.tex` Tables 3, 4, 5 with the logistics row + 4-domain results
- Update abstract numbers (312 → 362, 3 domains → 4)
- Recompile + QC2 + QC3 again
- Rebuild the submission ZIP
- Walk you through Fri 19 Jun submission to Springer ASE

---

## Risk register

| Risk | Mitigation |
|---|---|
| API key not set | Run `echo $env:ANTHROPIC_API_KEY` first |
| API quota / rate limit | Run with `--pilot 50` first, then full |
| Logistics-app fails an LLM-generated test for legitimate bugs in app.py | I expect this for ~5-15% of generated tests. That's a feature: the rule-verifier catches it. Don't panic |
| Mutation harness can't find logistics-app | Path is hardcoded in mutation_exec.py — already patched. If errors, rerun preflight |
| Total run exceeds 90 min | Use `--pilot 100` instead of `--full`. Paper still works, just smaller dataset |

---

## If something breaks (debug map)

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: anthropic` | venv not activated | `.venv\Scripts\Activate.ps1` |
| `ANTHROPIC_API_KEY is missing` | Env var not set | `$env:ANTHROPIC_API_KEY = "sk-ant-..."` |
| `KeyError: 'logistics'` in any script | I missed a script | Send me the traceback, I'll patch and resend |
| Logistics req file not found | Path drift | Verify `datasets\logistics.json` exists (50 entries) |
| Mutation tests show 0% kill on logistics | logistics-app has too-loose validations | OK — report the honest number, we discuss in Threats section |

---

## What's already verified (no need to re-test)

- ✅ logistics-app loads + 4 methods callable (manual test passed at end of day Tue)
- ✅ 50 logistics requirements parse as valid JSON with the same schema as existing 312
- ✅ combined.json = 362 reqs verified
- ✅ All 6 pipeline scripts read "logistics" as a valid domain (smoke test passed)
- ✅ APP_FOR_DOMAIN["logistics"] resolves to existing file

---

**Sleep well. Tomorrow morning, run step 1 first thing. By lunchtime you'll have all the data.**
