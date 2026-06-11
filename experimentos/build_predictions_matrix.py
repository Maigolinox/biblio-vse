# BUILD CANONICAL PREDICTION MATRIX (N=32 × 8 experiments × 4 models)
#
# Parses the consolidated experiment logs and emits a single canonical,
# machine-readable matrix of all per-artifact predictions:
#
#   - Exp 1, 2, 3, 5 (non-steering)        ← resultados_conglomerados_actualizados_03062026.txt
#   - Exp 4, 6, 7, 8 (steering, ES anchors) ← resultados_new_layer.txt
#   - Regex rule-based baseline             ← resultados_conglomerados_actualizados_03062026.txt
#
# For Exp 4 each model block contains the α-sensitivity sweep followed by a
# final α=0.8 run; the final run (last 32 predictions) is the canonical one.
#
# Output:
#   experimentos/predictions_n32.json  (full matrix + metadata)
#   experimentos/predictions_n32.csv   (long format, one row per prediction)
#
# Every cell is validated against the F1 values reported in the manuscript
# (access.tex, Table tab:full_results); the script fails loudly on mismatch.

import csv
import json
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOG_MAIN = os.path.join(_ROOT, "resultados_conglomerados_actualizados_03062026.txt")
LOG_ES = os.path.join(_ROOT, "resultados_new_layer.txt")
DATASET = os.path.join(_ROOT, "dataset_isomorfico.json")

MODELS = ["Gemma-2-9B-it", "Mistral-7B-Instruct-v0.2",
          "Qwen2.5-7B-Instruct", "Phi-3.5-mini-instruct"]

# F1 values reported in access.tex Table tab:full_results, used for validation
EXPECTED_F1 = {
    "Gemma-2-9B-it":            {1: 0.7368, 2: 0.8000, 3: 0.7857, 4: 0.8205,
                                 5: 0.8750, 6: 0.8571, 7: 0.8125, 8: 0.8571},
    "Mistral-7B-Instruct-v0.2": {1: 0.6857, 2: 0.8235, 3: 0.7742, 4: 0.6667,
                                 5: 0.8235, 6: 0.8485, 7: 0.8108, 8: 0.8000},
    "Qwen2.5-7B-Instruct":      {1: 0.7273, 2: 0.8235, 3: 0.7742, 4: 0.7027,
                                 5: 0.8125, 6: 0.8235, 7: 0.7586, 8: 0.8125},
    "Phi-3.5-mini-instruct":    {1: 0.7059, 2: 0.6429, 3: 0.8000, 4: 0.7556,
                                 5: 0.7742, 6: 0.8421, 7: 0.7442, 8: 0.7805},
}

PRED_RE = re.compile(r"^\s+(\S+): real=([01]) pred=([01])\s*$")
EXP_RE = re.compile(r"^\s+EXPERIMENT (\d) —")
MODEL_RE = re.compile(r"^\s+Modelo: (\S+)")


