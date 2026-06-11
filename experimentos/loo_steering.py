#!/usr/bin/env python3
"""
LOO_STEERING.PY — Leave-One-Out alpha-selection for steering experiments.

Addresses two reviewer concerns:

  §3 — In-sample hyperparameter selection:
    alpha=0.8 and the intervention layer were chosen on the same N=20 artifacts
    used for evaluation. This script implements proper LOO alpha selection: for
    each held-out artifact i, alpha is chosen by maximizing F1 on the remaining
    19 artifacts; the held-out artifact is then classified with that alpha.
    The resulting LOO-F1 is an out-of-sample performance estimate.

  §4 — Language confound (via --lang es):
    The original anchor prompts are English while artifacts and prompts are
    Spanish. Running with --lang es extracts the steering vector from
    Spanish anchors, allowing direct comparison with English-anchor LOO-F1.
    Combine with ablacion_espanol.py for the full comparison table.

Usage:
    python loo_steering.py                          # Exp 4,6,7,8 with EN anchors
    python loo_steering.py --exp 4 6                # only Exp 4 and Exp 6
    python loo_steering.py --exp 4 6 --lang es      # Spanish-anchor ablation
    python loo_steering.py --models phi35 gemma2    # subset of models
    python loo_steering.py --exp all --save loo_results_en.json

Compute estimate (~RTX 4060, 4-bit NF4):
    All 4 experiments, all 4 models: ~2.1 h  (4 models x 4 exp x 6 alpha x 20 art x 4 s)
    Exp 4+6 only, all 4 models:      ~1.1 h
    Single model, Exp 4+6:           ~16 min
"""
import argparse, json, os, sys
from datetime import datetime

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

# --------------------------------------------------------------------------- #
#  Configuration                                                                #
# --------------------------------------------------------------------------- #

ALPHA_SWEEP = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
ALPHA_PAPER = 0.8   # value used in the original paper

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
    7: {
        "nombre":   "Exp 7 — RAG + Steering",
        "system":   SYSTEM_INSTRUCTION,
        "uses_rag": True,
        "uses_zs":  False,
    },
    8: {
        "nombre":   "Exp 8 — Zero-Shot + RAG + Steering",
        "system":   SYSTEM_ZEROSHOT,
        "uses_rag": True,
        "uses_zs":  True,
    },
}


# --------------------------------------------------------------------------- #
#  Prompt construction                                                          #
# --------------------------------------------------------------------------- #

def build_user_prompt(muestra: dict, config: dict, rag_ctx: str | None) -> str:
    m = muestra
    rule, atype, content = m["meta_regla"], m["tipo_artefacto"], m["contenido_texto"]
    if config["uses_rag"] and config["uses_zs"]:
        return prompt_zeroshot_rag(rule, atype, content, rag_ctx)
    if config["uses_rag"]:
        return prompt_rag(rule, atype, content, rag_ctx)
    if config["uses_zs"]:
        return prompt_zeroshot(rule, atype, content)
    return prompt_basico(rule, atype, content)


def precompute_rag_contexts(dataset: list, documentos: list) -> dict:
    """Pre-compute RAG context for every artifact. Contexts are alpha-independent."""
    ctx = {}
    for m in dataset:
        ctx[m["id_muestra"]] = recuperar_contexto(
            documentos, m["meta_regla"], m.get("contenido_texto", "")
        )
    return ctx


# --------------------------------------------------------------------------- #
#  Inference                                                                    #
# --------------------------------------------------------------------------- #

def infer_all(modelo, tokenizer, dataset: list, config: dict,
              rag_contexts: dict) -> list[int]:
    """Run inference on all artifacts with the currently registered hook.
    Returns a list of 0/1 predictions in dataset order.
    """
    preds = []
    for m in dataset:
        rag_ctx = rag_contexts.get(m["id_muestra"]) if config["uses_rag"] else None
        user_text   = build_user_prompt(m, config, rag_ctx)
        prompt_text = formatear_prompt(tokenizer, user_text, system_content=config["system"])
        raw  = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
        pred = extraer_prediccion(raw)
        preds.append(pred if pred != -1 else 0)
    return preds


def collect_alpha_predictions(modelo, tokenizer, capa: int, vector,
                               dataset: list, config: dict,
                               rag_contexts: dict) -> dict:
    """For each alpha in ALPHA_SWEEP, run all 20 artifact inferences.
    The steering vector is pre-computed once and reused, avoiding 2 forward
    passes per alpha value.

    Returns {alpha: [pred_0, ..., pred_19]}.
    """
    y_true = [m["etiqueta_clase"] for m in dataset]
    alpha_preds = {}

    print(f"    [alpha sweep]", end="  ", flush=True)
    for alpha in ALPHA_SWEEP:
        handle = aplicar_steering_con_vector(modelo, vector, capa, alpha=alpha)
        try:
            preds = infer_all(modelo, tokenizer, dataset, config, rag_contexts)
        finally:
            handle.remove()
        f1_in = f1_score(y_true, preds, zero_division=0)
        alpha_preds[alpha] = preds
        print(f"alpha={alpha} F1={f1_in:.4f}", end="  ", flush=True)
    print()
    return alpha_preds


