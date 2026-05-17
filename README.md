# Test Case Generation Research (Paper 4)

Fourth paper in the AI-augmented software quality engineering research series. Addresses LLM-driven test case generation with structured prompt engineering and rule-based verification.

## Deliverables

### Paper

- **Canonical LaTeX source:** `test_case_generation_paper.tex` — IEEE conference class (`IEEEtran`). Compile on Windows / MiKTeX / TeX Live with `texlive-publishers`.
- **Build:** run `compile_all.bat` (Windows) or `pdflatex -interaction=nonstopmode test_case_generation_paper.tex` three times.
- **Preview (non-IEEE):** `scripts/build_preview.py` produces `test_case_generation_paper_preview.pdf` using the plain `article` class for environments without `IEEEtran.cls`. Not the submission artefact — use the canonical build for final PDFs.

### Experiment (Track B)

- **Dataset:** `datasets/{commercial_web,financial_services,healthcare,combined}.json` — 312 requirements. Regenerated via `python scripts/generate_requirements.py`.
- **Reference apps for mutation testing:** `repo/hr-app`, `repo/banking-api`, `repo/fhir-lite` — small, runnable Python apps covering the three domains.
- **Pipeline:** `scripts/run_experiment.py` — end-to-end orchestrator that runs 3 conditions (unverified / ablation / full) across all 312 requirements, verifies, scores mutation detection, and writes the paper's CSV tables.
- **Supporting modules:** `scripts/prompts.py` (5-element taxonomy), `scripts/verify.py` (4-class rule calculus), `scripts/mutation.py` (mutation engine + symbolic scoring), `scripts/llm_adapter.py` (Claude adapter + deterministic stub).

### Service (Track C)

The framework is productised as a sibling microservice under `../test-case-generation-service/` (peer to `test-prioritization-service`). See that folder's README for run instructions.

### Platform integration (Track C)

Scaffolded in `../../API/modern-automation-platform/`:
- Backend proxy route: `apps/framework-generator-api/src/routes/test-case-generation.routes.ts`
- UI page: `apps/platform-ui/src/app/test-case-generator/page.tsx`
- UI wizard component: `apps/platform-ui/src/components/test-case-generator/TestCaseGeneratorWizard.tsx`
- Integration checklist: `apps/framework-generator-api/src/routes/INTEGRATION_NOTES_test_case_generator.md`

## Running the experiment

### Pilot (30 requirements, stub backend — no API key required)

```bash
python scripts/run_experiment.py --pilot 30 --backend stub
```

### Full scale (312 requirements, Claude backend)

```bash
export ANTHROPIC_API_KEY=sk-...
python scripts/run_experiment.py --full --backend anthropic --model claude-sonnet-4-6
```

Outputs land in `results/` (per-requirement JSON logs, `model_provenance.json`) and overwrite `tables/aggregate_results.csv` + `tables/per_domain_results.csv`. Regenerate figures with `python scripts/generate_all_figures.py`, then recompile the paper.

### Cost and runtime

Approximate for full scale on `claude-sonnet-4-6`:
- ~3.2M input tokens, ~2.6M output tokens ⇒ **~$50–65** at current list pricing (verify at https://www.anthropic.com/pricing).
- Wall-clock ~2–4 hours, rate-limit bound.

## Repository layout

```
TestCaseGen_Reserach/
  test_case_generation_paper.tex          # canonical IEEE source
  test_case_generation_paper_preview.pdf  # preview build
  compile_all.bat                         # Windows build script
  figures/                                # figures referenced by .tex
  tables/                                 # CSVs rendered by csvsimple
  datasets/                               # 312-requirement corpora
  repo/                                   # reference apps for mutation targets
    hr-app/
    banking-api/
    fhir-lite/
  scripts/
    generate_requirements.py              # dataset generator
    generate_all_figures.py               # figure regenerator
    build_preview.py                      # preview-class LaTeX build
    prompts.py                            # 5-element prompt taxonomy
    verify.py                             # 4-class rule calculus
    mutation.py                           # mutation operators + scoring
    llm_adapter.py                        # Claude + deterministic stub
    run_experiment.py                     # Track B orchestrator
  results/                                # run outputs + provenance
  notebooks/                              # exploratory analysis (empty)
```

## Research series

1. Defect prediction — repository analytics + ML (`defect_prediction_paper/`).
2. Self-healing test automation — DOM similarity + ML (`self_healing_stage_a/`).
3. Risk-based testing — CI/CD-integrated defect prediction (`test-prioritization-service/`).
4. **This paper:** LLM-driven test case generation (`test-case-generation-service/` + MAP wizard).

## Governance

Prompt content, payload caps, path exclusions, and redaction regexes are configured in `ai-quality.config.yaml` at the service root. Shared schema with the Test Prioritization Service so a single governance file can cover all four AI-quality services in a deployment.
