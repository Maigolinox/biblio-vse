# STATISTICAL ANALYSIS — N=32, canonical prediction matrix
#
# Replaces the previous version of this script, which carried obsolete
# 20-element prediction vectors hard-coded from the N=20 pilot logs.
# All predictions are now loaded from experimentos/predictions_n32.json
# (built and validated by experimentos/build_predictions_matrix.py).
#
# Statistical design (revised after two rounds of external review):
#   1. CLUSTER-LEVEL PAIRED PERMUTATION TEST (primary): the 32 artifacts are
#      related mutations/variants generated per meta-rule from one synthetic
#      project, so even paired artifact-level tests overstate independence.
#      The per-cluster correctness difference (config - baseline) is computed
#      for each of the 9 meta-rule clusters and the cluster signs are flipped
#      exhaustively (2^9 = 512 exact enumeration); the two-sided p-value is
#      the fraction of sign patterns with |T| >= |T_observed|.
#   2. Exact McNemar tests on paired CORRECTNESS outcomes (secondary; treats
#      artifact pairs as independent). The previously used Wilcoxon
#      signed-rank test on paired binary predictions tests label shift, not
#      accuracy difference, and was therefore replaced.
#   3. GROUPED (cluster) bootstrap CIs: 9 meta-rule clusters resampled with
#      replacement.
#   4. Additional metrics: MCC, balanced accuracy, per-rule macro-F1, and an
#      explicit ASYMMETRIC COST function C = c_FP*FP + c_FN*FN evaluated at
#      cost ratios c_FP:c_FN in {1, 2, 5, 10} (false compliance declarations
#      are costlier in auditing).
#   5. Holm-Bonferroni step-down correction over each family of 28 tests.
#
# Usage (from repo root):
#   python experimentos/statistical_resampling.py
#
# Output: full console report + experimentos/statistical_analysis_n32.json

import json
import math
import os
import random
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MATRIX_PATH = os.environ.get(
    "PREDICTIONS_MATRIX", os.path.join(_DIR, "predictions_n32.json")
)
OUT_PATH = os.environ.get(
    "STATISTICAL_ANALYSIS_OUT", os.path.join(_DIR, "statistical_analysis_n32.json")
)

N_BOOT = 10000
SEED = 42

EXP_NAMES = {1: "Baseline", 2: "Zero-Shot", 3: "RAG", 4: "Steering",
             5: "ZS + RAG", 6: "ZS + Steering", 7: "RAG + Steering",
             8: "ZS + RAG + Steering"}


# ── Metrics ───────────────────────────────────────────────────────────────────

