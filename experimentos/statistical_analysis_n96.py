# STATISTICAL ANALYSIS — Biblio-VSE v2 (N=96), one condition
#
# Extends experimentos/statistical_resampling.py (N=32, kept unchanged for the
# archival results) to the expanded benchmark.
#
# Dependence structure. Artifacts are generated as compliant/violating variants
# of shared mutation scenarios, so observations are clustered. Two clusterings
# are analysed:
#   - scenario  (53 mutation scenarios; PRIMARY): the unit at which the
#     mutation protocol induces dependence;
#   - meta-rule (9 clusters; CONSERVATIVE sensitivity analysis). With 9
#     clusters the exact sign-flip test has 2^9 = 512 patterns, so its smallest
#     attainable two-sided p-value is 2/512 = 0.0039, larger than the Holm
#     threshold for the first of 28 tests (0.05/28 = 0.0018): no comparison can
#     ever be declared significant under that design, whatever the sample size.
#     This is why the primary test moves to the scenario level.
#
# For each model x experiment cell:
#   F1, MCC, balanced accuracy, per-rule macro-F1, expected asymmetric cost,
#   grouped percentile bootstrap CIs (scenario and meta-rule, k=10,000),
#   paired cluster sign-flip permutation tests vs. Exp 1 (scenario: Monte Carlo
#   with 100,000 sign patterns; meta-rule: exact enumeration), exact McNemar.
# Holm-Bonferroni correction is applied within each test family over all
# model x experiment comparisons present in the matrix.
#
# Usage (from repo root):
#   python experimentos/statistical_analysis_n96.py --condition mixed
# Output: experimentos/statistical_analysis_n96_<condition>.json

import argparse
import json
import os
import random
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from statistical_resampling import (
    f1, mcc, balanced_accuracy, macro_f1_per_rule, expected_costs,
    mcnemar_exact, holm_correction, COST_RATIOS, EXP_NAMES,
)

N_BOOT = 10000
N_PERM_MC = 100000
SEED = 42


def grouped_bootstrap(y_true, preds_by_key, clusters, stat, n_boot=N_BOOT, seed=SEED):
    """Percentile CI of stat(y, p) resampling clusters with replacement."""
    rng = random.Random(seed)
    members = defaultdict(list)
    for i, c in enumerate(clusters):
        members[c].append(i)
    keys = sorted(members)
    values = []
    for _ in range(n_boot):
        idx = []
        for _ in keys:
            idx.extend(members[rng.choice(keys)])
        values.append(stat([y_true[i] for i in idx], {k: [p[i] for i in idx]
                                                       for k, p in preds_by_key.items()}))
    values.sort()
    return values[int(0.025 * n_boot)], values[min(int(0.975 * n_boot), n_boot - 1)]


def cluster_diffs(y_true, pred_a, pred_b, clusters):
    d = defaultdict(int)
    for t, pa, pb, c in zip(y_true, pred_a, pred_b, clusters):
        d[c] += (pb == t) - (pa == t)
    return list(d.values())


