# Paper 8 — Review Addendum

**Source:** `test_case_generation_paper.tex` (current, 752 lines, IEEEtran conference class).
**Companion variants:** `test_case_generation_paper_preview.tex` (616 lines), `test_case_generation_paper_preview_v2.tex` (701 lines).
**Status:** Partial revision since prior `REVIEW.md`. Major construct-validity gap acknowledged but **not yet remediated**; several minor and governance items addressed.

---

## 1. Validation of prior `REVIEW.md` major gaps

| # | Original major gap | Verdict | Evidence |
|---|---|---|---|
| 1 | Symbolic vs executable mutation score not comparable | **PARTIALLY ADDRESSED** | Paper now explicitly states the symbolic score is "comparable between RAITG conditions only" (abstract, §5.4, §6.1), withdraws the manual-vs-RAITG claim, and commits to PIT/mutmut in §10 future work. Source still uses `scripts/mutation.py` (symbolic); `scripts/mutation_exec.py` exists in the repo but is not invoked for the headline numbers. Numbers cited (59.5/58.5/46.7) match `results/runs/*.json` re-computed means (59.9/59.0/47.1) within rounding. |
| 2 | Reference apps under-described — LoC / complexity / mutant count | **PARTIALLY ADDRESSED** | New §4.3 + Table `tab:reference_apps` added with LoC (hr-app 142, banking-api 126, fhir-lite 147 — confirmed exact via `wc -l repo/*/app.py`). Cyclomatic complexity and mutant count are still **TBD** (5 occurrences in the .tex). |
| 3 | Manual baseline blends real logs + literature estimate; no per-domain breakdown | **VALID** | §5.2 still asserts "184.1 hours" from a literature-cited 35 min/req figure. §6.2 explicitly admits "per-domain timing logs were not separately captured." No change. |
| 4 | Unverified-LLM baseline handicapped by missing schema | **VALID — now acknowledged** | New §6.1 second paragraph concedes the 0.0% coverage figure "reflects the baseline output *format*, not the baseline backend's intrinsic capability." Good. But the headline number remains in the abstract without an asterisk — reviewers will still flag it. |
| 5 | No EvoSuite / AthenaTest / commercial-tool comparison | **VALID** | Related-work §2.2 still cites EvoSuite/Randoop only narratively; no head-to-head experiment. |
| 6 | Verification rules not formalised (no Z3 / FOL spec) | **VALID** | §3.4 still describes the four rule classes by prose example. No appendix with formal pseudocode. |
| 7 | Governance / HIPAA / PCI redaction claims unsupported | **PARTIALLY ADDRESSED** | New Appendix A (Governance Configuration Excerpt, lines 519–540) shows an `ai-quality.config.yaml` snippet with `max_payload_size_kb`, `exclude_files`, `redact_patterns` (`JIRA-[0-9]+`, `db\.internal\.[a-z]+`), `hash_author_identifiers: true`. **However**: there is *no* patient-name, MRN, account-number, SSN, or PHI/PCI-specific pattern despite the healthcare/financial domains. The example reads as DevOps hygiene, not HIPAA/PCI redaction. |

## 2. New findings the prior review missed

### 2.1 Zenodo DOI placeholder is still present (3 locations)

`grep -n XXXXXXXX test_case_generation_paper.tex` returns three hits:
- **Line 606** — §7 Data and Artefact Availability (`\url{https://doi.org/10.5281/zenodo.XXXXXXXX}`).
- **Line 748** — bibliography entry `javvadi2026raitg_dataset` (`doi: 10.5281/zenodo.XXXXXXXX`).
- **Line 748** — same entry, second URL.

The Zenodo build artefact (`zenodo/dist/raitg-v1.0.0.zip`) exists, but the DOI has not been minted/copied into the .tex. Same placeholder appears in `_preview_v2.tex` (lines 555, 697). Submission-blocking.

### 2.2 Mutation scoring methodology — still symbolic in the current paper

`scripts/mutation.py` docstring explicitly self-describes as a "deliberate simplification" and labels executable mutation as "Track B's v2." `scripts/mutation_exec.py` has been written (pure-stdlib, no mutmut dependency) but is **not wired into `run_experiment.py`** and not referenced from the .tex. The paper therefore still ships symbolic numbers. Prior REVIEW.md gap #1 cannot be marked FIXED.

### 2.3 Reference-app summary table exists but is half-populated

Table `tab:reference_apps` (lines 268–282) lists LoC but cyclomatic complexity, mutant count, and totals are all `TBD`. Five `TBD` strings remain in the .tex. The note ("populated from the v1.0 release pipeline before the journal extension") is a deferral, not a fix.

### 2.4 Governance excerpt does not show domain-specific PHI/PCI redaction

Appendix A's only redact patterns are `JIRA-[0-9]+` and `db\.internal\.[a-z]+`. The paper's healthcare-/financial-services emphasis is not reflected — a reviewer evaluating HIPAA/PCI claims will see no patient-name, MRN, account-number, or card-PAN pattern. The claim in §1 contributions that the framework supports "deployment in regulated environments" remains thinly evidenced.

### 2.5 Writing — specific problematic sentences

