# PAIRED COMPARISON OF TWO EXPERIMENTAL CONDITIONS (Biblio-VSE v2, N=96)
#
# Used for
#   - the language study (reviewer R1): es vs en (monolingual Spanish vs
#     monolingual English), mixed vs es, mixed vs en;
#   - the robustness study (reviewer R2): mixed vs noisy (same artifacts with
#     label-preserving enterprise noise).
#
# The editions share artifact IDs, labels, and order, so every comparison is
# paired artifact by artifact. For each model x experiment present in both
# matrices: F1 in each condition, ΔF1 = F1_b - F1_a with a paired
# scenario-cluster bootstrap 95% CI (k=10,000), and a paired sign-flip
# permutation test on scenario-level correctness differences (Monte Carlo,
# 100,000 patterns). Holm-Bonferroni within the comparison family.
#
# Usage (from repo root):
#   python experimentos/compare_conditions.py --a es --b en
#   python experimentos/compare_conditions.py --a mixed --b noisy
# Output: experimentos/compare_n96_<a>_vs_<b>.json

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

from statistical_resampling import f1, mcc, holm_correction, EXP_NAMES
from statistical_analysis_n96 import cluster_diffs, sign_flip_test

N_BOOT = 10000
SEED = 42


def load(condition):
    with open(os.path.join(_DIR, f"predictions_n96_{condition}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def paired_delta_ci(y, pa, pb, clusters):
    rng = random.Random(SEED)
    members = defaultdict(list)
    for i, c in enumerate(clusters):
        members[c].append(i)
    keys = sorted(members)
    deltas = []
    for _ in range(N_BOOT):
        idx = []
        for _ in keys:
            idx.extend(members[rng.choice(keys)])
        yt = [y[i] for i in idx]
        deltas.append(f1(yt, [pb[i] for i in idx]) - f1(yt, [pa[i] for i in idx]))
    deltas.sort()
    return deltas[int(0.025 * N_BOOT)], deltas[min(int(0.975 * N_BOOT), N_BOOT - 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    args = ap.parse_args()
    A, B = load(args.a), load(args.b)

    ids_a = [x["id"] for x in A["artifacts"]]
    ids_b = [x["id"] for x in B["artifacts"]]
    assert ids_a == ids_b, "artifact order differs between conditions"
    assert A["ground_truth"] == B["ground_truth"], "labels differ between conditions"
    y = A["ground_truth"]
    scenarios = [x["scenario"] for x in A["artifacts"]]

    rows = []
    for model in A["predictions"]:
        if model not in B["predictions"]:
            continue
        for exp in sorted(A["predictions"][model], key=int):
            if exp not in B["predictions"][model]:
                continue
            pa, pb = A["predictions"][model][exp], B["predictions"][model][exp]
            lo, hi = paired_delta_ci(y, pa, pb, scenarios)
            t_obs, p, method = sign_flip_test(cluster_diffs(y, pa, pb, scenarios))
            agree = sum(x == z for x, z in zip(pa, pb)) / len(y)
            rows.append({
                "model": model, "exp": exp,
                f"f1_{args.a}": round(f1(y, pa), 4), f"f1_{args.b}": round(f1(y, pb), 4),
                f"mcc_{args.a}": round(mcc(y, pa), 4), f"mcc_{args.b}": round(mcc(y, pb), 4),
                "delta_f1": round(f1(y, pb) - f1(y, pa), 4),
                "delta_f1_ci_scenario": [round(lo, 4), round(hi, 4)],
                "t_observed": t_obs, "p_raw": round(p, 5), "prediction_agreement": round(agree, 4),
            })

    adj = holm_correction([r["p_raw"] for r in rows])
    for r, pa in zip(rows, adj):
        r["p_holm"] = round(pa, 5)

    print("=" * 118)
    print(f"  {args.a} -> {args.b}: ΔF1 = F1({args.b}) - F1({args.a}); paired scenario tests, "
          f"Holm m={len(rows)}")
    print("=" * 118)
    for r in rows:
        mark = "  *" if r["p_holm"] < 0.05 else ""
        print(f"  {r['model']:<30}{EXP_NAMES[int(r['exp'])]:<22}"
              f"{r[f'f1_{args.a}']:>7.3f} -> {r[f'f1_{args.b}']:<7.3f}"
              f"Δ={r['delta_f1']:+.3f} [{r['delta_f1_ci_scenario'][0]:+.3f},"
              f"{r['delta_f1_ci_scenario'][1]:+.3f}]  p={r['p_raw']:.4f} "
              f"Holm={r['p_holm']:.4f}  agree={r['prediction_agreement']:.2f}{mark}")
    mean_delta = sum(r["delta_f1"] for r in rows) / len(rows) if rows else 0.0
    wins = sum(r["delta_f1"] > 0 for r in rows)
    losses = sum(r["delta_f1"] < 0 for r in rows)
    print(f"\n  cells: {len(rows)}  mean ΔF1={mean_delta:+.4f}  "
          f"{args.b} better in {wins}, worse in {losses}, tied in {len(rows) - wins - losses}")

    out = {
        "a": args.a, "b": args.b, "n_artifacts": len(y),
        "design": "paired; ΔF1 CI from scenario-cluster bootstrap (k=10,000); sign-flip "
                  "permutation over scenarios (Monte Carlo 100,000); Holm within family",
        "summary": {"cells": len(rows), "mean_delta_f1": round(mean_delta, 4),
                    "b_better": wins, "b_worse": losses},
        "rows": rows,
    }
    path = os.path.join(_DIR, f"compare_n96_{args.a}_vs_{args.b}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"[+] Wrote {path}")


if __name__ == "__main__":
    main()
