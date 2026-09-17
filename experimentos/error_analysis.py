# ERROR ANALYSIS — Per-Artifact Misclassification Report
# Uses the prediction arrays already stored in statistical_resampling.py
# (no re-running of models required).
#
# Generates:
#   1. Per-artifact prediction table for each model under its best configuration
#   2. Cross-model consensus table (which artifacts ALL models fail on)
#   3. Error categorization by meta-rule
#   4. LaTeX-ready table for the paper (Section 5 / Appendix)
#
# Usage:
#   python experimentos/error_analysis.py

import json
import os
import sys
import numpy as np

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for p in (_DIR, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")

# ── Ground truth (same order as dataset_isomorfico.json) ─────────────────────
y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1])

# ── All predictions from statistical_resampling.py ───────────────────────────
experiments = {
    1: {
        "Gemma-2":  np.array([0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1]),
        "Mistral":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0]),
        "Qwen2.5":  np.array([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0]),
        "Phi-3.5":  np.array([1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0]),
    },
    2: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
    },
    3: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Mistral":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Qwen2.5":  np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    },
    4: {
        "Gemma-2":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1]),
        "Mistral":  np.array([1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5":  np.array([1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1]),
    },
    5: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    },
    6: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
    },
    7: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Mistral":  np.array([0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Qwen2.5":  np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1]),
    },
    8: {
        "Gemma-2":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral":  np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5":  np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        "Phi-3.5":  np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
    },
}

# Best experiment per model (by F1-Score from paper results)
BEST_EXP = {
    "Gemma-2": 4,   # Steering, F1=0.800
    "Mistral": 4,   # Steering, F1=0.880
    "Qwen2.5": 2,   # Zero-Shot, F1=0.800
    "Phi-3.5": 8,   # Synergistic, F1=0.917
}

MODELS = ["Gemma-2", "Mistral", "Qwen2.5", "Phi-3.5"]

EXP_NAMES = {
    1: "Baseline", 2: "Zero-Shot", 3: "RAG", 4: "Steering",
    5: "ZS+RAG", 6: "ZS+Steer", 7: "RAG+Steer", 8: "Synergistic",
}


def error_type(true_label, pred_label) -> str:
    if true_label == pred_label:
        return "TP" if true_label == 1 else "TN"
    if true_label == 1 and pred_label == 0:
        return "FN"
    return "FP"


def load_artifact_info():
    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return [
        {
            "idx": i,
            "id":    d["id_muestra"],
            "rule":  d["meta_regla"],
            "type":  d["tipo_artefacto"],
            "label": d["etiqueta_clase"],
        }
        for i, d in enumerate(data)
    ]


def per_artifact_table(artifacts, model_name, exp_num):
    preds = experiments[exp_num][model_name]
    print(f"\n  [{model_name}] — Exp {exp_num}: {EXP_NAMES[exp_num]}")
    print(f"  {'#':<3} {'Artifact ID':<28} {'Rule':<14} {'Type':<15} {'GT':<4} {'Pred':<5} {'Result'}")
    print("  " + "-" * 82)
    errors = {"FP": [], "FN": []}
    for a in artifacts:
        i  = a["idx"]
        gt = y_true[i]
        p  = preds[i]
        et = error_type(gt, p)
        marker = " <--" if et in ("FP", "FN") else ""
        print(f"  {i+1:<3} {a['id']:<28} {a['rule']:<14} {a['type']:<15} {gt:<4} {p:<5} {et}{marker}")
        if et in ("FP", "FN"):
            errors[et].append(a)
    return errors


def cross_model_consensus(artifacts):
    """Artifacts misclassified by ALL models under their best configuration."""
    always_wrong = []
    for a in artifacts:
        i = a["idx"]
        all_wrong = all(
            experiments[BEST_EXP[m]][m][i] != y_true[i]
            for m in MODELS
        )
        if all_wrong:
            always_wrong.append(a)
    return always_wrong


def error_by_rule(artifacts, model_name, exp_num):
    preds = experiments[exp_num][model_name]
    rule_errors = {}
    for a in artifacts:
        i  = a["idx"]
        et = error_type(y_true[i], preds[i])
        if et in ("FP", "FN"):
            rule_errors.setdefault(a["rule"], []).append(et)
    return rule_errors


