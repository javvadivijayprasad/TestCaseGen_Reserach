# RAITG: Requirement-Aware Intelligent Test Generator Dataset

Zenodo release version 1.0.0 — companion dataset for Paper 8 of the *Vijay Javvadi Research* series on AI-augmented software quality engineering.

> **Paper:** AI-Driven Test Case Generation from Natural-Language Requirements: A Prompt-Engineered, Rule-Verified Framework for Scalable Software Quality Engineering
> **Author:** Vijay P. Javvadi — Independent Researcher
> **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)

## What's in this release

```
raitg-v1.0.0/
  datasets/
    combined.json              # 312 requirements across three domains
    commercial_web.json        # 112 requirements (HR management web app)
    financial_services.json    # 98  requirements (retail banking API)
    healthcare.json            # 102 requirements (FHIR-lite exchange)
  results/
    runs/                      # 936 per-requirement run logs (3 conditions × 312 reqs)
    model_provenance.json      # backend, model, prompt version, rules version
  tables/
    aggregate_results.csv      # per-condition aggregates (manual / unverified / ablation / full)
    per_domain_results.csv     # per-domain results for the full framework condition
    dataset_summary.csv        # requirement counts by domain and layer
    raitg_subsystems.csv       # RAITG architecture subsystem roles
  figures/                     # 7 PNG figures used in the paper
  repo/                        # three reference applications used as mutation targets
    hr-app/                    #   employee / leave / timesheet domain
    banking-api/               #   account / transfer / interest domain
    fhir-lite/                 #   patient / encounter / observation domain
  scripts/                     # reproducibility artefacts
    run_experiment.py          # end-to-end orchestrator
    generate_requirements.py   # deterministic dataset generator
    prompts.py                 # five-element prompt engineering taxonomy
    verify.py                  # four-class rule-based verification calculus
    mutation.py                # symbolic mutation engine
    llm_adapter.py             # Claude/Anthropic backend adapter
    rescore.py                 # re-aggregate metrics from run logs
    generate_all_figures.py    # regenerate figures from tables
    json_extract.py            # robust JSON extraction from LLM responses
  README.md                    # this file
  LICENSE                      # CC BY 4.0 text
  CITATION.cff                 # machine-readable citation metadata
  requirements.txt             # Python dependencies
```

The paper PDF and LaTeX source are intentionally **not** bundled in this release. This matches the convention of the companion *Software Defect Prediction Dataset* (doi:10.5281/zenodo.19682733), which ships only the data, trained model artefacts, and extraction scripts. The paper itself is distributed through the journal / preprint channel; cite it via the `javvadi2026raitg_paper` entry in the citation block below.

## How to cite

If you use this dataset or the artefacts in your work, please cite:

```
@misc{javvadi2026raitg_dataset,
  author       = {Javvadi, Vijay P.},
  title        = {{RAITG}: Requirement-Aware Intelligent Test Generator Dataset ---
                   312 Natural-Language Requirements, Generated Test Artefacts,
                   and Reference Applications},
  month        = {Apr},
  year         = 2026,
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.XXXXXXXX},
  url          = {https://doi.org/10.5281/zenodo.XXXXXXXX}
}
```

Please also cite the companion paper:

```
@article{javvadi2026raitg_paper,
  author    = {Javvadi, Vijay P.},
  title     = {{AI}-Driven Test Case Generation from Natural-Language Requirements:
               A Prompt-Engineered, Rule-Verified Framework for Scalable
               Software Quality Engineering},
  journal   = {Vijay Javvadi Research},
  volume    = {8},
  year      = {2026}
}
```

## Reproducibility

Re-run the full 312-requirement experiment on Anthropic Claude Sonnet 4.6:

```bash
python -m venv .venv
source .venv/bin/activate                 # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # on Windows: $env:ANTHROPIC_API_KEY="sk-ant-..."

python scripts/run_experiment.py --full --backend anthropic \
  --model claude-sonnet-4-6
python scripts/generate_all_figures.py
```

Expected cost: ~USD 40 at current Anthropic list pricing.
Expected wall-clock time: ~3 hours, rate-limit bound.

## Research series

This release is the second Zenodo dataset in an eight-paper research series on AI-augmented software quality engineering:

- Papers 1–6 — Software Defect Prediction series (dataset: doi:10.5281/zenodo.19682733)
- Paper  7  — Self-Healing Test Automation (DOM-similarity + ML)
- Paper  8  — **This paper**: LLM-driven Test Case Generation (RAITG)

All eight papers share a common deployment surface: the TestForge AI monorepo of microservices with a Next.js wizard UI.

## Contact

Independent Researcher — Applied AI for Software Quality Engineering
Website: https://vijayjavvadiresearch.ai
