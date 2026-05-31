# EXPERIMENT 3 — RAG
# Retrieves relevant fragments from documentos_estandar and injects normative context.
# No structured zero-shot, no steering.
import json, os, sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils import (
    CATALOGO_MODELOS, ORDEN_MODELOS, DATASET_PATH, SYSTEM_INSTRUCTION,
    cargar_modelo_por_clave, limpiar_vram,
    generar_con_modelo, extraer_prediccion,
    formatear_prompt, prompt_rag, imprimir_resultados,
)
from rag_utils import cargar_documentos, recuperar_contexto

NOMBRE = "EXPERIMENT 3 — RAG"


def evaluar_dataset(modelo, tokenizer, dataset: list,
                    documentos: list) -> tuple[list, list, int]:
    y_true, y_pred, fallos = [], [], 0
    for muestra in dataset:
        contexto = recuperar_contexto(documentos, muestra["meta_regla"],
                                        muestra.get("contenido_texto", ""))
        user_text = prompt_rag(
            muestra["meta_regla"], muestra["tipo_artefacto"],
            muestra["contenido_texto"], contexto,
        )
        prompt_text = formatear_prompt(tokenizer, user_text, system_content=SYSTEM_INSTRUCTION)
        raw = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
        pred = extraer_prediccion(raw)
        if pred == -1:
            fallos += 1
            pred = 0
        y_true.append(muestra["etiqueta_clase"])
        y_pred.append(pred)
        print(f"    {muestra['id_muestra']}: real={muestra['etiqueta_clase']} pred={pred}")
    return y_true, y_pred, fallos


def evaluar_modelo(clave: str, dataset: list, documentos: list):
    conf_info = CATALOGO_MODELOS[clave]
    print(f"\n{'─'*65}")
    print(f"  Modelo: {conf_info['nombre']}")
    print(f"{'─'*65}")
    modelo, tokenizer, conf = cargar_modelo_por_clave(clave)
    y_true, y_pred, fallos = evaluar_dataset(modelo, tokenizer, dataset, documentos)
    imprimir_resultados(conf["nombre"], y_true, y_pred, fallos)
    del modelo, tokenizer
    limpiar_vram()


def main():
    print(f"\n{'#'*70}")
    print(f"  {NOMBRE}")
    print(f"  Normative context injected from documentos_estandar/")
    print(f"{'#'*70}")

    print("\n  [*] Loading RAG documents...")
    documentos = cargar_documentos()
    if not documentos:
        print("  [!] No documents found. RAG will operate without context.")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for clave in ORDEN_MODELOS:
        evaluar_modelo(clave, dataset, documentos)

    print(f"\n[✓] {NOMBRE} completed.\n")


if __name__ == "__main__":
    main()


