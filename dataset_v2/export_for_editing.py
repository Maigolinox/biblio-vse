# EXPORT THE BENCHMARK ARTIFACTS AS EDITABLE FILES
#
# Writes every artifact of the extended benchmark to an ordinary file with the
# extension of its type, so that they can be reviewed and rewritten in an
# editor instead of inside JSON or Python string literals:
#
#   dataset_v2/edicion/es/<id>.py|.md|.yml     Spanish edition
#   dataset_v2/edicion/en/<id>.py|.md|.yml     English edition
#   dataset_v2/edicion/metadata.json           rule, type, label, scenario,
#                                              adversarial kind and rationale
#   dataset_v2/edicion/LEEME.md                what must be preserved when editing
#
# After editing, run dataset_v2/import_edited.py to rebuild the datasets and
# re-run every validation check.
#
# Usage (from repo root):  python dataset_v2/export_for_editing.py

import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
OUT = os.path.join(_DIR, "edicion")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXT = {"codigo_fuente": ".py", "documento_texto": ".md", "pipeline_ci": ".yml",
       "source_code": ".py", "text_document": ".md", "ci_pipeline": ".yml"}

LEEME = """\
# Edición de los artefactos de Biblio-VSE

Cada archivo de `es/` y `en/` es el contenido exacto de un artefacto del
benchmark. Edítalos con libertad: al terminar, ejecuta

    python dataset_v2/import_edited.py

que reconstruye `dataset_isomorfico_n96.json`, `_en.json` y `_noisy.json` y
vuelve a ejecutar todas las comprobaciones automáticas.

## Qué debe conservarse

1. **La etiqueta.** `metadata.json` indica, para cada artefacto, la meta-regla y
   si cumple (`etiqueta_clase` = 1) o la viola (0). El contenido editado debe
   seguir correspondiendo a esa etiqueta según el criterio de la meta-regla; si
   decides cambiar la etiqueta, edítala también en `metadata.json`.
2. **El diseño adversarial.** Los artefactos marcados `tipo_b` deben seguir
   activando el regex de su regla (contienen las palabras clave en un contexto
   que NO cumple); los `tipo_c` deben seguir cumpliendo SIN esas palabras clave.
   El importador verifica ambas condiciones y falla si dejan de cumplirse.
   `adversarial_nota` explica la intención de cada uno.
3. **El emparejamiento ES/EN.** Los archivos con el mismo nombre en `es/` y `en/`
   son el mismo artefacto en dos idiomas y deben seguir diciendo lo mismo.
4. **Los identificadores técnicos** (RF_05, HU-12, BVSE-*, nombres de host) se
   mantienen iguales en ambos idiomas.
5. **Nada de comentarios que revelen la etiqueta** (p. ej. "esto viola CALIDAD").

## Qué NO hace falta conservar

El estilo, la redacción, los nombres de variables, la longitud y los detalles
del escenario son libres. Los 32 artefactos originales (`origen=original_v1`)
pueden editarse igual, pero ten en cuenta que cambiarlos rompe la comparación
directa con los resultados del envío inicial.

Tras la edición hay que volver a ejecutar los experimentos (`run_condition.py`
para las cuatro condiciones y `experimento_gemini.py`), porque los resultados
publicados corresponden al texto actual de los artefactos.
"""


def main():
    os.makedirs(os.path.join(OUT, "es"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "en"), exist_ok=True)

    with open(os.path.join(_ROOT, "dataset_isomorfico_n96.json"), encoding="utf-8") as fh:
        es = json.load(fh)
    with open(os.path.join(_ROOT, "dataset_isomorfico_n96_en.json"), encoding="utf-8") as fh:
        en = {r["id_muestra"]: r for r in json.load(fh)}

    meta = []
    for rec in es:
        art_id = rec["id_muestra"]
        ext = EXT[rec["tipo_artefacto"]]
        for lang, source in (("es", rec), ("en", en[art_id])):
            path = os.path.join(OUT, lang, art_id + ext)
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(source["contenido_texto"])
        meta.append({
            "id_muestra": art_id,
            "archivo": art_id + ext,
            "meta_regla": rec["meta_regla"],
            "meta_regla_en": en[art_id]["meta_regla"],
            "tipo_artefacto": rec["tipo_artefacto"],
            "etiqueta_clase": rec["etiqueta_clase"],
            "escenario": rec["escenario"],
            "origen": rec["origen"],
            "adversarial": rec.get("adversarial"),
            "adversarial_nota": rec.get("adversarial_nota"),
            "ruta_original": rec["archivo"],
            "depurado_v2": rec.get("depurado_v2", False),
        })

    with open(os.path.join(OUT, "metadata.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "LEEME.md"), "w", encoding="utf-8") as fh:
        fh.write(LEEME)

    print(f"[+] Exported {len(meta)} artifacts to {OUT}\\es and \\en")
    print(f"[+] Metadata: {os.path.join(OUT, 'metadata.json')}")
    print(f"[+] Instructions: {os.path.join(OUT, 'LEEME.md')}")


if __name__ == "__main__":
    main()
