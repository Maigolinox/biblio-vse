# SUBSET AND ERROR ANALYSIS — Biblio-VSE v2 (N=96), one condition
#
# For every model x experiment cell:
#   - accuracy on the original 32 artifacts vs. the 64 extension artifacts
#     (checks that the extension did not change task difficulty by construction);
#   - recall on Type-C positives and specificity on Type-B negatives
#     (adversarial robustness), and the same on non-adversarial artifacts;
#   - per-meta-rule accuracy.
# Across all cells: artifacts misclassified in the most cells, and artifacts
# misclassified by every model under its best (highest-F1) configuration.
# The regex baseline is included as a reference row.
#
# Usage (from repo root):
#   python experimentos/subset_analysis_n96.py --condition mixed
# Output: experimentos/subset_analysis_n96_<condition>.json

import argparse
import json
import os
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from statistical_resampling import f1


def rate(pairs):
    return round(sum(t == p for t, p in pairs) / len(pairs), 4) if pairs else None


def cell_subsets(arts, y, pred):
    def sel(cond):
        return [(y[i], pred[i]) for i, a in enumerate(arts) if cond(a)]
    per_rule = defaultdict(list)
    for i, a in enumerate(arts):
        per_rule[a["meta_rule"]].append((y[i], pred[i]))
    return {
        "f1": round(f1(y, pred), 4),
        "acc_original32": rate(sel(lambda a: a["origin"] == "original_v1")),
        "acc_extension64": rate(sel(lambda a: a["origin"] == "extension_v2")),
        "recall_typeC": rate(sel(lambda a: a["adversarial"] == "tipo_c")),
        "specificity_typeB": rate(sel(lambda a: a["adversarial"] == "tipo_b")),
        "recall_nonadv_pos": rate(sel(lambda a: not a["adversarial"] and a["label"] == 1)),
        "specificity_nonadv_neg": rate(sel(lambda a: not a["adversarial"] and a["label"] == 0)),
        "acc_per_rule": {r: rate(v) for r, v in sorted(per_rule.items())},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True)
    args = ap.parse_args()
    with open(os.path.join(_DIR, f"predictions_n96_{args.condition}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    arts, y = data["artifacts"], data["ground_truth"]

    cells = {"regex_baseline": {"-": cell_subsets(arts, y, data["regex_baseline"])}}
    errors = defaultdict(int)
    n_cells = 0
    best = {}
    for model, exps in data["predictions"].items():
        cells[model] = {}
        for exp, pred in exps.items():
            cells[model][exp] = cell_subsets(arts, y, pred)
            n_cells += 1
            for i, (t, p) in enumerate(zip(y, pred)):
                errors[i] += t != p
        best_exp = max(exps, key=lambda e: (f1(y, exps[e]), -int(e)))
        best[model] = {"exp": best_exp, "f1": round(f1(y, exps[best_exp]), 4),
                       "errors": [arts[i]["id"] for i, (t, p) in enumerate(zip(y, exps[best_exp])) if t != p]}

    common = set.intersection(*(set(b["errors"]) for b in best.values())) if best else set()
    hardest = sorted(errors.items(), key=lambda kv: -kv[1])[:15]

    print(f"{'System':<30}{'Exp':>4}{'F1':>7}{'orig32':>8}{'ext64':>8}{'recC':>7}{'specB':>7}"
          f"{'recPos':>8}{'specNeg':>8}")
    for model, exps in cells.items():
        for exp, c in sorted(exps.items()):
            print(f"{model:<30}{exp:>4}{c['f1']:>7.3f}{c['acc_original32']:>8.3f}"
                  f"{c['acc_extension64']:>8.3f}{c['recall_typeC']:>7.3f}{c['specificity_typeB']:>7.3f}"
                  f"{c['recall_nonadv_pos']:>8.3f}{c['specificity_nonadv_neg']:>8.3f}")
    print("\nBest configuration per model:", {m: (b["exp"], b["f1"]) for m, b in best.items()})
    print("Misclassified by every model under its best configuration:", sorted(common))
    print(f"Hardest artifacts (errors across {n_cells} model-experiment cells):")
    for i, k in hardest:
        a = arts[i]
        print(f"  {a['id']:<30}{a['meta_rule']:<14}label={a['label']}  adv={a['adversarial'] or '-':<7} errors={k}")

    out = {"condition": args.condition, "cells": cells, "best_per_model": best,
           "common_best_config_errors": sorted(common),
           "hardest": [{"id": arts[i]["id"], "meta_rule": arts[i]["meta_rule"],
                        "label": arts[i]["label"], "adversarial": arts[i]["adversarial"],
                        "errors": k, "cells": n_cells} for i, k in hardest]}
    path = os.path.join(_DIR, f"subset_analysis_n96_{args.condition}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"[+] Wrote {path}")


if __name__ == "__main__":
    main()
