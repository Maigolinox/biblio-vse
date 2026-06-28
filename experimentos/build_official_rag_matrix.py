"""Build an N=32 prediction matrix with official-corpus RAG experiments.

Non-RAG experiments (1, 2, 4, 6) are copied from predictions_n32.json.
Official ISO/IEC 29110 logs supply experiments 3, 5, 7, and 8.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "predictions_n32.json")
OUT_PATH = os.path.join(HERE, "predictions_n32_official_rag.json")
LOGS = {exp: os.path.join(HERE, f"resultados_rag_official_exp{exp}.txt")
        for exp in (3, 5, 7, 8)}

MODEL_RE = re.compile(r"^\s+Modelo: (\S+)")
PRED_RE = re.compile(r"^\s+(\S+): real=([01]) pred=([01])\s*$")


def f1_score(y_true, y_pred):
    tp = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred))
    fp = sum(t == 0 and p == 1 for t, p in zip(y_true, y_pred))
    fn = sum(t == 1 and p == 0 for t, p in zip(y_true, y_pred))
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0


def parse_log(path):
    parsed = {}
    model = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            match = MODEL_RE.match(line)
            if match:
                model = match.group(1)
                parsed.setdefault(model, [])
                continue
            match = PRED_RE.match(line)
            if match and model:
                parsed[model].append(
                    (match.group(1), int(match.group(2)), int(match.group(3)))
                )
    return parsed


def main():
    with open(BASE_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    ids = [artifact["id"] for artifact in data["artifacts"]]
    y_true = data["ground_truth"]
    models = list(data["predictions"])

    for exp, path in LOGS.items():
        parsed = parse_log(path)
        for model in models:
            rows = parsed.get(model, [])
            if len(rows) != len(ids):
                raise ValueError(f"Exp {exp} {model}: expected {len(ids)} rows, got {len(rows)}")
            if [row[0] for row in rows] != ids:
                raise ValueError(f"Exp {exp} {model}: artifact order mismatch")
            if [row[1] for row in rows] != y_true:
                raise ValueError(f"Exp {exp} {model}: ground-truth mismatch")
            preds = [row[2] for row in rows]
            data["predictions"][model][str(exp)] = preds
            print(f"Exp {exp} {model}: F1={f1_score(y_true, preds):.4f}")

    data["description"] = (
        "Canonical N=32 matrix using the official ISO/IEC 29110 Part 5-1-2 "
        "PDF for RAG experiments 3, 5, 7, and 8; non-RAG experiments are "
        "copied from predictions_n32.json."
    )
    data["rag_corpus"] = {
        "mode": "official",
        "file": "NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf",
        "characters": 96552,
        "chunks": 271,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    print(f"[+] Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