def confusion(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return tp, tn, fp, fn


def f1(y_true, y_pred):
    tp, tn, fp, fn = confusion(y_true, y_pred)
    return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0


def mcc(y_true, y_pred):
    tp, tn, fp, fn = confusion(y_true, y_pred)
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / denom if denom else 0.0


def balanced_accuracy(y_true, y_pred):
    tp, tn, fp, fn = confusion(y_true, y_pred)
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    return (sens + spec) / 2


def macro_f1_per_rule(y_true, y_pred, rules):
    """Mean of per-meta-rule binary F1 over the 9 meta-rule groups."""
    by_rule = defaultdict(list)
    for t, p, r in zip(y_true, y_pred, rules):
        by_rule[r].append((t, p))
    scores = []
    for r in sorted(by_rule):
        yt = [t for t, _ in by_rule[r]]
        yp = [p for _, p in by_rule[r]]
        scores.append(f1(yt, yp))
    return sum(scores) / len(scores)


# ── Grouped (cluster) bootstrap ───────────────────────────────────────────────

def grouped_bootstrap_ci(y_true, y_pred, clusters, n_boot=N_BOOT, seed=SEED):
    """95% percentile CI for F1 resampling meta-rule clusters with replacement."""
    rng = random.Random(seed)
    members = defaultdict(list)
    for i, c in enumerate(clusters):
        members[c].append(i)
    keys = sorted(members)
    stats = []
    for _ in range(n_boot):
        idx = []
        for _ in keys:
            idx.extend(members[rng.choice(keys)])
        yt = [y_true[i] for i in idx]
        yp = [y_pred[i] for i in idx]
        stats.append(f1(yt, yp))
    stats.sort()
    lo = stats[int(0.025 * n_boot)]
    hi = stats[min(int(0.975 * n_boot), n_boot - 1)]
    return lo, hi


# ── Cluster-level paired permutation test ─────────────────────────────────────

def cluster_permutation_test(y_true, pred_base, pred_new, clusters):
    """Exact cluster-level paired sign-flip permutation test.

    Statistic: T = sum over clusters of (correct_new - correct_base) within
    the cluster. Under H0 the classifier assignment is exchangeable within
    each cluster, so each cluster difference is sign-symmetric. All 2^G sign
    patterns are enumerated exactly (G = 9 clusters -> 512 patterns).
    Returns (T_observed, two-sided p)."""
    diffs = defaultdict(int)
    for t, pb, pn, c in zip(y_true, pred_base, pred_new, clusters):
        diffs[c] += (1 if pn == t else 0) - (1 if pb == t else 0)
    d = list(diffs.values())
    g = len(d)
    t_obs = sum(d)
    count = 0
    for mask in range(2 ** g):
        t = 0
        for i in range(g):
            t += d[i] if (mask >> i) & 1 else -d[i]
        if abs(t) >= abs(t_obs):
            count += 1
    return t_obs, count / 2 ** g


# ── Asymmetric cost function ──────────────────────────────────────────────────

COST_RATIOS = [1, 2, 5, 10]  # c_FP : c_FN, with c_FN = 1


def expected_costs(y_true, y_pred):
    """Normalized expected cost C = (c_FP*FP + c_FN*FN) / N per cost ratio."""
    tp, tn, fp, fn = confusion(y_true, y_pred)
    n = len(y_true)
    return {str(r): round((r * fp + fn) / n, 4) for r in COST_RATIOS}


# ── Exact McNemar test and Holm correction ────────────────────────────────────

def mcnemar_exact(y_true, pred_base, pred_new):
    """Exact two-sided McNemar test on paired correctness outcomes.

    b = baseline correct, new wrong;  c = baseline wrong, new correct.
    Under H0 the discordant pairs follow Binomial(b+c, 0.5)."""
    b = sum(1 for t, pb, pn in zip(y_true, pred_base, pred_new)
            if pb == t and pn != t)
    c = sum(1 for t, pb, pn in zip(y_true, pred_base, pred_new)
            if pb != t and pn == t)
    n = b + c
    if n == 0:
        return b, c, 1.0
    k = min(b, c)
    # two-sided exact binomial p-value (doubling method, capped at 1)
    cdf = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return b, c, min(1.0, 2 * cdf)


def holm_correction(pvals):
    """Holm-Bonferroni step-down adjusted p-values (monotone)."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        running = max(running, val)
        adj[i] = running
    return adj


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(MATRIX_PATH, encoding="utf-8") as fh:
        data = json.load(fh)

    y_true = data["ground_truth"]
    rules = [a["meta_rule"] for a in data["artifacts"]]
    models = list(data["predictions"].keys())

    results = {}
    tests = []       # (model, exp, b, c, p_raw) for McNemar
    perm_tests = []  # (model, exp, t_obs, p_raw) for cluster permutation

    print("=" * 100)
    print("  PER-CELL METRICS — N=32, grouped bootstrap by meta-rule "
          f"(9 clusters, k={N_BOOT})")
    print("=" * 100)
    print(f"  {'Model':<26}{'Exp':<22}{'F1':>7}{'CI lo':>7}{'CI hi':>7}"
          f"{'MCC':>8}{'BalAcc':>8}{'MacroF1':>9}")
    print("  " + "-" * 96)

    for model in models:
        base = data["predictions"][model]["1"]
        for exp in range(1, 9):
            pred = data["predictions"][model][str(exp)]
            lo, hi = grouped_bootstrap_ci(y_true, pred, rules)
            cell = {
                "f1": round(f1(y_true, pred), 4),
                "ci_grouped": [round(lo, 4), round(hi, 4)],
                "mcc": round(mcc(y_true, pred), 4),
                "balanced_accuracy": round(balanced_accuracy(y_true, pred), 4),
                "macro_f1_per_rule": round(macro_f1_per_rule(y_true, pred, rules), 4),
                "expected_cost": expected_costs(y_true, pred),
            }
            if exp > 1:
                b, c, p = mcnemar_exact(y_true, base, pred)
                cell["mcnemar"] = {"b_base_only_correct": b,
                                   "c_new_only_correct": c,
                                   "p_raw": round(p, 4)}
                tests.append((model, exp, b, c, p))
                t_obs, pp = cluster_permutation_test(y_true, base, pred, rules)
                cell["cluster_permutation"] = {"t_observed": t_obs,
                                               "p_raw": round(pp, 4)}
                perm_tests.append((model, exp, t_obs, pp))
            results.setdefault(model, {})[exp] = cell
            print(f"  {model:<26}{EXP_NAMES[exp]:<22}{cell['f1']:>7.4f}"
                  f"{lo:>7.2f}{hi:>7.2f}{cell['mcc']:>8.3f}"
                  f"{cell['balanced_accuracy']:>8.3f}"
                  f"{cell['macro_f1_per_rule']:>9.3f}")

    # Regex rule-based baseline
    regex = data["regex_baseline"]
    lo, hi = grouped_bootstrap_ci(y_true, regex, rules)
    regex_cell = {
        "f1": round(f1(y_true, regex), 4),
        "ci_grouped": [round(lo, 4), round(hi, 4)],
        "mcc": round(mcc(y_true, regex), 4),
        "balanced_accuracy": round(balanced_accuracy(y_true, regex), 4),
        "macro_f1_per_rule": round(macro_f1_per_rule(y_true, regex, rules), 4),
        "expected_cost": expected_costs(y_true, regex),
    }
    print(f"  {'Regex baseline':<26}{'(rule-based)':<22}{regex_cell['f1']:>7.4f}"
          f"{lo:>7.2f}{hi:>7.2f}{regex_cell['mcc']:>8.3f}"
          f"{regex_cell['balanced_accuracy']:>8.3f}"
          f"{regex_cell['macro_f1_per_rule']:>9.3f}")

    # Holm correction over all 28 McNemar tests
    pvals = [t[4] for t in tests]
    adj = holm_correction(pvals)
    print()
    print("=" * 100)
    print("  EXACT McNEMAR TESTS vs. Exp 1 baseline (paired correctness; "
          "Holm-Bonferroni, m=28)")
    print("=" * 100)
    print(f"  {'Model':<26}{'Exp':<22}{'b':>4}{'c':>4}{'p raw':>9}{'p Holm':>9}")
    print("  " + "-" * 74)
    any_sig = False
    for (model, exp, b, c, p), pa in zip(tests, adj):
        results[model][exp]["mcnemar"]["p_holm"] = round(pa, 4)
        mark = "  *" if pa < 0.05 else ""
        any_sig = any_sig or pa < 0.05
        print(f"  {model:<26}{EXP_NAMES[exp]:<22}{b:>4}{c:>4}{p:>9.4f}{pa:>9.4f}{mark}")
    print()
    print(f"  McNemar tests surviving Holm correction at alpha=0.05: "
          f"{'YES' if any_sig else 'NONE'}")

    # Cluster-level paired permutation tests (primary; respects dependence)
    perm_p = [t[3] for t in perm_tests]
    perm_adj = holm_correction(perm_p)
    print()
    print("=" * 100)
    print("  CLUSTER-LEVEL PAIRED PERMUTATION TESTS vs. Exp 1 baseline "
          "(exact, 2^9=512 sign patterns; Holm m=28)")
    print("=" * 100)
    print(f"  {'Model':<26}{'Exp':<22}{'T_obs':>6}{'p raw':>9}{'p Holm':>9}")
    print("  " + "-" * 72)
    any_sig_perm = False
    for (model, exp, t_obs, p), pa in zip(perm_tests, perm_adj):
        results[model][exp]["cluster_permutation"]["p_holm"] = round(pa, 4)
        mark = "  *" if pa < 0.05 else ""
        any_sig_perm = any_sig_perm or pa < 0.05
        print(f"  {model:<26}{EXP_NAMES[exp]:<22}{t_obs:>6}{p:>9.4f}{pa:>9.4f}{mark}")
    print()
    print(f"  Permutation tests surviving Holm correction at alpha=0.05: "
          f"{'YES' if any_sig_perm else 'NONE'}")

    # Cost-minimizing configuration per model and cost ratio
    print()
    print("=" * 100)
    print("  COST-MINIMIZING CONFIGURATION per model and cost ratio "
          "(C = (c_FP*FP + FN)/N, c_FN=1)")
    print("=" * 100)
    print(f"  {'Model':<26}" + "".join(f"{'c_FP=' + str(r):>22}" for r in COST_RATIOS))
    for model in models:
        row = f"  {model:<26}"
        for r in COST_RATIOS:
            best = min(range(1, 9),
                       key=lambda e: results[model][e]["expected_cost"][str(r)])
            cost = results[model][best]["expected_cost"][str(r)]
            row += f"{EXP_NAMES[best] + ' (' + format(cost, '.3f') + ')':>22}"
        print(row)

    out = {
        "design": {
            "n_artifacts": 32,
            "bootstrap": f"grouped/cluster percentile bootstrap, 9 meta-rule "
                         f"clusters resampled with replacement, k={N_BOOT}, seed={SEED}",
            "primary_test": "exact cluster-level paired sign-flip permutation "
                            "test over the 9 meta-rule clusters (512 patterns) "
                            "vs. Exp 1 baseline, Holm-Bonferroni m=28",
            "secondary_test": "exact two-sided McNemar (binomial) on paired "
                              "correctness vs. Exp 1 baseline, Holm-Bonferroni "
                              "m=28 (treats artifact pairs as independent)",
            "cost_function": "C = (c_FP*FP + c_FN*FN)/N with c_FN=1, "
                             f"c_FP in {COST_RATIOS}",
        },
        "regex_baseline": regex_cell,
        "models": results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"\n[+] Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