1. **Abstract (line 47)** is one ~580-word paragraph (single `\begin{abstract}` block). IEEEtran does not enforce paragraph breaks here, but most ICSE/ASE reviewers will flag this as unreadable. The abstract states "structural validity, logical correctness, requirement traceability, and redundancy filtering" and then again "deterministic rule-based verification engine" within 40 words — internal redundancy.
2. **Line 264** (§4.3): "All three are deliberately compact Python services that mirror the functional surface of well-known open-source projects in their domain (`hr-app` after Gitea / Ghost staff modules, `banking-api` after Supabase-style CRUD plus transactional state, `fhir-lite` after LinuxForHealth FHIR resource handlers); the compactness keeps the symbolic mutation pass fast (executable mutation testing under PIT/mutmut is deferred to the journal extension as discussed in Section~\ref{sec:validity})." — 64-word run-on with parentheticals stacked three deep.
3. **Line 358** (§5.4): "The manual baseline estimate of 68.5% is drawn from prior empirical literature that executes hand-authored suites against mutated code with tools such as PIT and `mutmut` rather than scoring them symbolically, and is therefore *not directly comparable* to the three RAITG-condition numbers reported here." — the same apologia is repeated in the abstract and §6.1.
4. **§8.3 (~line 559)**: "Organisations piloting the framework reported increased engineer satisfaction and improved retention" — unsupported claim with no citation, study, or n. Drop or cite.
5. **§1.2 (lines 80–92)**: Paper-Organisation subsection is nine identical `Section~\ref{} ...` sentences. Compress into one sentence with parenthetical section numbers, or delete.

### 2.6 Variant divergence — which is the canonical submission target?

| File | Class | Title block | Coverage | Mutation | Effort | Platform name |
|---|---|---|---|---|---|---|
| `test_case_generation_paper.tex` | `IEEEtran[conference]` | `\IEEEauthorblockN{}` | 100% / 0% / 100% | 59.5% symbolic (with disclaimer) | 184.1 → 6.4 h (96.5%) | **TestForge AI** |
| `_preview.tex` | `IEEEtran[conference]` | same | **94.1% vs 71.2% (22.9 pp)** | **84.6% vs 68.5% (16.1 pp)** | 184.0 → 58.9 h (68.0%) | **Modern Automation Platform** |
| `_preview_v2.tex` | `article` (11pt letterpaper) | plain `\author` | 100% / 0% / 100% | 59.5% symbolic | 184.1 → 6.4 h (96.5%) | TestForge AI |

Findings:
- **The `_preview.tex` numbers are stale by an order of magnitude** (94.1% vs current 100%, 68.0% effort reduction vs current 96.5%, 84.6% mutation vs current 59.5%). It also still names "Modern Automation Platform" — the rebrand to "TestForge AI" was not propagated. **Do not ship this file.** It will leak inconsistent claims if attached as supplemental material.
- `_preview_v2.tex` is content-identical to the current IEEEtran paper but in plain-article form — a "human-readable preview." Keep one; delete or `.gitignore` the other.
- **Recommendation:** `test_case_generation_paper.tex` is the canonical submission. Delete `_preview.tex` (stale data); keep `_preview_v2.tex` only as a build artefact.

### 2.7 Residual "MAP" naming leakage in current paper

Even after the rebrand to TestForge AI, the integration figure is still:
- `figures/map_integration.png` (line 544 in current .tex)
- `\label{fig:map_integration}` (line 546)

Caption text now says "TestForge AI integration" but filename and label still say `map`. Cosmetic but reviewer-noticeable.

### 2.8 Headline-claim verification against artefacts

Re-computed from `results/runs/*.json` (n=312 per condition, 936 files total):

| Condition | Coverage (paper) | Coverage (computed) | Mut (paper) | Mut (computed) | V-pass (paper) | V-pass (computed) |
|---|---|---|---|---|---|---|
| Unverified | 0.0% | 0.0% | 46.7% | 47.1% | 0.0% | 0.0% |
| Ablation | 100.0% | 100.0% | 58.5% | 59.0% | 73.9% | 73.7% |
| Full RAITG | 100.0% | 100.0% | 59.5% | 59.9% | 95.6% | 95.5% |

All match within rounding. The **96.5% effort reduction is not directly verifiable from logs** because the 184.1 h figure is a literature extrapolation (35 min × 312 / 60), and the 6.4 h figure is wall-clock from `telemetry`. The ratio is arithmetic, not empirical.

## 3. Top-5 prioritised fix list (combining prior + new)

| Rank | Fix | Effort | Source |
|---|---|---|---|
| 1 | **Replace symbolic mutation with executable** (`scripts/mutation_exec.py` already drafted — wire it into `run_experiment.py`, re-score all 3 conditions × 3 apps, regenerate Table 4/Fig 4). Removes the headline construct-validity blocker. | 1–2 weeks | Prior #1 + new §2.2 |
| 2 | **Mint Zenodo DOI v1.0.0 and replace `XXXXXXXX` in 3 .tex locations + delete stale `_preview.tex`.** Trivial but submission-blocking. | <1 day | Prior #8 + new §2.1, §2.6 |
| 3 | **Complete Table `tab:reference_apps`** with cyclomatic complexity (`radon cc`) and mutant counts produced by fix #1; remove all 5 `TBD` strings. | 1 day | New §2.3 |
| 4 | **Add a HIPAA/PCI-shaped governance example** to Appendix A (≥2 patterns each for patient identifiers / MRN / SSN / PAN / account numbers) so the regulated-environment claim is concretely supported. | 1–2 days | Prior #7 + new §2.4 |
| 5 | **Compress the abstract** into 2–3 paragraphs (≤350 words), drop redundant clauses, fix the 5 specific run-on/unsupported sentences listed in §2.5; rename `map_integration.png` → `testforge_integration.png` and update label. | 1 day | New §2.5, §2.7 |

**Lower-priority** (still recommended but not blocking): EvoSuite head-to-head on `banking-api` (Prior #5, ~1 week); formal pseudo-code appendix for the four rule classes (Prior #6, 2–3 days); per-domain manual-baseline timing instrumentation (Prior #3 — defer to journal extension).