# --------------------------------------------------------------------------- #
#  LOO alpha selection (pure Python/NumPy — no GPU)                            #
# --------------------------------------------------------------------------- #

def loo_select_alpha(alpha_preds: dict, y_true: list) -> tuple[list, list]:
    """Leave-one-out alpha selection.

    For each held-out fold i:
      1. Compute F1 for every alpha on the 19 remaining artifacts.
      2. Select alpha* = argmax F1 on those 19.
      3. Record the prediction for artifact i made by alpha*.

    Returns (loo_preds, selected_alpha_per_fold).
    This runs in milliseconds — no GPU required.
    """
    n  = len(y_true)
    yt = np.array(y_true)
    loo_preds, sel_alphas = [], []

    for i in range(n):
        train_idx = [j for j in range(n) if j != i]
        yt_train  = yt[train_idx]

        best_alpha, best_f1 = None, -1.0
        for alpha, preds in alpha_preds.items():
            train_preds = np.array(preds)[train_idx]
            f1 = f1_score(yt_train, train_preds, zero_division=0)
            if f1 > best_f1:
                best_f1  = f1
                best_alpha = alpha

        loo_preds.append(alpha_preds[best_alpha][i])
        sel_alphas.append(best_alpha)

    return loo_preds, sel_alphas


def bootstrap_f1_ci(y_true: list, y_pred: list,
                    n_iter: int = 1000) -> tuple[float, float]:
    np.random.seed(42)
    yt, yp = np.array(y_true), np.array(y_pred)
    n = len(yt)
    scores = []
    for _ in range(n_iter):
        idx = np.random.randint(0, n, n)
        scores.append(f1_score(yt[idx], yp[idx], zero_division=0))
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


# --------------------------------------------------------------------------- #
#  Per-model-experiment reporting                                               #
# --------------------------------------------------------------------------- #

def run_and_report(model_name: str, exp_id: int, y_true: list,
                   alpha_preds: dict, lang: str) -> dict:
    """Run LOO selection and print results. Returns a result dict."""
    config = EXP_CONFIGS[exp_id]
    loo_preds, sel_alphas = loo_select_alpha(alpha_preds, y_true)

    loo_f1       = f1_score(y_true, loo_preds, zero_division=0)
    ci_lo, ci_hi = bootstrap_f1_ci(y_true, loo_preds)
    insample_f1  = f1_score(y_true, alpha_preds[ALPHA_PAPER], zero_division=0)
    optimism     = loo_f1 - insample_f1

    cm_arr = sk_cm(y_true, loo_preds, labels=[0, 1])
    tn, fp, fn, tp = cm_arr.ravel()
    alpha_dist = {str(a): sel_alphas.count(a) for a in ALPHA_SWEEP}

    print(f"\n    ┌─ {config['nombre']} (lang={lang})")
    print(f"    │  In-sample F1 (alpha={ALPHA_PAPER}):     {insample_f1:.4f}")
    print(f"    │  LOO-F1 (out-of-sample):          {loo_f1:.4f}  "
          f"(95% CI [{ci_lo:.2f}, {ci_hi:.2f}])")
    print(f"    │  Optimism (LOO - in-sample):      {optimism:+.4f}")
    print(f"    │  LOO confusion matrix: "
          f"TN={tn}  FP={fp}  FN={fn}  TP={tp}")
    print(f"    └─ alpha distribution (20 folds): {alpha_dist}")

    return {
        "insample_f1": round(float(insample_f1), 4),
        "loo_f1":      round(float(loo_f1),      4),
        "ci_lo":       round(float(ci_lo),        4),
        "ci_hi":       round(float(ci_hi),        4),
        "optimism":    round(float(optimism),     4),
        "alpha_dist":  alpha_dist,
        "loo_preds":   loo_preds,
        "loo_cm":      {
            "tn": int(tn), "fp": int(fp),
            "fn": int(fn), "tp": int(tp),
        },
    }


# --------------------------------------------------------------------------- #
#  Summary table                                                                #
# --------------------------------------------------------------------------- #

