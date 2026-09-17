# BUILD THE NOISE-INJECTED STRESS-TEST EDITION OF BIBLIO-VSE v2 (N=96, Spanish)
#
# Purpose (reviewer concern on transfer to noisy, non-standardized enterprise
# codebases): each artifact is embedded in label-preserving "enterprise noise"
# of the kind found in real repositories, while the compliance evidence itself
# is left untouched:
#   - source code : license/ownership header, unrelated but well-formed helper
#                   functions, a legacy block kept for reference;
#   - documents   : wiki-export residue (breadcrumbs, HTML entities), a
#                   confidentiality banner, an unrelated FAQ/glossary annex;
#   - CI pipelines: header comments and unrelated jobs (static assets,
#                   documentation site, chat notification).
#
# Label preservation is enforced by construction:
#   1. every noise block is checked against the regex patterns of ALL nine
#      meta-rules, so noise adds no compliance (or violation) keyword;
#   2. noise blocks contain no credentials, hosts, requirement/test IDs,
#      approvals, backup commands, version/date fields, or agreements;
#   3. QUALITY artifacts only receive noise written in clean style
#      (docstrings, named constants, used imports, no dead code), so the style
#      verdict of the original code is unchanged.
#
# Selection is deterministic (seeded by artifact ID).
#
# Usage (from repo root):  python dataset_v2/build_dataset_n96_noisy.py
# Output: dataset_isomorfico_n96_noisy.json

import hashlib
import json
import os
import random
import re
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, _DIR)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from build_dataset_n96 import REGEX

SRC_PATH = os.path.join(_ROOT, "dataset_isomorfico_n96.json")
OUT_PATH = os.path.join(_ROOT, "dataset_isomorfico_n96_noisy.json")

# ── Source-code noise ─────────────────────────────────────────────────────────
CODE_HEADERS = [
    "# -*- coding: utf-8 -*-\n# Proyecto Biblio-VSE — Biblioteca Municipal\n"
    "# Uso interno. Prohibida su distribución fuera de la institución.\n"
    "# Mantenido por el equipo de desarrollo; dudas en el canal #biblio-dev.\n\n",
    "#\n# Este archivo forma parte del sistema de préstamos de la biblioteca.\n"
    "# Última limpieza de formato realizada con el editor del equipo.\n#\n\n",
    "# ============================================================\n"
    "#  Módulo del sistema de préstamos\n"
    "#  Nota: conservar la codificación UTF-8 al editar este archivo\n"
    "# ============================================================\n\n",
]

CODE_HELPERS_CLEAN = [
    '\n\ndef formatear_nombre_completo(nombre, apellido):\n'
    '    """Devuelve el nombre y apellido con mayúscula inicial."""\n'
    '    return f"{nombre.strip().title()} {apellido.strip().title()}"\n',
    '\n\nSEPARADOR_CSV = ";"\n\n\n'
    'def unir_campos(campos):\n'
    '    """Une una lista de campos de texto con el separador del reporte."""\n'
    '    return SEPARADOR_CSV.join(str(campo) for campo in campos)\n',
    '\n\ndef es_isbn_con_guiones(texto):\n'
    '    """Indica si el texto contiene guiones típicos de un ISBN impreso."""\n'
    '    return texto.count("-") >= 3\n',
    '\n\nMESES = (\n    "enero", "febrero", "marzo", "abril", "mayo", "junio",\n'
    '    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",\n)\n\n\n'
    'def nombre_mes(numero):\n'
    '    """Devuelve el nombre del mes a partir de su número (1-12)."""\n'
    '    return MESES[numero - 1]\n',
]

CODE_LEGACY = [
    "\n\n# --- bloque anterior conservado como referencia de la migración a Django ---\n"
    "# def pagina_inicio_vieja(peticion):\n"
    "#     return render(peticion, 'inicio_viejo.html', {})\n",
    "\n\n# NOTA DE MANTENIMIENTO: la función de impresión de etiquetas se movió al\n"
    "# módulo de catálogo en la reorganización de carpetas del año pasado.\n",
]

# ── Document noise ────────────────────────────────────────────────────────────
DOC_HEADERS = [
    "Inicio > Espacio del proyecto > Documentación&nbsp;&nbsp;|&nbsp;&nbsp;Exportado desde la wiki interna\n"
    "<br>\n\n",
    "> **Aviso de confidencialidad:** este material es de uso interno de la Biblioteca Municipal\n"
    "> y no debe reenviarse a terceros.\n\n",
    "[Volver al índice](../README.md) · [Ver historial en la wiki](#)\n\n---\n\n",
]

