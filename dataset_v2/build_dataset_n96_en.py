# BUILD BIBLIO-VSE v2 — ENGLISH EDITION (N=96)
#
# Produces the fully English benchmark used by the monolingual English
# condition. Starts from dataset_isomorfico_n96.json (Spanish) and replaces:
#   - contenido_texto with the English translation (en_*.py),
#   - meta_regla with the English rule name,
#   - tipo_artefacto with the English artifact-type name.
# Labels, IDs, scenarios, and adversarial annotations are unchanged, so the two
# editions are paired artifact by artifact.
#
# Translation policy: natural language (prose, comments, docstrings, string
# literals) and code identifiers are translated; hostnames, requirement and
# document IDs, hashes, and fabricated credentials are kept verbatim.
#
# The adversarial design is re-validated with English regex patterns that
# translate the Spanish baseline patterns (experimentos/classic_baseline.py).
#
# Usage (from repo root):  python dataset_v2/build_dataset_n96_en.py
# Output: dataset_isomorfico_n96_en.json

import json
import os
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import en_extension_a
import en_extension_b
import en_extension_c
import en_originals

ES_PATH = os.path.join(_ROOT, "dataset_isomorfico_n96.json")
OUT_PATH = os.path.join(_ROOT, "dataset_isomorfico_n96_en.json")

RULES_EN = {
    "DOCUMENTAL": "DOCUMENTATION", "CALIDAD": "QUALITY", "GOBERNANZA": "GOVERNANCE",
    "SEGURIDAD": "SECURITY", "TRAZABILIDAD": "TRACEABILITY", "PRUEBAS": "TESTING",
    "RESPALDO": "BACKUP", "ACUERDOS": "AGREEMENTS", "INFRA": "INFRA",
}
TYPES_EN = {"codigo_fuente": "source_code", "documento_texto": "text_document",
            "pipeline_ci": "ci_pipeline"}

REGEX_EN = {
    "DOCUMENTATION": r"\bCode\b|Version|Effective Date|BVSE-[A-Z]+-\d+",
    "QUALITY":       r"linter|flake8|Checklist|unit tests|magic numbers",
    "GOVERNANCE":    r"Approved|Digital Signature|Authoriz|BVSE-REQ-\d+",
    "SECURITY":      r"os\.environ|environ\.get|getenv",
    "TRACEABILITY":  r"RF_\d+|US_\d+|Requirement ID|Associated Test Case",
    "TESTING":       r"Expected Result|Environment:|Steps:|Test Case:",
    "BACKUP":        r"backup|pg_dump|dump|restore",
    "AGREEMENTS":    r"Agreement\s+\d+|Responsible:|Status:",
    "INFRA":         r"biblioteca\.local|\.internal|authorized\s+environments?",
}

# Frequent Spanish function words; any hit outside identifiers is reported for review.
SPANISH_RESIDUE = re.compile(
    r"\b(el|los|las|del|que|para|con|una|por|sistema|préstamo|usuario|pruebas|"
    r"respaldo|acuerdo|firma|versión|código|está|también|según)\b", re.IGNORECASE)
ALLOWED_RESIDUE = {"prestamos.biblioteca.local"}


def main():
    with open(ES_PATH, encoding="utf-8") as fh:
        dataset_es = json.load(fh)

    translations = {}
    for module in (en_originals, en_extension_a, en_extension_b, en_extension_c):
        overlap = translations.keys() & module.EN.keys()
        assert not overlap, f"duplicate translations: {overlap}"
        translations.update(module.EN)

    missing = [r["id_muestra"] for r in dataset_es if r["id_muestra"] not in translations]
    extra = translations.keys() - {r["id_muestra"] for r in dataset_es}
    assert not missing and not extra, f"missing={missing} extra={extra}"

    dataset_en, problems, residue = [], [], []
    for rec in dataset_es:
        new = dict(rec)
        new["contenido_texto"] = translations[rec["id_muestra"]].apply(rec["contenido_texto"])
        new["meta_regla"] = RULES_EN[rec["meta_regla"]]
        new["tipo_artefacto"] = TYPES_EN[rec["tipo_artefacto"]]
        new["idioma"] = "en"
        dataset_en.append(new)

        hit = re.search(REGEX_EN[new["meta_regla"]], new["contenido_texto"], re.IGNORECASE)
        if rec.get("adversarial") == "tipo_b" and not hit:
            problems.append(f"{rec['id_muestra']}: Type-B does not trigger English regex")
        if rec.get("adversarial") == "tipo_c" and hit:
            problems.append(f"{rec['id_muestra']}: Type-C triggers English regex ({hit.group()})")

        for m in SPANISH_RESIDUE.finditer(new["contenido_texto"]):
            line = new["contenido_texto"][max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
            if not any(a in line for a in ALLOWED_RESIDUE):
                residue.append(f"{rec['id_muestra']}: ...{line}...")

    if problems:
        sys.exit("adversarial design violations:\n  " + "\n  ".join(problems))

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(dataset_en, fh, indent=1, ensure_ascii=False)
    print(f"[+] Wrote {OUT_PATH}: N={len(dataset_en)}")
    if residue:
        print(f"[!] {len(residue)} possible untranslated fragments (review manually):")
        for r in residue:
            print("   ", r)


if __name__ == "__main__":
    main()
