# Zenodo Upload Guide — RAITG Dataset v1.0.0

Step-by-step click-through for uploading `raitg-v1.0.0.zip` to Zenodo, matching the pattern used by the companion *Software Defect Prediction Dataset* (doi:10.5281/zenodo.19682733).

Estimated time: 10–15 minutes.

## Prerequisites

- A free Zenodo account (https://zenodo.org/signup) — ORCID sign-in recommended.
- The release bundle at `E:\EB1A_Research\TestCaseGen_Reserach\zenodo\dist\raitg-v1.0.0.zip`
- If you haven't rebuilt the bundle recently:
  ```powershell
  cd E:\EB1A_Research\TestCaseGen_Reserach
  .\.venv\Scripts\Activate.ps1
  python zenodo\build_release.py
  ```

## Step 1 — Start a new upload

1. Go to https://zenodo.org/uploads/new
2. Click **"Upload files"** and select `raitg-v1.0.0.zip`
3. Wait for the upload to complete (4.06 MB, usually < 30 seconds)

## Step 2 — Fill in the form

Copy-paste these values — they mirror the field layout on the Zenodo upload form.

### Basic information

**Title:**
```
RAITG: Requirement-Aware Intelligent Test Generator Dataset — 312 Natural-Language Requirements, Generated Test Artefacts, and Reference Applications
```

**Upload type:** Dataset

**Publication date:** (today's date; Zenodo auto-fills)

**Creators:**
- Given names: `Vijay P.`
- Family names: `Javvadi`
- Affiliation: `Independent Researcher`
- ORCID: (your ORCID if you have one)

**Description** (paste HTML — Zenodo renders it):
```html
<p>Dataset and reproducibility artefacts for the paper <em>AI-Driven Test Case Generation from Natural-Language Requirements: A Prompt-Engineered, Rule-Verified Framework for Scalable Software Quality Engineering</em>.</p>

<p>This release supports Paper 8 of the <em>Vijay Javvadi Research</em> series on AI-augmented software quality engineering. It contains:</p>

<ul>
  <li>312 natural-language requirements across commercial web (112), financial services (98), and healthcare (102) domains</li>
  <li>936 per-requirement run logs produced on Anthropic Claude Sonnet 4.6 under three experimental conditions: unverified LLM, framework with verification disabled (ablation), and full RAITG framework</li>
  <li>A multi-model comparison subset of 78 requirements on Claude Haiku 4.5</li>
  <li>Aggregate, per-domain, and per-condition result CSVs (bootstrap 95% confidence intervals, Cohen's d effect sizes, Wilcoxon signed-rank p-values)</li>
  <li>Three reference applications (HR, retail banking, FHIR-lite) used as mutation targets</li>
  <li>The five-element prompt engineering taxonomy (role, context, task, heuristic, output contract)</li>
  <li>The four-class rule-based verification calculus (structural, logical, coverage, redundancy)</li>
  <li>The end-to-end experimental pipeline with deterministic dataset generator, verification engine, symbolic mutation engine, and Claude adapter</li>
</ul>

<p><strong>Licence:</strong> Creative Commons Attribution 4.0 International (CC BY 4.0).</p>
<p><strong>Related dataset:</strong> <a href="https://doi.org/10.5281/zenodo.19682733">Software Defect Prediction Dataset (doi:10.5281/zenodo.19682733)</a> — supports Papers 1–6 of the same series.</p>
```

### Licence

Select: **Creative Commons Attribution 4.0 International (CC BY 4.0)**

### Funding

Leave blank (independent research).

### Related/alternate identifiers

Click **Add identifier** and enter:
- **Identifier:** `10.5281/zenodo.19682733`
- **Scheme:** DOI
- **Relationship:** is part of
- **Resource type:** Dataset

This links your new dataset to the defect-prediction dataset so they appear as a family on Zenodo.

### Subjects / keywords

Paste these one per line:
```
large language models
test case generation
prompt engineering
rule-based verification
software quality engineering
requirement analysis
AI-driven software engineering
behaviour-driven development
Playwright
pytest
mutation testing
Anthropic Claude
```

### Version

`1.0.0`

### Language

English

## Step 3 — Save as draft, then review

1. Click **Save draft** at the bottom.
2. Review the preview. Compare against the companion paper's Data Availability section (`test_case_generation_paper.tex`, `\section{Data and Artefact Availability}`).
3. Verify the file list shows `raitg-v1.0.0.zip` (~4 MB).

## Step 4 — Publish

1. Click **Publish**.
2. Zenodo assigns a permanent DOI — something like `10.5281/zenodo.XXXXXXXX`.
3. Copy the DOI; you'll need it next.

## Step 5 — Update the paper's placeholder DOI

In PowerShell:

```powershell
cd E:\EB1A_Research\TestCaseGen_Reserach
$realDoi = "10.5281/zenodo.XXXXXXXX"   # <- replace with the real one from Zenodo

# Update the paper + Zenodo release docs in place
(Get-Content test_case_generation_paper.tex) -replace 'zenodo\.XXXXXXXX', ($realDoi -replace '10.5281/','') | Set-Content test_case_generation_paper.tex
(Get-Content zenodo\README_zenodo.md)        -replace 'zenodo\.XXXXXXXX', ($realDoi -replace '10.5281/','') | Set-Content zenodo\README_zenodo.md
(Get-Content zenodo\CITATION.cff)            -replace 'zenodo\.XXXXXXXX', ($realDoi -replace '10.5281/','') | Set-Content zenodo\CITATION.cff
(Get-Content zenodo\metadata.json)           -replace 'zenodo\.XXXXXXXX', ($realDoi -replace '10.5281/','') | Set-Content zenodo\metadata.json
```

## Step 6 — Rebuild the paper with the real DOI

```powershell
.\compile_all.bat
```

The final IEEE PDF will show the real Zenodo DOI in the References and in the Data Availability section.

## Step 7 — (Optional) Cut a Zenodo v1.0.1 with the updated README

If you edited `zenodo\README_zenodo.md` to reflect the real DOI, rebuild the bundle and upload as a new version:

```powershell
python zenodo\build_release.py
```

On Zenodo, use the "New version" button on your v1.0.0 record to upload `raitg-v1.0.1.zip`. Zenodo assigns a fresh DOI for the new version while preserving a stable "all versions" DOI.

## Troubleshooting

- **Upload fails with "file too large"** — Zenodo limit is 50 GB per file. Our bundle is 4 MB so this should never happen.
- **Can't find the new-version button** — you must be signed in as the original creator.
- **ORCID sign-in not working** — fall back to email/password; you can link ORCID later.
- **DOI not rendering** — Zenodo DOIs take a few minutes to resolve on DataCite; paste the URL with leading `https://doi.org/` if needed.

## Citation (after publish)

Once published, the citation block in the paper becomes:

```
[X] V. P. Javvadi, "RAITG: Requirement-Aware Intelligent Test Generator Dataset — ...," Zenodo, ver. 1.0.0, 2026. doi: 10.5281/zenodo.<your-id>.
```

This matches the exact style already used for `javvadi2025defect_dataset` in Papers 1–2.
