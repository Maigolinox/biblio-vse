#!/usr/bin/env python3
"""
LAYER_SENSITIVITY.PY — Layer sweep for activation steering.

Addresses the single largest unresolved technical question identified in §VII-B:
the intervention layer was chosen by a 50%-depth heuristic without validation.

This script evaluates steering F1 at every transformer layer for a selected
model and experiment (default: Phi-3.5, Exp 6 ZS+Steering, Spanish anchors).
Results feed directly into Fig. layer_sensitivity in §VII-B of the manuscript.

Usage:
    python layer_sensitivity.py                          # Phi-3.5, Exp6, lang=es
    python layer_sensitivity.py --model gemma2 --exp 6  # Gemma-2, Exp6
    python layer_sensitivity.py --model phi35 --exp 4   # Phi-3.5, Exp4
    python layer_sensitivity.py --model phi35 --exp 6 --lang en  # English ablation

Compute estimate (~RTX 4060, 4-bit NF4):
    Phi-3.5 (32 layers): ~70 min   (32 layers × 32 artifacts × ~4 s + vector extraction)
    Gemma-2  (42 layers): ~90 min
    Qwen2.5  (28 layers): ~60 min

Output:
    layer_sensitivity_{model}_{exp}_{lang}.json  — data file
    Printed table: layer | F1 | TP | FP | FN | TN
"""
import argparse, json, os, sys
import numpy as np
from sklearn.metrics import f1_score, confusion_matrix as sk_cm

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils import (
    CATALOGO_MODELOS, ORDEN_MODELOS, DATASET_PATH,
    SYSTEM_INSTRUCTION, SYSTEM_ZEROSHOT,
    cargar_modelo_por_clave, limpiar_vram,
    generar_con_modelo, extraer_prediccion, formatear_prompt,
    prompt_basico, prompt_zeroshot, prompt_rag, prompt_zeroshot_rag,
    calcular_vector_steering, aplicar_steering_con_vector,
)
from rag_utils import cargar_documentos, recuperar_contexto

# Experiment configurations (non-RAG only for efficiency; add RAG if needed)
EXP_CONFIGS = {
    4: {
        "nombre":   "Exp 4 — Activation Steering",
        "system":   SYSTEM_INSTRUCTION,
        "uses_rag": False,
        "uses_zs":  False,
    },
    6: {
        "nombre":   "Exp 6 — Zero-Shot + Steering",
        "system":   SYSTEM_ZEROSHOT,
        "uses_rag": False,
        "uses_zs":  True,
    },
}


def build_prompt(muestra: dict, config: dict, rag_ctx=None) -> str:
    m = muestra
    if config["uses_zs"]:
        return prompt_zeroshot(m["meta_regla"], m["tipo_artefacto"], m["contenido_texto"])
    return prompt_basico(m["meta_regla"], m["tipo_artefacto"], m["contenido_texto"])


def infer_at_layer(modelo, tokenizer, vector, capa: int, alpha: float,
                   dataset: list, config: dict) -> list[int]:
    """Run all 32 artifact inferences with steering vector injected at `capa`."""
    handle = aplicar_steering_con_vector(modelo, vector, capa, alpha=alpha)
    preds = []
    try:
        for m in dataset:
            user_text   = build_prompt(m, config)
            prompt_text = formatear_prompt(tokenizer, user_text,
                                           system_content=config["system"])
            raw  = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
            pred = extraer_prediccion(raw)
            preds.append(pred if pred != -1 else 0)
    finally:
        handle.remove()
    return preds


