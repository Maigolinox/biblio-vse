# EXPERIMENT 1 — BASELINE
# Pure LLM with no prompt engineering.
# Measures the model's baseline classification capacity without assistance.
import json, os, sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils import (
    CATALOGO_MODELOS, ORDEN_MODELOS, DATASET_PATH,
    cargar_modelo_por_clave, limpiar_vram,
    generar_con_modelo, extraer_prediccion,
    formatear_prompt_sin_sistema, imprimir_resultados,
)

NOMBRE = "EXPERIMENT 1 — BASELINE (pure LLM)"


def construir_prompt(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    return (
        f"Meta-rule: {meta_rule}\n"
        f"Artifact type: {artifact_type}\n"
        f"Artifact:\n{artifact_content}\n\n"
        f"Does it comply (1) or violate (0) the meta-rule? Respond only 1 or 0."
    )


def evaluar_dataset(modelo, tokenizer, dataset: list) -> tuple[list, list, int]:
    y_true, y_pred, fallos = [], [], 0
    for muestra in dataset:
        user_text = construir_prompt(
            muestra["meta_regla"], muestra["tipo_artefacto"], muestra["contenido_texto"]  # JSON keys unchanged
        )
        prompt_text = formatear_prompt_sin_sistema(tokenizer, user_text)
        raw = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
        pred = extraer_prediccion(raw)
        if pred == -1:
            fallos += 1
            pred = 0
        y_true.append(muestra["etiqueta_clase"])
        y_pred.append(pred)
        print(f"    {muestra['id_muestra']}: real={muestra['etiqueta_clase']} pred={pred}")
    return y_true, y_pred, fallos


def evaluar_modelo(clave: str, dataset: list):
    conf_info = CATALOGO_MODELOS[clave]
    print(f"\n{'─'*65}")
    print(f"  Modelo: {conf_info['nombre']}")
    print(f"{'─'*65}")
    modelo, tokenizer, conf = cargar_modelo_por_clave(clave)
    y_true, y_pred, fallos = evaluar_dataset(modelo, tokenizer, dataset)
    imprimir_resultados(conf["nombre"], y_true, y_pred, fallos)
    del modelo, tokenizer
    limpiar_vram()


def main():
    print(f"\n{'#'*70}")
    print(f"  {NOMBRE}")
    print(f"  LLM without system prompt or structuring — baseline capacity")
    print(f"{'#'*70}")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for clave in ORDEN_MODELOS:
        evaluar_modelo(clave, dataset)

    print(f"\n[✓] {NOMBRE} completed.\n")


if __name__ == "__main__":
    main()


