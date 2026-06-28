# EXPERIMENT 8 — ZERO-SHOT + RAG + ACTIVATION STEERING
# All techniques combined: structured prompt + normative context + steering.
import json, os, sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils import (
    CATALOGO_MODELOS, ORDEN_MODELOS, DATASET_PATH, SYSTEM_ZEROSHOT,
    cargar_modelo_por_clave, limpiar_vram,
    generar_con_modelo, extraer_prediccion,
    formatear_prompt, prompt_zeroshot_rag, imprimir_resultados,
    aplicar_steering,
)
from rag_utils import cargar_documentos, recuperar_contexto

NOMBRE = "EXPERIMENT 8 — ZERO-SHOT + RAG + STEERING"
ALPHA  = 0.8

# Default lang=es: Spanish anchors match the Spanish evaluation artifacts.
LANG = "es"
RAG_CORPUS = "metarules"
for _i, _v in enumerate(sys.argv):
    if _v == "--lang" and _i + 1 < len(sys.argv):
        LANG = sys.argv[_i + 1]
    if _v == "--rag-corpus" and _i + 1 < len(sys.argv):
        RAG_CORPUS = sys.argv[_i + 1]


def evaluar_dataset(modelo, tokenizer, dataset: list,
                    documentos: list) -> tuple[list, list, int]:
    y_true, y_pred, fallos = [], [], 0
    for muestra in dataset:
        contexto = recuperar_contexto(documentos, muestra["meta_regla"],
                                        muestra.get("contenido_texto", ""))
        user_text = prompt_zeroshot_rag(
            muestra["meta_regla"], muestra["tipo_artefacto"],
            muestra["contenido_texto"], contexto,
        )
        prompt_text = formatear_prompt(tokenizer, user_text, system_content=SYSTEM_ZEROSHOT)
        raw  = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
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
    handle = aplicar_steering(modelo, tokenizer, conf["capa_steering"],
                              alpha=ALPHA, lang=LANG)
    try:
        y_true, y_pred, fallos = evaluar_dataset(modelo, tokenizer, dataset, documentos)
    finally:
        handle.remove()
        print("  [*] Steering hook removed.")
    imprimir_resultados(conf["nombre"], y_true, y_pred, fallos)
    del modelo, tokenizer
    limpiar_vram()


def main():
    print(f"\n{'#'*70}")
    print(f"  {NOMBRE}")
    print(f"  ZS + RAG corpus={RAG_CORPUS} + steering α={ALPHA}  lang={LANG}")
    print(f"{'#'*70}")

    print("\n  [*] Loading RAG documents...")
    documentos = cargar_documentos(RAG_CORPUS)
    if not documentos:
        print("  [!] No documents found. RAG will operate without context.")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for clave in ORDEN_MODELOS:
        evaluar_modelo(clave, dataset, documentos)

    print(f"\n[✓] {NOMBRE} completed.\n")


if __name__ == "__main__":
    main()