def main():
    parser = argparse.ArgumentParser(
        description="Layer sensitivity sweep for activation steering (§VII-B)"
    )
    parser.add_argument(
        "--model", default="phi35",
        choices=list(CATALOGO_MODELOS.keys()),
        help="Model key (default: phi35 — 32 layers, fastest to sweep)",
    )
    parser.add_argument(
        "--exp", type=int, default=6, choices=[4, 6],
        help="Experiment: 4=Steering only, 6=ZS+Steering (default: 6)",
    )
    parser.add_argument(
        "--lang", default="es", choices=["en", "es"],
        help="Anchor language for steering vector (default: es — methodologically correct)",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.8,
        help="Steering coefficient (default: 0.8 — pilot value from main experiments)",
    )
    parser.add_argument(
        "--save", default="",
        help="Output JSON filename (default: auto-named layer_sensitivity_{model}_{exp}_{lang}.json)",
    )
    args = parser.parse_args()

    conf_info  = CATALOGO_MODELOS[args.model]
    num_layers = conf_info["num_layers"]
    heuristic  = conf_info["capa_steering"]
    config     = EXP_CONFIGS[args.exp]

    out_name = args.save or f"layer_sensitivity_{args.model}_exp{args.exp}_{args.lang}.json"
    out_path = os.path.join(_DIR, out_name)

    print(f"\n{'#'*70}")
    print(f"  LAYER SENSITIVITY SWEEP — {config['nombre']}")
    print(f"  Model : {conf_info['nombre']}  ({num_layers} layers)")
    print(f"  lang  : {args.lang}  |  alpha : {args.alpha}")
    print(f"  Heuristic layer: {heuristic}  (~50% depth)")
    print(f"  Output: {out_name}")
    print(f"  Estimated time: ~{num_layers * 32 * 4 // 60} min")
    print(f"{'#'*70}\n")

    with open(DATASET_PATH, encoding="utf-8") as fh:
        dataset = json.load(fh)
    y_true = [m["etiqueta_clase"] for m in dataset]

    modelo, tokenizer, conf = cargar_modelo_por_clave(args.model)

    results: dict = {
        "model":      conf_info["nombre"],
        "model_key":  args.model,
        "exp":        args.exp,
        "lang":       args.lang,
        "alpha":      args.alpha,
        "num_layers": num_layers,
        "heuristic_layer": heuristic,
        "layers": {},
    }

    # Header
    print(f"  {'Layer':>6}  {'F1':>8}  {'TP':>4}  {'FP':>4}  {'FN':>4}  {'TN':>4}  Note")
    print("  " + "─" * 52)

    for layer in range(num_layers):
        # Extract steering vector at this specific layer
        vector = calcular_vector_steering(modelo, tokenizer, layer, lang=args.lang)

        preds = infer_at_layer(modelo, tokenizer, vector, layer,
                               args.alpha, dataset, config)

        f1_val = f1_score(y_true, preds, zero_division=0)
        cm = sk_cm(y_true, preds, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        results["layers"][layer] = {
            "f1": round(float(f1_val), 4),
            "tp": int(tp), "fp": int(fp),
            "fn": int(fn), "tn": int(tn),
        }

        note = "<-- heuristic (50% depth)" if layer == heuristic else ""
        print(f"  {layer:>6}  {f1_val:>8.4f}  {tp:>4}  {fp:>4}  {fn:>4}  {tn:>4}  {note}")

    # Summary
    best_layer = max(results["layers"], key=lambda l: results["layers"][l]["f1"])
    best_f1    = results["layers"][best_layer]["f1"]
    heur_f1    = results["layers"][heuristic]["f1"]

    results["best_layer"] = best_layer
    results["best_f1"]    = best_f1
    results["heuristic_f1"] = heur_f1
    results["delta_best_vs_heuristic"] = round(best_f1 - heur_f1, 4)

    print()
    print(f"  {'─'*52}")
    print(f"  Heuristic layer ({heuristic:2d}):  F1 = {heur_f1:.4f}")
    print(f"  Best layer      ({best_layer:2d}):  F1 = {best_f1:.4f}")
    print(f"  Δ (best − heuristic)   : {best_f1 - heur_f1:+.4f}")

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\n  [✓] Results saved to {out_path}")
    print(f"  Use these values to fill in the pgfplots data in Fig. layer_sensitivity\n")

    del modelo, tokenizer
    limpiar_vram()
    print(f"[✓] Layer sensitivity sweep completed.\n")


if __name__ == "__main__":
    main()