def sign_flip_test(diffs, n_mc=N_PERM_MC, seed=SEED):
    """Two-sided paired sign-flip test on cluster-level correctness differences.
    Exact enumeration for <= 16 clusters, otherwise Monte Carlo (add-one corrected)."""
    t_obs = sum(diffs)
    g = len(diffs)
    if g <= 16:
        count = 0
        for mask in range(2 ** g):
            t = sum(d if (mask >> i) & 1 else -d for i, d in enumerate(diffs))
            count += abs(t) >= abs(t_obs)
        return t_obs, count / 2 ** g, "exact"
    rng = random.Random(seed)
    nonzero = [d for d in diffs if d]
    count = 0
    for _ in range(n_mc):
        t = sum(d if rng.random() < 0.5 else -d for d in nonzero)
        count += abs(t) >= abs(t_obs)
    return t_obs, (count + 1) / (n_mc + 1), "monte_carlo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True)
    args = ap.parse_args()
    matrix_path = os.path.join(_DIR, f"predictions_n96_{args.condition}.json")
    out_path = os.path.join(_DIR, f"statistical_analysis_n96_{args.condition}.json")

    with open(matrix_path, encoding="utf-8") as fh:
        data = json.load(fh)
    y = data["ground_truth"]
    rules = [a["meta_rule"] for a in data["artifacts"]]
    scenarios = [a["scenario"] for a in data["artifacts"]]
    n = len(y)

    def f1_stat(yt, p):
        return f1(yt, p["x"])

    results, perm_s, perm_r, mcn = {}, [], [], []
    print("=" * 112)
    print(f"  N={n}, condition={args.condition}: F1 with scenario-grouped (S) and "
          f"meta-rule-grouped (R) 95% bootstrap CIs")
    print("=" * 112)
    for model, exps in data["predictions"].items():
        base = exps.get("1")
        for exp in sorted(exps, key=int):
            pred = exps[exp]
            ci_s = grouped_bootstrap(y, {"x": pred}, scenarios, f1_stat)
            ci_r = grouped_bootstrap(y, {"x": pred}, rules, f1_stat)
            cell = {
                "f1": round(f1(y, pred), 4),
                "ci_scenario": [round(v, 4) for v in ci_s],
                "ci_meta_rule": [round(v, 4) for v in ci_r],
                "mcc": round(mcc(y, pred), 4),
                "balanced_accuracy": round(balanced_accuracy(y, pred), 4),
                "macro_f1_per_rule": round(macro_f1_per_rule(y, pred, rules), 4),
                "expected_cost": expected_costs(y, pred),
            }
            if exp != "1" and base is not None:
                t_s, p_s, how_s = sign_flip_test(cluster_diffs(y, base, pred, scenarios))
                t_r, p_r, how_r = sign_flip_test(cluster_diffs(y, base, pred, rules))
                b, c, p_m = mcnemar_exact(y, base, pred)
                cell["perm_scenario"] = {"t_observed": t_s, "p_raw": round(p_s, 5), "method": how_s}
                cell["perm_meta_rule"] = {"t_observed": t_r, "p_raw": round(p_r, 5), "method": how_r}
                cell["mcnemar"] = {"b_base_only_correct": b, "c_new_only_correct": c,
                                   "p_raw": round(p_m, 5)}
                perm_s.append((model, exp, p_s))
                perm_r.append((model, exp, p_r))
                mcn.append((model, exp, p_m))
            results.setdefault(model, {})[exp] = cell
            print(f"  {model:<30}{EXP_NAMES[int(exp)]:<22}{cell['f1']:>7.4f}  "
                  f"S[{ci_s[0]:.2f},{ci_s[1]:.2f}]  R[{ci_r[0]:.2f},{ci_r[1]:.2f}]  "
                  f"MCC={cell['mcc']:+.3f}  BAcc={cell['balanced_accuracy']:.3f}")

    for family, key in ((perm_s, "perm_scenario"), (perm_r, "perm_meta_rule"), (mcn, "mcnemar")):
        adj = holm_correction([t[2] for t in family])
        for (model, exp, _), pa in zip(family, adj):
            results[model][exp][key]["p_holm"] = round(pa, 5)

    print("\n" + "=" * 112)
    print(f"  PAIRED TESTS vs Exp 1 (Holm within family; m={len(perm_s)})")
    print("=" * 112)
    print(f"  {'Model':<30}{'Exp':<22}{'T_S':>5}{'p_S raw':>10}{'p_S Holm':>10}"
          f"{'p_R raw':>10}{'p_R Holm':>10}{'McN raw':>10}{'McN Holm':>10}")
    for model, exps in results.items():
        for exp, cell in exps.items():
            if exp == "1" or "perm_scenario" not in cell:
                continue
            s, r, m = cell["perm_scenario"], cell["perm_meta_rule"], cell["mcnemar"]
            flag = "  *" if s["p_holm"] < 0.05 else ""
            print(f"  {model:<30}{EXP_NAMES[int(exp)]:<22}{s['t_observed']:>5}{s['p_raw']:>10.4f}"
                  f"{s['p_holm']:>10.4f}{r['p_raw']:>10.4f}{r['p_holm']:>10.4f}"
                  f"{m['p_raw']:>10.4f}{m['p_holm']:>10.4f}{flag}")

    regex = data["regex_baseline"]
    regex_cell = {"f1": round(f1(y, regex), 4),
                  "ci_scenario": [round(v, 4) for v in grouped_bootstrap(y, {"x": regex}, scenarios, f1_stat)],
                  "mcc": round(mcc(y, regex), 4),
                  "balanced_accuracy": round(balanced_accuracy(y, regex), 4)}

    cost_min = {}
    for model, exps in results.items():
        cost_min[model] = {}
        for r in COST_RATIOS:
            best = min(exps, key=lambda e: exps[e]["expected_cost"][str(r)])
            cost_min[model][str(r)] = {"exp": best, "cost": exps[best]["expected_cost"][str(r)]}

    out = {
        "design": {
            "condition": args.condition,
            "n_artifacts": n,
            "n_scenarios": len(set(scenarios)),
            "n_meta_rules": len(set(rules)),
            "bootstrap": f"percentile, clusters resampled with replacement, k={N_BOOT}, seed={SEED}",
            "primary_test": f"paired sign-flip permutation test over {len(set(scenarios))} "
                            f"mutation scenarios (Monte Carlo, {N_PERM_MC} patterns), Holm",
            "conservative_test": "exact paired sign-flip test over 9 meta-rule clusters "
                                 "(512 patterns; min attainable p = 0.0039), Holm",
            "secondary_test": "exact McNemar on paired correctness (assumes independence), Holm",
            "majority_class_f1": data.get("majority_class_f1"),
        },
        "regex_baseline": regex_cell,
        "models": results,
        "cost_minimizing": cost_min,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"\n  Regex baseline F1={regex_cell['f1']:.4f}; majority-class F1={data.get('majority_class_f1')}")
    print(f"[+] Wrote {out_path}")


if __name__ == "__main__":
    main()