def print_summary_table(all_results: dict, lang: str):
    """Print a compact table for direct inclusion in the paper's Table 5 revision."""
    sep = "═" * 86
    print(f"\n\n{sep}")
    print(f"  SUMMARY — LOO-F1 vs In-Sample F1  (lang={lang})")
    print(f"  Replace or augment Table 5 / forest-plot data with these values.")
    print(sep)
    hdr = (f"  {'Model':<28}  {'Exp':<6}  {'In-sample':>10}  "
           f"{'LOO-F1':>8}  {'95% CI':>14}  {'Optimism':>10}")
    print(hdr)
    print("  " + "─" * 82)

    for model_name, exp_results in all_results.items():
        for exp_id_str in sorted(exp_results, key=int):
            r = exp_results[exp_id_str]
            ci_str = f"[{r['ci_lo']:.2f}, {r['ci_hi']:.2f}]"
            print(
                f"  {model_name:<28}  Exp {exp_id_str:<3}  "
                f"{r['insample_f1']:>10.4f}  "
                f"{r['loo_f1']:>8.4f}  "
                f"{ci_str:>14}  "
                f"{r['optimism']:>+10.4f}"
            )

    print(sep)
    print(f"  Positive optimism = in-sample F1 overstates held-out performance.")
    print(f"  Negative optimism = LOO-F1 actually exceeds the in-sample figure.\n")


# --------------------------------------------------------------------------- #
#  Main                                                                         #
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description="LOO alpha-selection for steering experiments (T1-A + T1-B)"
    )
    parser.add_argument(
        "--exp", nargs="+", type=int, choices=[4, 6, 7, 8],
        default=[4, 6, 7, 8],
        help="Steering experiment IDs to run (default: all four)",
    )
    parser.add_argument(
        "--lang", choices=["en", "es"], default="es",
        help=(
            "Anchor language for steering vector. "
            "es = Spanish (default — methodologically correct, matches artifact language). "
            "en = English (original paper configuration / ablation condition)."
        ),
    )
    parser.add_argument(
        "--models", nargs="+", choices=list(CATALOGO_MODELOS.keys()),
        default=ORDEN_MODELOS,
        help="Model keys to evaluate (default: all four in ORDEN_MODELOS order)",
    )
    parser.add_argument(
        "--save", type=str, default="",
        metavar="FILE",
        help="Save JSON results to FILE (e.g. loo_results_en.json). "
             "Required input for ablacion_espanol.py.",
    )
    args = parser.parse_args()

    exp_ids = sorted(set(args.exp))

    print(f"\n{'#'*70}")
    print(f"  LOO STEERING — Leave-One-Out alpha-Selection")
    print(f"  Experiments : {exp_ids}")
    print(f"  Anchor lang : {args.lang}")
    print(f"  Models      : {args.models}")
    print(f"  alpha sweep : {ALPHA_SWEEP}  (paper value: {ALPHA_PAPER})")
    print(f"{'#'*70}\n")

    with open(DATASET_PATH, encoding="utf-8") as fh:
        dataset = json.load(fh)
    y_true = [m["etiqueta_clase"] for m in dataset]

    # Pre-load RAG documents once if any selected experiment needs them
    documentos  = []
    rag_contexts: dict = {}
    if any(EXP_CONFIGS[e]["uses_rag"] for e in exp_ids):
        print("  [*] Loading RAG documents (shared across experiments)...")
        documentos   = cargar_documentos()
        rag_contexts = precompute_rag_contexts(dataset, documentos)
        print(f"  [+] RAG contexts pre-computed for {len(rag_contexts)} artifacts.\n")

    all_results: dict = {}

    for clave in args.models:
        conf_info  = CATALOGO_MODELOS[clave]
        model_name = conf_info["nombre"]

        print(f"\n{'═'*70}")
        print(f"  Model: {model_name}")
        print(f"{'═'*70}")

        modelo, tokenizer, conf = cargar_modelo_por_clave(clave)
        capa = conf["capa_steering"]

        # Compute the steering vector ONCE per model.
        # It is reused across all alpha values in the sweep,
        # saving 2 * (len(ALPHA_SWEEP) - 1) forward passes per model.
        vector = calcular_vector_steering(modelo, tokenizer, capa, lang=args.lang)

        model_results: dict = {}
        for exp_id in exp_ids:
            config    = EXP_CONFIGS[exp_id]
            exp_rags  = rag_contexts if config["uses_rag"] else {}

            print(f"\n  ── {config['nombre']} ──")

            # GPU: collect predictions for every alpha value
            alpha_preds = collect_alpha_predictions(
                modelo, tokenizer, capa, vector,
                dataset, config, exp_rags,
            )

            # CPU: LOO selection + reporting
            r = run_and_report(model_name, exp_id, y_true, alpha_preds, args.lang)
            model_results[str(exp_id)] = r

        all_results[model_name] = model_results

        del modelo, tokenizer
        limpiar_vram()

    print_summary_table(all_results, args.lang)

    if args.save:
        out_path = (
            os.path.join(_DIR, args.save)
            if not os.path.isabs(args.save) else args.save
        )
        output = {
            "lang":        args.lang,
            "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
            "alpha_sweep": ALPHA_SWEEP,
            "alpha_paper": ALPHA_PAPER,
            "experiments": exp_ids,
            "results":     all_results,
        }
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, ensure_ascii=False)
        print(f"  [✓] Results saved to {out_path}")

    print(f"\n[✓] LOO steering completed.\n")


if __name__ == "__main__":
    main()
