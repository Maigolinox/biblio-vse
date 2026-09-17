"""Factorial interaction analysis for activation steering.

Uses the canonical N=32 prediction matrix and a paired cluster bootstrap over
the nine meta-rule groups. The reported interaction contrasts are:

  ZS interaction  = (Exp 6 - Exp 2) - (Exp 4 - Exp 1)
  RAG interaction = (Exp 8 - Exp 5) - (Exp 7 - Exp 3)

Run from the repository root:
  python experimentos/steering_interaction_analysis.py
"""

import json
import math
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.environ.get(
    "PREDICTIONS_MATRIX", os.path.join(HERE, "predictions_n32.json")
)
OUT_PATH = os.environ.get(
    "STEERING_INTERACTION_OUT",
    os.path.join(HERE, "steering_interaction_n32.json"),
)
N_BOOT = 10000
SEED = 42


def confusion(y_true, y_pred):
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))
    tn = sum(t == 0 and p == 0 for t, p in zip(y_true, y_pred))
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))
    fn = sum(t == 1 and p == 0 for t, p in zip(y_true, y_pred))
    return tp, tn, fp, fn


def metrics(y_true, y_pred):
    tp, tn, fp, fn = confusion(y_true, y_pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denom if denom else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    return {
        "f1": f1,
        "mcc": mcc,
        "balanced_accuracy": (recall + specificity) / 2,
        "precision": precision,
        "recall": recall,
    }


def contrast(metric_values, exps):
    a, b, c, d = exps
    return (metric_values[a] - metric_values[b]) - (metric_values[c] - metric_values[d])


def percentile_ci(values):
    values.sort()
    return values[int(0.025 * len(values))], values[min(int(0.975 * len(values)), len(values) - 1)]


def analyze_model(y_true, clusters, predictions):
    definitions = {
        "structured_prompting": ("(Exp6-Exp2)-(Exp4-Exp1)", (6, 2, 4, 1)),
        "rag": ("(Exp8-Exp5)-(Exp7-Exp3)", (8, 5, 7, 3)),
    }
    point_metrics = {exp: metrics(y_true, predictions[str(exp)]) for exp in range(1, 9)}
    members = defaultdict(list)
    for i, cluster in enumerate(clusters):
        members[cluster].append(i)
    keys = sorted(members)
    rng = random.Random(SEED)
    boot = {
        name: {metric: [] for metric in next(iter(point_metrics.values()))}
        for name in definitions
    }
    for _ in range(N_BOOT):
        idx = []
        for _ in keys:
            idx.extend(members[rng.choice(keys)])
        yt = [y_true[i] for i in idx]
        sampled = {
            exp: metrics(yt, [predictions[str(exp)][i] for i in idx])
            for exp in range(1, 9)
        }
        for name, (_, exps) in definitions.items():
            for metric in boot[name]:
                boot[name][metric].append(
                    contrast({exp: sampled[exp][metric] for exp in sampled}, exps)
                )

    result = {}
    for name, (formula, exps) in definitions.items():
        result[name] = {"formula": formula, "metrics": {}}
        for metric in boot[name]:
            point = contrast({exp: point_metrics[exp][metric] for exp in point_metrics}, exps)
            lo, hi = percentile_ci(boot[name][metric])
            result[name]["metrics"][metric] = {
                "estimate": round(point, 4),
                "ci_grouped_95": [round(lo, 4), round(hi, 4)],
            }
    return result


def main():
    with open(MATRIX_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    y_true = data["ground_truth"]
    clusters = [artifact["meta_rule"] for artifact in data["artifacts"]]
    results = {
        model: analyze_model(y_true, clusters, predictions)
        for model, predictions in data["predictions"].items()
    }
    output = {
        "design": {
            "n_artifacts": len(y_true),
            "clusters": len(set(clusters)),
            "bootstrap": f"paired cluster bootstrap, k={N_BOOT}, seed={SEED}",
            "interpretation": "Positive interaction means steering performs better in the named context than without it.",
        },
        "models": results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    for model, model_results in results.items():
        print(f"\n{model}")
        for name, entry in model_results.items():
            print(f"  {name}: {entry['formula']}")
            for metric, value in entry["metrics"].items():
                lo, hi = value["ci_grouped_95"]
                print(f"    {metric:<18} {value['estimate']:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    print(f"\n[+] Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
