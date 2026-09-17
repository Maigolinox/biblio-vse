# BUILD BIBLIO-VSE v2 (N=96, Spanish)
#
# 1. Loads the original N=32 benchmark (dataset_isomorfico.json, kept unchanged
#    as the archival v1 used in the first submission).
# 2. Makes the four duplicated artifact IDs unique, using the names already
#    used in the manuscript (SMP-GOBERNANZA-SRC/DOC-POS, SMP-TRAZABILIDAD-POS-A/B).
# 3. Removes label-revealing comments from six original artifacts (e.g.
#    "# MAL: Credenciales en texto plano", "viola CALIDAD"). These comments
#    state the ground truth inside the artifact and would let a model or a
#    lexical baseline read the label instead of judging the evidence.
# 4. Appends the 64 artifacts of the v2 extension (extension_es_*.py).
# 5. Adds a mutation-scenario identifier ("escenario") to every artifact; it is
#    the dependence unit used by the scenario-level permutation test.
# 6. Recomputes simple size metrics and validates balance and uniqueness.
#
# Usage (from repo root):  python dataset_v2/build_dataset_n96.py
# Output: dataset_isomorfico_n96.json

import json
import os
import re
import sys
from collections import Counter

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import extension_es_a
import extension_es_b
import extension_es_c

V1_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")
OUT_PATH = os.path.join(_ROOT, "dataset_isomorfico_n96.json")

RENAMES = {  # index in v1 -> unique id
    5: "SMP-GOBERNANZA-SRC-POS",
    6: "SMP-GOBERNANZA-DOC-POS",
    10: "SMP-TRAZABILIDAD-POS-A",
    11: "SMP-TRAZABILIDAD-POS-B",
}

# (artifact id, exact text to remove/replace, replacement)
SCRUB = [
    ("SMP-CALIDAD-NEG", "import sys,os,time,json,random  # imports no usados — viola CALIDAD",
     "import sys,os,time,json,random"),
    ("SMP-CALIDAD-NEG", "    # Sin docstring ni referencia de requerimiento (RF_XX/US_XX)\n", ""),
    ("SMP-CALIDAD-NEG", "    x=id  # nombre de variable no descriptivo — viola CALIDAD", "    x=id"),
    ("SMP-CALIDAD-NEG", '"v":x*3.14})  # magic number', '"v":x*3.14})'),
    ("SMP-CALIDAD-NEG", '"v":x*1.5})  # magic number', '"v":x*1.5})'),
    ("SMP-SEGURIDAD-NEG", "# MAL: Credenciales en texto plano\n", ""),
    ("SMP-TRAZABILIDAD-NEG",
     "    # Función sin docstring, sin ID de requerimiento, introducida sin autorización\n", ""),
    ("SMP-TRAZABILIDAD-NEG",
     "    # No hay referencia a RF_XX, US_XX ni ningún identificador de requerimiento\n", ""),
    ("SMP-RESPALDO-NEG", 'echo "Desplegando directo a produccion sin respaldar"',
     'echo "Desplegando directo a produccion"'),
    ("SMP-INFRA-NEG", "# MAL: Permite cualquier host o IPs públicas explícitas\n", ""),
    ("ADV-B-PRUEBAS-NEG",
     "        # Solo verifica que el servidor responde, no valida comportamiento funcional\n", ""),
]

# Regex baseline patterns (copied from experimentos/classic_baseline.py) used to
# check that every adversarial artifact behaves as designed.
REGEX = {
    "DOCUMENTAL":   r"Código|Versión|Fecha de Vigencia|BVSE-[A-Z]+-\d+",
    "CALIDAD":      r"linter|flake8|Lista de Cotejo|pruebas unitarias|magic numbers",
    "GOBERNANZA":   r"Aprobado|Firma Digital|Autoriza|BVSE-REQ-\d+",
    "SEGURIDAD":    r"os\.environ|environ\.get|getenv",
    "TRAZABILIDAD": r"RF_\d+|US_\d+|ID Requerimiento|Caso de Prueba Asociado",
    "PRUEBAS":      r"Resultado Esperado|Entorno:|Pasos:|Caso de Prueba:",
    "RESPALDO":     r"backup|pg_dump|dump|restore|respaldo",
    "ACUERDOS":     r"Acuerdo\s+\d+|Responsable:|Estado:",
    "INFRA":        r"biblioteca\.local|\.internal|entornos?\s+autorizado",
}


