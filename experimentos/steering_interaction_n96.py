"""Factorial steering interaction analysis for Biblio-VSE v2 (N=96).

Same contrasts as steering_interaction_analysis.py (N=32, unchanged):
  ZS interaction  = (Exp 6 - Exp 2) - (Exp 4 - Exp 1)
  RAG interaction = (Exp 8 - Exp 5) - (Exp 7 - Exp 3)
with paired cluster-bootstrap 95% CIs, computed twice: resampling the mutation
scenarios (primary) and the nine meta-rules (conservative). Only models with
all eight experiments (the local open-weight models) are analysed.

Usage (from repo root):
  python experimentos/steering_interaction_n96.py --condition mixed
Output: experimentos/steering_interaction_n96_<condition>.json
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from steering_interaction_analysis import analyze_model, N_BOOT, SEED


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True)
    args = ap.parse_args()
    with open(os.path.join(HERE, f"predictions_n96_{args.condition}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    y = data["ground_truth"]
    clusterings = {
        "scenario": [a["scenario"] for a in data["artifacts"]],
        "meta_rule": [a["meta_rule"] for a in data["artifacts"]],
    }
    results = {}
    for model, preds in data["predictions"].items():
        if not all(str(e) in preds for e in range(1, 9)):
            continue
        results[model] = {name: analyze_model(y, clusters, preds)
                          for name, clusters in clusterings.items()}
        for name in clusterings:
            for contrast, entry in results[model][name].items():
                v = entry["metrics"]["f1"]
                print(f"  {model:<28}{name:<10}{contrast:<22}F1 {v['estimate']:+.4f} "
                      f"[{v['ci_grouped_95'][0]:+.4f}, {v['ci_grouped_95'][1]:+.4f}]")
    out = {"design": {"condition": args.condition, "n_artifacts": len(y),
                      "bootstrap": f"paired cluster bootstrap, k={N_BOOT}, seed={SEED}",
                      "clusterings": {k: len(set(v)) for k, v in clusterings.items()}},
           "models": results}
    path = os.path.join(HERE, f"steering_interaction_n96_{args.condition}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"[+] Wrote {path}")


if __name__ == "__main__":
    main()
