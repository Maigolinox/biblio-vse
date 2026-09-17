# BUILD THE N=96 PREDICTION MATRIX FOR ONE EXPERIMENTAL CONDITION
#
# Parses resultados/n96/<condition>/exp<N>.txt (local models, Exp 1-8) and
# resultados/n96/<condition>/gemini_exp<N>.txt (hosted frontier model,
# Exp 1/2/3/5) and writes a canonical machine-readable matrix:
#
#   experimentos/predictions_n96_<condition>.json
#   experimentos/predictions_n96_<condition>.csv   (long format)
#
# Every parsed block is validated against the dataset (artifact order and
# ground truth). The regex baseline is recomputed from the dataset with the
# patterns of the matching language, and the majority-class floor is stored.
#
# Usage (from repo root):
#   python experimentos/build_matrix_n96.py --condition mixed

import argparse
import csv
import json
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
sys.path.insert(0, os.path.join(_ROOT, "dataset_v2"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from run_condition import CONDITIONS
from build_dataset_n96 import REGEX as REGEX_ES
from build_dataset_n96_en import REGEX_EN

LOCAL_MODELS = ["Gemma-2-9B-it", "Mistral-7B-Instruct-v0.2",
                "Qwen2.5-7B-Instruct", "Phi-3.5-mini-instruct"]
PRED_RE = re.compile(r"^\s+(\S+): real=([01]) pred=([01])\s*$")
MODEL_RE = re.compile(r"^\s+Modelo: (\S+)")
EXP_RE = re.compile(r"^\s+EXPERIMENT (\d) —")


def f1(y, p):
    tp = sum(t == 1 and q == 1 for t, q in zip(y, p))
    fp = sum(t == 0 and q == 1 for t, q in zip(y, p))
    fn = sum(t == 1 and q == 0 for t, q in zip(y, p))
    return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0


def parse(path):
    """Returns {model: [(id, real, pred), ...]} for one log (last complete run per model)."""
    rows, model = {}, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = MODEL_RE.match(line)
            if m:
                model = m.group(1)
                rows[model] = []
                continue
            m = PRED_RE.match(line)
            if m and model:
                rows[model].append((m.group(1), int(m.group(2)), int(m.group(3))))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=sorted(CONDITIONS))
    args = ap.parse_args()
    cond = CONDITIONS[args.condition]

    with open(os.path.join(_ROOT, cond["dataset"]), encoding="utf-8") as fh:
        dataset = json.load(fh)
    ids = [a["id_muestra"] for a in dataset]
    y_true = [a["etiqueta_clase"] for a in dataset]
    n = len(dataset)

    log_dir = os.path.join(_ROOT, "resultados", "n96", args.condition)
    predictions, sources, errors = {}, {}, []
    for fname in sorted(os.listdir(log_dir)):
        m = re.fullmatch(r"(gemini_)?exp(\d)\.txt", fname)
        if not m:
            continue
        exp = m.group(2)
        for model, rows in parse(os.path.join(log_dir, fname)).items():
            if len(rows) != n:
                errors.append(f"{fname} {model}: {len(rows)} predictions (expected {n}); skipped")
                continue
            if [r[0] for r in rows] != ids:
                errors.append(f"{fname} {model}: artifact order mismatch")
                continue
            if [r[1] for r in rows] != y_true:
                errors.append(f"{fname} {model}: ground-truth mismatch")
                continue
            predictions.setdefault(model, {})[exp] = [r[2] for r in rows]
            sources.setdefault(model, {})[exp] = f"resultados/n96/{args.condition}/{fname}"

    english = args.condition == "en"
    patterns = REGEX_EN if english else REGEX_ES
    regex_preds = [1 if re.search(patterns[a["meta_regla"]], a["contenido_texto"], re.IGNORECASE)
                   else 0 for a in dataset]

    artifacts = [{
        "index": i, "id": a["id_muestra"], "meta_rule": a["meta_regla"],
        "artifact_type": a["tipo_artefacto"], "label": a["etiqueta_clase"],
        "scenario": a["escenario"], "origin": a.get("origen"),
        "adversarial": a.get("adversarial"),
    } for i, a in enumerate(dataset)]

    ordered = {m: predictions[m] for m in LOCAL_MODELS if m in predictions}
    ordered.update({m: v for m, v in predictions.items() if m not in ordered})

    out = {
        "description": f"Biblio-VSE v2 prediction matrix, N={n}, condition={args.condition} "
                       f"(dataset={cond['dataset']}, prompts={cond['prompt_lang']}, "
                       f"anchors={cond['anchors']}, RAG corpus={cond['corpus']}).",
        "condition": args.condition,
        "condition_settings": cond,
        "artifacts": artifacts,
        "ground_truth": y_true,
        "regex_baseline": regex_preds,
        "majority_class_f1": round(f1(y_true, [1] * n), 4),
        "predictions": ordered,
        "sources": sources,
    }
    base = os.path.join(_DIR, f"predictions_n96_{args.condition}")
    with open(base + ".json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    with open(base + ".csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["artifact_id", "meta_rule", "artifact_type", "scenario", "adversarial",
                    "origin", "ground_truth", "system", "experiment", "prediction"])
        for a in artifacts:
            meta = [a["id"], a["meta_rule"], a["artifact_type"], a["scenario"],
                    a["adversarial"] or "", a["origin"], a["label"]]
            w.writerow(meta + ["regex_baseline", "", regex_preds[a["index"]]])
            for model, exps in ordered.items():
                for exp in sorted(exps, key=int):
                    w.writerow(meta + [model, exp, exps[exp][a["index"]]])

    print(f"[+] {args.condition}: N={n}, regex F1={f1(y_true, regex_preds):.4f}, "
          f"majority F1={out['majority_class_f1']:.4f}")
    for model, exps in ordered.items():
        cells = "  ".join(f"E{e}={f1(y_true, exps[e]):.3f}" for e in sorted(exps, key=int))
        print(f"    {model:<28} {cells}")
    for e in errors:
        print("  [!]", e)
    print(f"[+] Wrote {base}.json / .csv")


if __name__ == "__main__":
    main()
