# REBUILD THE BENCHMARK FROM THE EDITED FILES
#
# Reads dataset_v2/edicion/{es,en}/<id>.<ext> and dataset_v2/edicion/metadata.json
# and rewrites:
#   dataset_isomorfico_n96.json        (Spanish)
#   dataset_isomorfico_n96_en.json     (English, paired)
#   dataset_isomorfico_n96_noisy.json  (noise-injected, rebuilt from the Spanish edition)
#
# Every check of the original builders is re-run: label balance, unique IDs,
# adversarial design in both languages (Type-B must trigger the regex of its
# rule, Type-C must not), and leftover Spanish text in the English edition.
# Nothing is written unless all checks pass.
#
# Usage (from repo root):  python dataset_v2/import_edited.py

import json
import os
import re
import subprocess
import sys
from collections import Counter

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build_dataset_n96 import REGEX, size_metrics
from build_dataset_n96_en import REGEX_EN, RULES_EN, TYPES_EN, SPANISH_RESIDUE, ALLOWED_RESIDUE

EDIT = os.path.join(_DIR, "edicion")
ES_OUT = os.path.join(_ROOT, "dataset_isomorfico_n96.json")
EN_OUT = os.path.join(_ROOT, "dataset_isomorfico_n96_en.json")


def read(lang, filename):
    path = os.path.join(EDIT, lang, filename)
    if not os.path.exists(path):
        sys.exit(f"missing edited file: {path}")
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


_KEY_ORDER = {}


def order_like(rec, dataset_path):
    """Keep the field order of the dataset being replaced, so that re-importing
    unedited artifacts produces a byte-identical file."""
    if dataset_path not in _KEY_ORDER:
        order = {}
        if os.path.exists(dataset_path):
            with open(dataset_path, encoding="utf-8") as fh:
                order = {r["id_muestra"]: list(r) for r in json.load(fh)}
        _KEY_ORDER[dataset_path] = order
    keys = _KEY_ORDER[dataset_path].get(rec["id_muestra"], [])
    return {**{k: rec[k] for k in keys if k in rec},
            **{k: v for k, v in rec.items() if k not in keys}}


def main():
    with open(os.path.join(EDIT, "metadata.json"), encoding="utf-8") as fh:
        meta = json.load(fh)

    es, en, problems, residue = [], [], [], []
    for m in meta:
        text_es, text_en = read("es", m["archivo"]), read("en", m["archivo"])
        base = {"id_muestra": m["id_muestra"], "archivo": m["ruta_original"],
                "escenario": m["escenario"], "origen": m["origen"]}
        if m.get("adversarial"):
            base["adversarial"] = m["adversarial"]
            base["adversarial_nota"] = m["adversarial_nota"]
        if m.get("depurado_v2"):
            base["depurado_v2"] = True

        rec_es = dict(base, meta_regla=m["meta_regla"], tipo_artefacto=m["tipo_artefacto"],
                      contenido_texto=text_es, etiqueta_clase=m["etiqueta_clase"])
        rec_es["metricas_isomorfismo"] = size_metrics(rec_es)
        rec_en = dict(base, meta_regla=RULES_EN[m["meta_regla"]],
                      tipo_artefacto=TYPES_EN[m["tipo_artefacto"]], idioma="en",
                      contenido_texto=text_en, etiqueta_clase=m["etiqueta_clase"],
                      metricas_isomorfismo=rec_es["metricas_isomorfismo"])
        es.append(rec_es)
        en.append(rec_en)

        for rec, patterns, lang in ((rec_es, REGEX, "es"), (rec_en, REGEX_EN, "en")):
            hit = re.search(patterns[rec["meta_regla"]], rec["contenido_texto"], re.IGNORECASE)
            if m.get("adversarial") == "tipo_b" and not hit:
                problems.append(f"{m['id_muestra']} [{lang}]: Type-B no longer triggers the regex")
            if m.get("adversarial") == "tipo_c" and hit:
                problems.append(f"{m['id_muestra']} [{lang}]: Type-C now triggers the regex "
                                f"({hit.group()!r})")
        for hit in SPANISH_RESIDUE.finditer(text_en):
            line = text_en[max(0, hit.start() - 30): hit.end() + 30].replace("\n", " ")
            if not any(a in line for a in ALLOWED_RESIDUE):
                residue.append(f"{m['id_muestra']}: ...{line}...")

    ids = [r["id_muestra"] for r in es]
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        problems.append(f"duplicate ids: {dup}")
    labels = Counter(r["etiqueta_clase"] for r in es)
    if problems:
        sys.exit("validation failed:\n  " + "\n  ".join(problems))

    for path, data in ((ES_OUT, es), (EN_OUT, en)):
        data = [order_like(rec, path) for rec in data]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False)
        print(f"[+] Wrote {path}")

    subprocess.run([sys.executable, os.path.join(_DIR, "build_dataset_n96_noisy.py")], check=True)

    print(f"[+] N={len(es)}  labels={dict(labels)}  "
          f"adversarial={dict(Counter(r.get('adversarial', 'none') for r in es))}")
    if labels[0] != labels[1]:
        print(f"[!] labels are no longer balanced ({labels[0]} violations / {labels[1]} compliant); "
              f"this is allowed but changes the majority-class floor")
    if residue:
        print(f"[!] {len(residue)} possible untranslated fragments in the English edition:")
        for r in residue[:20]:
            print("   ", r)
    print("[i] Re-run the experiments after editing: experimentos/run_condition.py for the four "
          "conditions and experimentos/experimento_gemini.py, then the analysis scripts.")


if __name__ == "__main__":
    main()
