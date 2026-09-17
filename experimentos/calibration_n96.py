# DISTRIBUTIONAL CALIBRATION RE-MEASUREMENT (Biblio-VSE v2, N=96)
#
# Re-measures the calibration metrics of the manuscript for a synthetic
# benchmark and, when the private reference repository is available locally,
# for D_private with exactly the same code. Only aggregate statistics are
# printed or saved (the disclosure agreement covers aggregates only).
#
# Metrics
#   code artifacts : McCabe V(G) (radon), AST depth
#   doc/CI artifacts: Gunning Fog, "lexical density" as operationalized in the
#                     manuscript (type-token ratio, TTR = unique/total words),
#                     plus two length-robust lexical measures added in revision:
#                       - MATTR-50: moving-average TTR over 50-word windows
#                         (Covington & McFall, 2010), insensitive to text length;
#                       - content-word density: share of tokens that are not
#                         function words (Spanish + English stopword lists).
#                     Word count is reported because raw TTR decreases
#                     mechanically with document length.
#
# For each metric: means, SDs, |Δμ|, the manuscript tolerance where one exists,
# and a Welch TOST equivalence test.
#
# Usage (from repo root):
#   python experimentos/calibration_n96.py --dataset dataset_isomorfico_n96.json \
#       --private-dir "<path to D_private>"
# Output: experimentos/calibration_n96.json (aggregates only)

import argparse
import json
import os
import re
import statistics
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import isomorphism_metrics as iso
import measure_private_repo as mpr

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")

STOPWORDS = set("""
a al algo algunas algunos ante antes aquí así aun aunque cada como con contra cual
cuando de del desde donde dos el ella ellas ellos en entre era es esa esas ese eso
esos esta estas este esto estos fue fueron ha han hasta hay la las le les lo los
más me mi mientras muy nada ni no nos o otra otras otro otros para pero poco por
porque que quien se sea según ser si sin sino sobre son su sus también tan te tiene
todo todos tu un una unas uno unos y ya va van
a an and are as at be been but by can do does for from had has have if in into is
it its may must no not of on or should so such than that the their them then there
these they this those to was were which while will with would you your
""".split())

TOLERANCES = {"vg": 0.5, "ast_depth": 2.0, "fog": 1.0, "lex_density": 8.0}


def words(text):
    return WORD_RE.findall(text.lower())


def mattr(text, window=50):
    toks = words(text)
    if len(toks) < window:
        return len(set(toks)) / len(toks) * 100 if toks else 0.0
    ratios = [len(set(toks[i:i + window])) / window
              for i in range(len(toks) - window + 1)]
    return sum(ratios) / len(ratios) * 100


def content_density(text):
    toks = words(text)
    return sum(1 for t in toks if t not in STOPWORDS) / len(toks) * 100 if toks else 0.0


def summarize(values):
    return {"n": len(values), "mean": round(statistics.mean(values), 3),
            "stdev": round(statistics.stdev(values), 3) if len(values) > 1 else 0.0,
            "median": round(statistics.median(values), 3)}


def measure(code_texts, doc_texts):
    return {
        "vg": [iso.cyclomatic_complexity(t) for t in code_texts],
        "ast_depth": [iso.ast_depth(t) for t in code_texts],
        "fog": [iso.gunning_fog(t) for t in doc_texts],
        "lex_density": [iso.lexical_density(t) for t in doc_texts],
        "mattr50": [mattr(t) for t in doc_texts],
        "content_density": [content_density(t) for t in doc_texts],
        "word_count": [len(t.split()) for t in doc_texts],
    }


def private_texts(root):
    py_files, doc_files = mpr.collect_files(root, "all")
    code = []
    for path in py_files:
        text = mpr.read_text(path)
        if text.strip():
            try:
                compile(text, path, "exec")
                code.append(text)
            except (SyntaxError, ValueError):
                continue
    docs = []
    for path in doc_files:
        ext = os.path.splitext(path)[1].lower()
        text = (mpr.read_pdf(path) if ext == ".pdf" else
                mpr.read_docx(path) if ext in (".docx", ".doc") else mpr.read_text(path))
        if text.strip():
            docs.append(text)
    return code, docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=os.path.join(_ROOT, "dataset_isomorfico_n96.json"))
    ap.add_argument("--private-dir", default=None)
    ap.add_argument("--out", default=os.path.join(_DIR, "calibration_n96.json"))
    args = ap.parse_args()

    with open(args.dataset, encoding="utf-8") as fh:
        dataset = json.load(fh)
    code_types = {"codigo_fuente", "source_code"}
    synth = measure([a["contenido_texto"] for a in dataset if a["tipo_artefacto"] in code_types],
                    [a["contenido_texto"] for a in dataset if a["tipo_artefacto"] not in code_types])
    out = {"dataset": os.path.basename(args.dataset),
           "synthetic": {k: summarize(v) for k, v in synth.items()}}

    if args.private_dir and os.path.isdir(args.private_dir):
        code, docs = private_texts(args.private_dir)
        priv = measure(code, docs)
        out["private_remeasured"] = {k: summarize(v) for k, v in priv.items()}
        # Length-matched TTR: TTR of the first 150 words of documents with >=150 words.
        def ttr150(texts):
            vals = []
            for t in texts:
                toks = t.split()
                if len(toks) >= 150:
                    vals.append(len(set(w.lower() for w in toks[:150])) / 150 * 100)
            return vals
        synth_docs = [a["contenido_texto"] for a in dataset if a["tipo_artefacto"] not in code_types]
        out["synthetic"]["ttr_first150"] = summarize(ttr150(synth_docs)) if len(ttr150(synth_docs)) > 1 else None
        out["private_remeasured"]["ttr_first150"] = summarize(ttr150(docs))

        out["comparison"] = {}
        for key in ["vg", "ast_depth", "fog", "lex_density", "mattr50", "content_density",
                    "ttr_first150", "word_count"]:
            s, p = out["synthetic"].get(key), out["private_remeasured"].get(key)
            if not s or not p:
                continue
            row = {"abs_diff": round(abs(s["mean"] - p["mean"]), 3)}
            eps = TOLERANCES.get(key, 8.0 if key in ("mattr50", "content_density", "ttr_first150") else None)
            if eps is not None:
                row["tolerance"] = eps
                row["within_tolerance"] = row["abs_diff"] <= eps
                t = iso.tost_welch(s["mean"], s["stdev"], s["n"], p["mean"], p["stdev"], p["n"], eps)
                row["tost_p_lower"], row["tost_p_upper"] = t["p_lower"], t["p_upper"]
                row["tost_equivalent"] = t["equivalent"]
            out["comparison"][key] = row

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
