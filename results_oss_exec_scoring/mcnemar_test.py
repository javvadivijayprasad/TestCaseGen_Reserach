#!/usr/bin/env python3
"""Paired McNemar test: community (manual) baseline vs. full RAITG (Sonnet),
per mutant, on the 293 frozen mutants. Stdlib only.

Records:
  RAITG:     results_oss_exec_scoring/per_mutant_scores/sonnet__full__sut*.csv
  Community: results/oss_manual_baseline/sut*_manual_baseline.csv
Both keyed by mutant_id; 'killed' column is 0/1.
"""
import csv, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SUTS = [
    ("sut1_httpbin",             "sonnet__full__sut1_httpbin.csv",             "sut1_manual_baseline.csv"),
    ("sut2_fastapi_restful",     "sonnet__full__sut2_fastapi_restful.csv",     "sut2_manual_baseline.csv"),
    ("sut3_flaskr",              "sonnet__full__sut3_flaskr.csv",              "sut3_manual_baseline.csv"),
    ("sut4_fastapi_task_manager","sonnet__full__sut4_fastapi_task_manager.csv","sut4_manual_baseline.csv"),
]

def load(path):
    d = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            d[row["mutant_id"]] = int(row["killed"])
    return d

def binom_two_sided_p(b, c):
    """Exact two-sided binomial p for McNemar (n=b+c, k=min(b,c), p=0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)

def mcnemar_cc(b, c):
    if b + c == 0:
        return float("nan")
    return (abs(b - c) - 1) ** 2 / (b + c)

def chi2_1df_p(x):
    if math.isnan(x):
        return float("nan")
    return math.erfc(math.sqrt(x / 2.0))

lines = []
tot = dict(a=0, b=0, c=0, d=0)
for name, raitg_csv, manual_csv in SUTS:
    r = load(os.path.join(HERE, "per_mutant_scores", raitg_csv))
    m = load(os.path.join(ROOT, "results", "oss_manual_baseline", manual_csv))
    assert set(r) == set(m), f"mutant_id mismatch on {name}: {set(r) ^ set(m)}"
    a = sum(1 for k in r if m[k] == 1 and r[k] == 1)   # both kill
    b = sum(1 for k in r if m[k] == 1 and r[k] == 0)   # community only
    c = sum(1 for k in r if m[k] == 0 and r[k] == 1)   # RAITG only
    d = sum(1 for k in r if m[k] == 0 and r[k] == 0)   # neither
    for key, v in zip("abcd", (a, b, c, d)):
        tot[key] += v
    chi2 = mcnemar_cc(b, c)
    lines.append(
        f"{name}: n={a+b+c+d}  both={a}  community-only(b)={b}  "
        f"RAITG-only(c)={c}  neither={d}  "
        f"McNemar chi2(cc)={chi2:.3f}  exact binomial p={binom_two_sided_p(b,c):.4f}"
    )

a, b, c, d = tot["a"], tot["b"], tot["c"], tot["d"]
chi2 = mcnemar_cc(b, c)
lines.append("")
lines.append(
    f"AGGREGATE (293 mutants): both={a}  community-only(b)={b}  RAITG-only(c)={c}  "
    f"neither={d}"
)
lines.append(
    f"  community kills = {a+b}  RAITG kills = {a+c}"
)
lines.append(
    f"  McNemar chi2 (continuity-corrected) = (|{b}-{c}|-1)^2/({b}+{c}) = {chi2:.3f}"
)
lines.append(f"  chi2 1-df p (asymptotic) = {chi2_1df_p(chi2):.4f}")
lines.append(f"  exact two-sided binomial p = {binom_two_sided_p(b,c):.4f}")

out = "\n".join(lines) + "\n"
print(out, end="")
with open(os.path.join(HERE, "mcnemar_results.txt"), "w") as f:
    f.write(out)