DOC_ANNEXES = [
    "\n\n---\n\n## Anexo: preguntas frecuentes del personal\n\n"
    "**¿Cómo cambio mi contraseña de la computadora de préstamo?**\n"
    "Pide al área de soporte que te envíe el enlace de cambio; nunca la compartas con tus compañeros.\n\n"
    "**¿Qué hago si la impresora de etiquetas no imprime?**\n"
    "Revisa que tenga papel y reiníciala. Si sigue sin funcionar, levanta un reporte en la mesa de ayuda.\n",
    "\n\n---\n\n## Glosario\n\n"
    "- **Acervo:** conjunto de libros y materiales que posee la biblioteca.\n"
    "- **Ficha bibliográfica:** descripción de un libro con título, autor y editorial.\n"
    "- **Credencial:** identificación que la biblioteca entrega a cada lector.\n",
    "\n\n&nbsp;\n\n<!-- fin del contenido exportado -->\n"
    "_Esta página se generó automáticamente a partir de la wiki; algunos formatos pueden verse distintos._\n",
]

# ── CI noise ─────────────────────────────────────────────────────────────────
CI_HEADERS = [
    "# Configuración de la integración continua del proyecto Biblio-VSE.\n"
    "# Los cambios a este archivo se comentan en el canal del equipo.\n\n",
    "# yaml-language-server: $schema=https://json.schemastore.org/gitlab-ci\n\n",
]

CI_JOBS = [
    "\n\ncompilar_estilos:\n"
    "  image: node:20\n"
    "  script:\n"
    "    - npm ci\n"
    "    - npm run build:css\n",
    "\n\ngenerar_sitio_documentacion:\n"
    "  image: python:3.10\n"
    "  script:\n"
    "    - pip install mkdocs\n"
    "    - mkdocs build --site-dir sitio\n",
    "\n\navisar_canal:\n"
    "  image: curlimages/curl:8.5.0\n"
    "  script:\n"
    '    - echo "Pipeline $CI_PIPELINE_ID terminado para la rama $CI_COMMIT_REF_NAME"\n',
]
CI_JOBS_GHA = [
    "\n\n  compilar_estilos:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - run: npm ci && npm run build:css\n",
]


def check_neutral(block):
    for rule, pattern in REGEX.items():
        if re.search(pattern, block, re.IGNORECASE):
            raise ValueError(f"noise block triggers {rule} pattern: {block[:60]!r}")


def rng_for(art_id):
    return random.Random(int(hashlib.sha256(art_id.encode()).hexdigest(), 16) % 2**32)


def add_noise(rec):
    rng = rng_for(rec["id_muestra"])
    text = rec["contenido_texto"]
    kind = rec["tipo_artefacto"]

    if kind == "codigo_fuente":
        header = rng.choice(CODE_HEADERS)
        # Leading newline: two blank lines before top-level definitions (PEP 8).
        tail = "\n" + "".join(rng.sample(CODE_HELPERS_CLEAN, 2))
        if rec["meta_regla"] != "CALIDAD":
            tail += rng.choice(CODE_LEGACY)
        # Comment-only headers keep a module docstring as the first statement.
        return header + text.rstrip("\n") + tail + "\n"

    if kind == "documento_texto":
        return rng.choice(DOC_HEADERS) + text.rstrip("\n") + "".join(rng.sample(DOC_ANNEXES, 2)) + "\n"

    # pipeline_ci
    header = rng.choice(CI_HEADERS)
    if text.lstrip("﻿").startswith("name:") or "\njobs:" in text:
        return header + text.rstrip("\n") + rng.choice(CI_JOBS_GHA) + "\n"
    if text.lstrip().startswith("services:"):
        return header + text  # docker-compose: header comments only
    return header + text.rstrip("\n") + "".join(rng.sample(CI_JOBS, 2)) + "\n"


def main():
    for block in (CODE_HEADERS + CODE_HELPERS_CLEAN + CODE_LEGACY + DOC_HEADERS
                  + DOC_ANNEXES + CI_HEADERS + CI_JOBS + CI_JOBS_GHA):
        check_neutral(block)

    with open(SRC_PATH, encoding="utf-8") as fh:
        dataset = json.load(fh)

    noisy, ratios = [], []
    for rec in dataset:
        new = dict(rec)
        new["contenido_texto"] = add_noise(rec)
        new["ruido"] = True
        ratios.append(len(new["contenido_texto"]) / len(rec["contenido_texto"]))
        noisy.append(new)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(noisy, fh, indent=1, ensure_ascii=False)
    ratios.sort()
    print(f"[+] Wrote {OUT_PATH}: N={len(noisy)}")
    print(f"    length ratio noisy/original: median={ratios[len(ratios)//2]:.2f} "
          f"min={ratios[0]:.2f} max={ratios[-1]:.2f}")


if __name__ == "__main__":
    main()