def latex_error_table(artifacts):
    """Generates a LaTeX table for the paper (Section: Error Analysis)."""
    print("\n" + "=" * 90)
    print("  LATEX TABLE — Per-Artifact Error Analysis (Best Config per Model)")
    print("=" * 90)
    print()
    print(r"\begin{table*}[htbp]")
    print(r"\centering")
    print(r"\caption{Per-artifact error analysis under each model's best configuration.")
    print(r"TP=True Positive, TN=True Negative, FP=False Positive (overclaiming compliance),")
    print(r"FN=False Negative (missing violation). Best experiments: Gemma-2/Mistral = Exp~4 (Steering),")
    print(r"Qwen2.5 = Exp~2 (Zero-Shot), Phi-3.5 = Exp~8 (Synergistic).}")
    print(r"\label{tab:error_analysis}")
    print(r"\renewcommand{\arraystretch}{1.1}")
    print(r"\resizebox{\textwidth}{!}{")
    print(r"\begin{tabular}{|l|l|c|c|c|c|c|c|c|}")
    print(r"\hline")
    print(r"\textbf{Artifact ID} & \textbf{Rule} & \textbf{GT} & \textbf{Gemma-2} & \textbf{Mistral} & \textbf{Qwen2.5} & \textbf{Phi-3.5} & \textbf{\#Errors} & \textbf{Error Types} \\")
    print(r"\hline")

    for a in artifacts:
        i   = a["idx"]
        gt  = y_true[i]
        cells = []
        err_types = set()
        n_errors = 0
        for m in MODELS:
            p  = experiments[BEST_EXP[m]][m][i]
            et = error_type(gt, p)
            if et in ("FP", "FN"):
                cells.append(r"\textcolor{red}{" + et + "}")
                err_types.add(et)
                n_errors += 1
            else:
                cells.append(et)
        err_str = "+".join(sorted(err_types)) if err_types else "---"
        row = f"\\texttt{{{a['id']}}} & {a['rule']} & {gt} & {' & '.join(cells)} & {n_errors} & {err_str} \\\\"
        print(row)

    print(r"\hline")
    print(r"\end{tabular}")
    print(r"}")
    print(r"\end{table*}")


def main():
    artifacts = load_artifact_info()

    print("=" * 90)
    print("  ERROR ANALYSIS — Per-Artifact Misclassification (Best Config per Model)")
    print("=" * 90)

    all_rule_errors = {m: {} for m in MODELS}

    for model in MODELS:
        exp = BEST_EXP[model]
        errors = per_artifact_table(artifacts, model, exp)
        rule_errors = error_by_rule(artifacts, model, exp)
        all_rule_errors[model] = rule_errors
        if errors["FP"]:
            print(f"\n  FALSE POSITIVES (marked compliant but actually violating):")
            for a in errors["FP"]:
                print(f"    {a['id']} [{a['rule']}]")
        if errors["FN"]:
            print(f"\n  FALSE NEGATIVES (missed violations):")
            for a in errors["FN"]:
                print(f"    {a['id']} [{a['rule']}]")

    # Cross-model consensus
    print("\n" + "=" * 90)
    print("  CROSS-MODEL CONSENSUS — Artifacts misclassified by ALL models (best config)")
    print("=" * 90)
    hard = cross_model_consensus(artifacts)
    if hard:
        print(f"\n  {len(hard)} artifact(s) that ALL models fail on:")
        for a in hard:
            print(f"    [{a['idx']+1}] {a['id']} | rule={a['rule']} | type={a['type']} | GT={y_true[a['idx']]}")
    else:
        print("\n  No artifact is misclassified by all models simultaneously.")

    # Error by meta-rule
    print("\n" + "=" * 90)
    print("  ERRORS BY META-RULE")
    print("=" * 90)
    all_rules = sorted({a["rule"] for a in artifacts})
    print(f"\n  {'Rule':<15} {'Gemma-2':<12} {'Mistral':<12} {'Qwen2.5':<12} {'Phi-3.5':<12}")
    print("  " + "-" * 60)
    for rule in all_rules:
        row = f"  {rule:<15}"
        for model in MODELS:
            errs = all_rule_errors[model].get(rule, [])
            if errs:
                row += f" {', '.join(errs):<12}"
            else:
                row += f" {'OK':<12}"
        print(row)

    # LaTeX table
    latex_error_table(artifacts)

    print("\n[Done] Copy the LaTeX table above into your article (Section 4 / Appendix).")


if __name__ == "__main__":
    main()