def f1_score(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    if 2 * tp + fp + fn == 0:
        return 0.0
    return 2 * tp / (2 * tp + fp + fn)


def parse_log(path, wanted_exps):
    """Returns {exp: {model: [(artifact_id, real, pred), ...]}} keeping every
    run in order; the caller decides which run (e.g. final α=0.8) is canonical."""
    runs = {}
    exp = model = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = EXP_RE.match(line)
            if m:
                exp = int(m.group(1))
                model = None
                continue
            m = MODEL_RE.match(line)
            if m:
                model = m.group(1)
                continue
            m = PRED_RE.match(line)
            if m and exp in wanted_exps and model:
                runs.setdefault(exp, {}).setdefault(model, []).append(
                    (m.group(1), int(m.group(2)), int(m.group(3))))
    return runs


def parse_regex_baseline(path):
    """Parses the classical regex baseline table (GT/Pred columns)."""
    preds = []
    in_block = False
    row_re = re.compile(r"^\s+(\S+)\s+\S+\s+([01])\s+([01])\s+[✓✗]")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "CLASSICAL RULE-BASED BASELINE" in line:
                in_block = True
            if in_block:
                m = row_re.match(line)
                if m:
                    preds.append((m.group(1), int(m.group(2)), int(m.group(3))))
                if "RESULTS — Classical Baseline" in line:
                    break
    return preds


def main():
    with open(DATASET, encoding="utf-8") as fh:
        dataset = json.load(fh)
    artifacts = [{"index": i,
                  "id": a["id_muestra"],
                  "meta_rule": a["meta_regla"],
                  "artifact_type": a["tipo_artefacto"],
                  "label": a["etiqueta_clase"]} for i, a in enumerate(dataset)]
    y_true = [a["label"] for a in artifacts]
    n = len(artifacts)
    assert n == 32, f"expected 32 artifacts, got {n}"

    main_runs = parse_log(LOG_MAIN, wanted_exps={1, 2, 3, 5})
    es_runs = parse_log(LOG_ES, wanted_exps={4, 6, 7, 8})

    matrix = {}   # matrix[model][exp] = [pred, ...] aligned with dataset order
    errors = []
    for exp, source in [(1, main_runs), (2, main_runs), (3, main_runs),
                        (5, main_runs), (4, es_runs), (6, es_runs),
                        (7, es_runs), (8, es_runs)]:
        for model in MODELS:
            rows = source.get(exp, {}).get(model, [])
            if len(rows) % n != 0 or not rows:
                errors.append(f"Exp {exp} {model}: {len(rows)} prediction lines "
                              f"(not a multiple of {n})")
                continue
            final = rows[-n:]  # last full run = canonical (post-sweep for Exp 4)
            ids = [r[0] for r in final]
            reals = [r[1] for r in final]
            preds = [r[2] for r in final]
            if ids != [a["id"] for a in artifacts]:
                errors.append(f"Exp {exp} {model}: artifact order mismatch")
                continue
            if reals != y_true:
                errors.append(f"Exp {exp} {model}: ground-truth mismatch")
                continue
            got = f1_score(y_true, preds)
            want = EXPECTED_F1[model][exp]
            if abs(got - want) > 5e-4:
                errors.append(f"Exp {exp} {model}: parsed F1={got:.4f} != "
                              f"manuscript F1={want:.4f}")
            matrix.setdefault(model, {})[exp] = preds

    regex_rows = parse_regex_baseline(LOG_MAIN)
    regex_preds = None
    if len(regex_rows) == n and [r[0] for r in regex_rows] == [a["id"] for a in artifacts]:
        regex_preds = [r[2] for r in regex_rows]
        got = f1_score(y_true, regex_preds)
        if abs(got - 0.6471) > 5e-4:
            errors.append(f"Regex baseline: parsed F1={got:.4f} != 0.6471")
    else:
        errors.append(f"Regex baseline: parsed {len(regex_rows)} rows")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    out = {
        "description": "Canonical per-artifact prediction matrix, N=32 artifacts x "
                       "8 experiments x 4 models (+ regex baseline). Exp 1/2/3/5 from "
                       "resultados_conglomerados_actualizados_03062026.txt; Exp 4/6/7/8 "
                       "(Spanish-anchor steering, final alpha=0.8 runs) from "
                       "resultados_new_layer.txt.",
        "artifacts": artifacts,
        "ground_truth": y_true,
        "regex_baseline": regex_preds,
        "predictions": matrix,
    }
    json_path = os.path.join(_DIR, "predictions_n32.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    csv_path = os.path.join(_DIR, "predictions_n32.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["artifact_id", "meta_rule", "artifact_type", "ground_truth",
                    "system", "experiment", "prediction"])
        for a in artifacts:
            i = a["index"]
            w.writerow([a["id"], a["meta_rule"], a["artifact_type"], a["label"],
                        "regex_baseline", "", regex_preds[i]])
            for model in MODELS:
                for exp in range(1, 9):
                    w.writerow([a["id"], a["meta_rule"], a["artifact_type"],
                                a["label"], model, exp, matrix[model][exp][i]])

    print(f"[+] All 32 model-experiment cells + regex baseline validated against "
          f"manuscript F1 values.")
    print(f"[+] Wrote {json_path}")
    print(f"[+] Wrote {csv_path}")


if __name__ == "__main__":
    main()
