# Paper 8 — Reviewer Report

**Title:** AI-Driven Test Case Generation from Natural-Language Requirements: A Prompt-Engineered, Rule-Verified Framework for Scalable Software Quality Engineering
**Target venue (inferred):** ICSE main / ASE / ICST (IEEEtran conference, ~18 pages)

**Verdict: MAJOR (3–4 weeks of fixes)** — useful empirical contribution but blocked by a methodological confound (symbolic vs executable mutation score), missing baselines, and unsubstantiated governance claims.

---

## Headline claims

* Design effort reduction: 184.1 hrs (manual) → 6.4 hrs (RAITG), 96.5% reduction across 312 requirements in 3 domains.
* Requirement coverage: 0% (unverified LLM) → 100% (RAITG).
* Verification pass rate: 73.9% (no verify) → 95.6% (full RAITG); +21.7pp gain.
* Mutation score: 59.5% (full) vs 58.5% (ablation); +1.0pp.

## Strengths

1. Multi-domain evaluation — 312 requirements across HR (112), financial (98), healthcare (102). Non-trivial scale.
2. Ablation rigor — four conditions (manual, unverified LLM, ablation no-verify, full RAITG) isolate verification contribution. +21.7pp pass-rate gain credible.
3. Prompt engineering formalised — five-element taxonomy (role, context, task, heuristic scaffold, output contract) grounded in classical test design (EP, BVA, state transitions, decision tables, negative paths).
4. Reproducibility scripts + cost transparency ($40–$65 USD for 312 requirements with Anthropic Sonnet 4.6).
5. Zenodo release at `zenodo/dist/raitg-v1.0.0` — packaged.

## Major gaps

1. **Symbolic mutation score is not comparable to manual baseline** — paper acknowledges in §6 (Validity) that the metric is regex-based ("permission", "validation", "comparison", "arithmetic") rather than executing mutations. The 59.5% vs manual baseline 68.5% comparison is **methodologically invalid** because the metrics differ. This is the biggest publication blocker.
2. **Reference apps under-described** — `hr-app`, `banking-api`, `fhir-lite` are "small, runnable Python apps" but no LoC / complexity / mutant count published.
3. **Manual baseline blends real data + literature estimate** — §4.2 says "engineering logs of originating organisations" but uses a literature-cited 35-min/req figure. Per-domain breakdown / variance not reported.
4. **Unverified LLM baseline handicapped** — 0% coverage because naive prompt produces no JSON schema. Not a fair comparison; coverage difference isn't due to RAITG, it's due to the output format being missing in the baseline.
5. **No EvoSuite / AthenaTest / commercial-tool comparison** — paper cites EvoSuite, Randoop as "structurally focused" but doesn't run them. Is 59.5% mutation score competitive with EvoSuite's 60–75% branch coverage on the same SUT?
6. **Verification rules not formalised** — §3.3 describes four rule classes (structural, logical, coverage, redundancy) by example, no formal spec. Z3? Regex? First-order logic? `scripts/verify.py` listed but contents not in paper.
7. **Governance claims unsupported** — line 73 mentions "governance configuration that controls prompt content, payload sizes, redaction patterns for regulated environments." For HIPAA / PCI domains, no explanation of how patient names / account numbers are redacted or anonymised.

## Minor issues

* Tufano et al. (2020) cited in line 122 — verify full bibliography entry.
* **Zenodo DOI placeholder** — line 63–64 shows `10.5281/zenodo.XXXXXXXX`. Must be filled before submission. (See §S1 in `SUBMISSION_REVIEW.md`.)
* Inconsistent terminology — "RAITG", "framework", "pipeline", "system", "architecture" used interchangeably.
* `mutation_score_by_domain.png` referenced; error bars / significance unclear.
* Per-domain breakdown (Table 4) generated but not deeply analysed.

## Cross-paper coupling

* **Zenodo DOI placeholder** vs paper 7's resolved DOI — series consistency broken (§S1).
* Framework name: paper 8 uses RAITG; paper 7 has none. Consider umbrella name.
* Line 29 mentions "TestForge AI monorepo" and `apps/framework-generator-api/src/routes/test-case-generation.routes.ts` integration — but no cross-reference to paper 7's self-healing service or the integrated platform story.

## Concrete fix list

1. **§5.3 mutation scoring methodology** — replace symbolic mutation with executable mutation testing: PIT (Java) or mutmut (Python) on the three reference apps. Re-score all four conditions with the same metric. This is the single largest fix and may take 2–3 weeks.
2. **New §4.1 Reference-app summary table** — LoC, cyclomatic complexity, test-to-code ratio, defect-history depth, mutation-operator distribution per app.
3. **§4.2 Unverified-LLM baseline:** clarify exact prompt; add a fairer ablation (same five-element taxonomy without verification) so the verification effect is isolated.
4. **§4.2 Manual baseline:** per-domain effort breakdown (HR / Financial / Healthcare hours, source attribution: real logs vs literature estimate per domain).
5. **New Appendix A: Rule Calculus Specification** — at least 3–5 formal rule definitions (e.g., "Precondition–Action Consistency", "Traceability Closure") in pseudo-code or first-order logic.
6. **New Appendix B: Governance config example** — sanitised excerpt of `ai-quality.config.yaml` showing 2+ redaction patterns (e.g., `patient_name_redaction`, `account_number_mask`).
7. **§6 Validity:** rewrite line 333 acknowledgement: "Symbolic mutation indicator served as proof-of-concept; this revision replaces it with executable mutation testing (PIT / mutmut)."
8. **Zenodo DOI:** finalise version v1.0.0 and replace `XXXXXXXX` with concrete DOI before submission. Apply canonical from §S1 if shared with the rest of the series; otherwise allocate a paper-8-specific DOI under the same Zenodo community.
9. **§2 Related work:** add EvoSuite / AthenaTest comparison plan or actual experiment on at least one reference app. Position vs commercial LLM test-gen tools.
10. **Cross-paper:** reference paper 7's self-healing as orthogonal contribution; mention integrated TestForge platform.
11. **§5 Per-domain analysis:** discuss whether healthcare verification pass rate differs from HR / financial. If not, why not.
12. **Acronyms:** standardise — "RAITG framework" throughout.
