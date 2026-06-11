# LEXICAL (NON-LLM) BASELINES — N=32
#
# Added after external review: outperforming the single handcrafted regex
# baseline does not by itself establish semantic reasoning, because models
# could exploit other lexical/formatting cues. These shallow lexical
# classifiers quantify how far surface word statistics alone go on the
# benchmark:
#
#   - TF-IDF (word 1-2 grams) + Logistic Regression
#   - TF-IDF (word 1-2 grams) + Linear SVM
#   - TF-IDF (char 3-5 grams) + Logistic Regression
#
# Evaluation: leave-one-meta-rule-group-out cross-validation (9 folds).
# Holding out an entire meta-rule cluster prevents the classifier from
# exploiting within-cluster lexical overlap between the train and test
# artifacts (the same leakage the grouped bootstrap guards against), so the
# resulting F1 measures transferable surface-cue learning, not memorisation
# of the held-out family.
#
# Usage (from repo root):
#   python experimentos/lexical_baselines.py
#
# Output: console report + experimentos/lexical_baselines_n32.json

import json
import os
import sys
from collections import defaultdict

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

DATASET = os.path.join(_ROOT, "dataset_isomorfico.json")
OUT_PATH = os.path.join(_DIR, "lexical_baselines_n32.json")

BASELINES = {
    "tfidf_word_logreg": lambda: make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True),
        LogisticRegression(max_iter=2000, C=1.0)),
    "tfidf_word_linearsvm": lambda: make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True),
        LinearSVC(C=1.0)),
    "tfidf_char_logreg": lambda: make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1,
                        sublinear_tf=True),
        LogisticRegression(max_iter=2000, C=1.0)),
}


def confusion(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    return tp, tn, fp, fn


def f1(y_true, y_pred):
    tp, tn, fp, fn = confusion(y_true, y_pred)
    return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0


def main():
    with open(DATASET, encoding="utf-8") as fh:
        dataset = json.load(fh)
    texts = [a["contenido_texto"] for a in dataset]
    labels = [a["etiqueta_clase"] for a in dataset]
    rules = [a["meta_regla"] for a in dataset]
    ids = [a["id_muestra"] for a in dataset]

    groups = defaultdict(list)
    for i, r in enumerate(rules):
        groups[r].append(i)

    print("=" * 88)
    print("  LEXICAL (NON-LLM) BASELINES — leave-one-meta-rule-group-out CV "
          f"({len(groups)} folds, N={len(dataset)})")
    print("=" * 88)

    results = {}
    for name, factory in BASELINES.items():
        preds = [None] * len(dataset)
        for rule, test_idx in sorted(groups.items()):
            train_idx = [i for i in range(len(dataset)) if i not in test_idx]
            clf = factory()
            clf.fit([texts[i] for i in train_idx],
                    [labels[i] for i in train_idx])
            for i in test_idx:
                preds[i] = int(clf.predict([texts[i]])[0])
        tp, tn, fp, fn = confusion(labels, preds)
        score = f1(labels, preds)
        acc = (tp + tn) / len(dataset)
        results[name] = {
            "f1": round(score, 4),
            "accuracy": round(acc, 4),
            "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
            "predictions": {ids[i]: preds[i] for i in range(len(dataset))},
        }
        print(f"  {name:<24} F1={score:.4f}  Acc={acc:.4f}  "
              f"(TP={tp} TN={tn} FP={fp} FN={fn})")

    print()
    print("  Evaluation: each meta-rule cluster is held out entirely; the")
    print("  classifier never sees lexical material from the tested family.")

    out = {
        "design": "TF-IDF baselines, leave-one-meta-rule-group-out CV "
                  "(9 folds); guards against within-cluster lexical leakage.",
        "results": results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"\n[+] Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
