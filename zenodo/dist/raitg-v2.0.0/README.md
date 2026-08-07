# RAITG v2.0.0 Reproducibility Bundle

**Project:** RAITG (Requirement-Aware Intelligent Test Generator)
**Paper:** LLM-Based Test Case Generation from Natural-Language Requirements:
A Verified Multi-Domain Empirical Study with Symbolic Mutation Indicators
**Author:** Vijay Prasad Javvadi (Independent Researcher)
**Email:** vijay@vijayjavvadiresearch.ai
**ORCID:** 0009-0004-1192-6906

## What's in v2.0.0 (vs v1.0.0)

Version 2.0.0 adds a fourth Subject Under Test (SUT) — `logistics-app` —
representing last-mile delivery logistics, along with 50 new natural-language
requirements and the full pipeline re-run across the expanded dataset.

| Element | v1.0.0 | **v2.0.0** |
|---|---|---|
| Requirements | 312 | **362** |
| Domains | 3 | **4** (added logistics) |
| SUTs | 3 | **4** (added logistics-app, 192 LOC) |
| LLM runs (3 conditions) | 936 | **1,086** |
| Executable mutation testing | 3 apps, 194 mutants | **4 apps, 273 mutants** |
| Aggregate kill rate | 82.99% | **82.42%** |
| Statistics | n=312 paired | **n=362 paired** |
| Verification full vs ablation | +21.79 pp | **+22.1 pp** (d=0.65, p<0.0001) |
| Mutation testing per operator | 3-app breakdown | **4-app breakdown** |

## Contents

```
raitg-v2.0.0/
  README.md                  - This file
  paperE_preprint_v2.pdf     - Preprint of the paper (11 pages, with logistics)
  requirements.txt           - Python dependencies

  datasets/
    combined.json            - All 362 requirements
    commercial_web.json      - 112 reqs
    financial_services.json  - 98 reqs
    healthcare.json          - 102 reqs
    logistics.json           - 50 reqs (NEW)
    README.md

  repo/                      - 4 SUTs source code
    hr-app/app.py            - HR (142 LOC)
    banking-api/app.py       - Financial services (126 LOC)
    fhir-lite/app.py         - Healthcare (147 LOC)
    logistics-app/app.py     - Last-mile delivery (192 LOC, NEW)

  scripts/                   - Full RAITG pipeline
    run_experiment.py        - End-to-end orchestrator
    prompts.py               - Five-element prompt taxonomy
    verify.py                - Rule verification engine
    mutation.py              - Symbolic mutation indicator (regex)
    mutation_exec_v2.py      - Executable AST-mutation testing
    baseline_tests.py        - Hand-authored boundary-comprehensive test suite
    stats_analysis.py        - Bootstrap CIs + Wilcoxon + Cohen's d
    generate_all_figures.py  - Figure regeneration
    rescore.py               - Per-domain rescoring
    llm_adapter.py           - Anthropic API adapter with retry

  tables/                    - Regenerated CSVs (n=362, 4 domains)
    aggregate_results.csv
    per_domain_results.csv
    executable_mutation_per_app.csv (4 apps)
    executable_mutation_by_operator.csv
    statistics.csv (n=362 bootstrap + paired)
    per_domain_significance.csv
    bootstrap_confidence_intervals.csv
    multi_model_comparison.csv (Sonnet 4.6 vs Haiku 4.5)
    raitg_subsystems.csv
    dataset_summary.csv

  results/
    mutation_exec_v2.json    - Per-app mutation testing details
    model_provenance.json    - LLM snapshots used
    runs/                    - Sample run logs per condition (subset of 1086)
      unverified/
      ablation/
      full/

  figures/                   - All paper figures
    raitg_architecture.png
    verification_ablation.png
    mutation_score_by_domain.png
    coverage_by_domain.png
    aggregate_results.png
    rule_class_contribution.png
    map_integration.png
```

## To reproduce

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# Full pipeline (1,086 LLM calls, ~$3-8, ~45-90 min)
python scripts/run_experiment.py --full

# Executable mutation testing (~5-10 min, free)
python scripts/mutation_exec_v2.py

# Statistical analysis (~30 sec, free)
python scripts/stats_analysis.py

# Regenerate figures
python scripts/generate_all_figures.py
```

Expected outputs match the values in `tables/` and `paperE_preprint_v2.pdf`.

## Headline numbers (Full RAITG, n=362)

- Coverage: 100% (vs 0% unverified-LLM baseline)
- Verification pass: 95.9% (vs 73.9% ablation), Cohen's d=0.65, Wilcoxon p<0.0001
- Symbolic mutation indicator: 53.3% (vs 42.8% unverified)
- Executable AST-mutation kill (4 SUTs): 82.42% aggregate (225/273)
- Per-domain verification pass: 93.8% (commercial web), 95.9% (financial), 97.1% (healthcare), 98.0% (logistics)

## License

All content released under **CC-BY-4.0** (text and data) and **MIT** (code).

## Citation

```bibtex
@dataset{javvadi2026raitg_v2,
  author       = {Javvadi, Vijay Prasad},
  title        = {RAITG: Requirement-Aware Intelligent Test Generator -
                  Dataset, Pipeline, and Reproducibility Bundle v2.0.0},
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v2.0.0},
  doi          = {<NEW DOI to be assigned on publication>},
  url          = {https://doi.org/10.5281/zenodo.20285104}
}
```

## Related

- **GitHub:** https://github.com/javvadivijayprasad/TestCaseGen_Reserach
- **Concept DOI (latest version):** https://doi.org/10.5281/zenodo.20285104
- **v1.0.0 (earlier version):** archived at the same concept DOI

## AI use disclosure

Anthropic Claude (Sonnet 4.6 + Haiku 4.5 for the cross-model comparison) is
the LLM under evaluation in this work. The same LLM was also used for
prose-drafting assistance during manuscript preparation. All empirical claims,
dataset extraction, pipeline runs, statistical analyses, and mutation-testing
computations were generated by the author's own scripts (this bundle) and
verified against on-disk artifacts. The AI tool was not used to generate
data, results, or analyses.

## Changelog

### v2.0.0 (2026-06-17)
- Added 4th SUT: `logistics-app` (last-mile delivery, 192 LOC)
- Added 50 logistics-domain requirements -> total 362
- Re-ran full pipeline: 1,086 LLM calls (362 × 3 conditions)
- Regenerated all tables, figures, statistics with n=362
- Fixed hr-app baseline test bug (password length boundary)
- Updated stats: full vs ablation Cohen's d 0.63 -> 0.65, Wilcoxon p<0.0001

### v1.0.0 (2026-05-19)
- Initial public release with 312 requirements across 3 domains