def size_metrics(rec):
    text = rec["contenido_texto"]
    m = {"lineas_totales": len(text.splitlines()), "longitud_caracteres": len(text)}
    if rec["tipo_artefacto"] == "documento_texto":
        m["conteo_palabras"] = len(text.split())
    elif rec["tipo_artefacto"] == "codigo_fuente":
        try:
            from radon.complexity import cc_visit
            blocks = cc_visit(text)
            m["complejidad_ciclomatica_VG"] = (
                sum(b.complexity for b in blocks) / len(blocks) if blocks else 0
            )
        except (ImportError, SyntaxError):
            pass
    return m


def original_scenario(rec):
    rule = rec["meta_regla"].lower()
    return f"orig-adv-{rule}" if rec["id_muestra"].startswith("ADV-") else f"orig-{rule}"


def main():
    with open(V1_PATH, encoding="utf-8") as fh:
        v1 = json.load(fh)
    assert len(v1) == 32

    originals = []
    for i, rec in enumerate(v1):
        rec = dict(rec)
        rec["id_muestra"] = RENAMES.get(i, rec["id_muestra"])
        rec["escenario"] = original_scenario(rec)
        rec["origen"] = "original_v1"
        originals.append(rec)

    by_id = {r["id_muestra"]: r for r in originals}
    for art_id, old, new in SCRUB:
        text = by_id[art_id]["contenido_texto"]
        if old not in text:
            sys.exit(f"scrub target not found in {art_id}: {old!r}")
        by_id[art_id]["contenido_texto"] = text.replace(old, new, 1)
        by_id[art_id]["depurado_v2"] = True

    extension = extension_es_a.ARTIFACTS + extension_es_b.ARTIFACTS + extension_es_c.ARTIFACTS
    dataset = originals + extension
    for rec in dataset:
        rec["metricas_isomorfismo"] = size_metrics(rec)

    ids = [r["id_muestra"] for r in dataset]
    dup = [k for k, v in Counter(ids).items() if v > 1]
    assert not dup, f"duplicate ids: {dup}"
    assert len(dataset) == 96, len(dataset)
    labels = Counter(r["etiqueta_clase"] for r in dataset)
    assert labels[0] == 48 and labels[1] == 48, labels

    # Adversarial sanity check: Type-B must trigger the regex (predict 1) and
    # Type-C must evade it (predict 0).
    problems = []
    for r in dataset:
        hit = re.search(REGEX[r["meta_regla"]], r["contenido_texto"], re.IGNORECASE) is not None
        if r.get("adversarial") == "tipo_b" and not hit:
            problems.append(f"{r['id_muestra']}: Type-B does not trigger regex")
        if r.get("adversarial") == "tipo_c" and hit:
            problems.append(f"{r['id_muestra']}: Type-C triggers regex")
    if problems:
        sys.exit("adversarial design violations:\n  " + "\n  ".join(problems))

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, indent=1, ensure_ascii=False)

    print(f"[+] Wrote {OUT_PATH}: N={len(dataset)}, labels={dict(labels)}")
    print("    per rule (neg/pos):")
    for rule in sorted({r['meta_regla'] for r in dataset}):
        c = Counter(r["etiqueta_clase"] for r in dataset if r["meta_regla"] == rule)
        print(f"      {rule:<13} {c[0]:>2}/{c[1]:<2}")
    print("    types:", dict(Counter(r["tipo_artefacto"] for r in dataset)))
    print("    adversarial:", dict(Counter(r.get("adversarial", "none") for r in dataset)))
    print("    scenarios:", len({r["escenario"] for r in dataset}))


if __name__ == "__main__":
    main()
