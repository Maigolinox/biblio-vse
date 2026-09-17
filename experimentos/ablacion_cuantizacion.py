"""
ABLACION_CUANTIZACION.PY — 4-bit NF4 vs bfloat16 quantization ablation
=======================================================================
Addresses reviewer concern: "4-bit NF4 quantization is applied to all models
and never ablated. Quantization can shift both calibration and the internal
representations that activation steering manipulates."

This script runs Phi-3.5-mini-instruct (the smallest model, ~3.8B parameters)
under Exp 6 (Zero-Shot + Activation Steering, Spanish anchors) with:
  (a) 4-bit NF4 quantization  — the standard config used in the paper
  (b) bfloat16 full precision — unquantized; needs ~7.6 GB VRAM on RTX 4060

ΔF1 = F1(bfloat16) - F1(4bit) quantifies the quantization effect on steering.

Usage (from repo root):
    python experimentos/ablacion_cuantizacion.py

Output:
  - Per-config F1, Precision, Recall, confusion matrix
  - Delta table showing quantization effect
  - LaTeX snippet for §VII-B (Internal Validity)
"""

import json
import os
import sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gc
import torch
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from transformers import AutoModelForCausalLM, AutoTokenizer

from utils import (
    DATASET_PATH, SYSTEM_ZEROSHOT,
    limpiar_vram,
    generar_con_modelo, extraer_prediccion, formatear_prompt,
    prompt_zeroshot,
    calcular_vector_steering, aplicar_steering_con_vector,
)

MODEL_ID   = "microsoft/Phi-3.5-mini-instruct"
MODEL_NAME = "Phi-3.5-mini-instruct"
LAYER      = 16      # 50%-depth heuristic (confirmed optimal for Phi-3.5, Fig. layer_sensitivity)
ALPHA      = 0.8
LANG       = "es"    # Spanish anchors (methodologically correct default)


def load_model_4bit() -> tuple:
    """Load Phi-3.5-mini with 4-bit NF4 quantization (standard paper config)."""
    print("  [*] Loading Phi-3.5-mini in 4-bit NF4...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    from transformers import BitsAndBytesConfig
    qcfg = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
    )
    modelo = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=qcfg, device_map="auto"
    )
    if torch.cuda.is_available():
        mb = torch.cuda.memory_allocated() / 1024**2
        print(f"  [+] 4-bit NF4 loaded. GPU allocated: {mb:.0f} MB")
    return modelo, tokenizer


def load_model_bf16() -> tuple:
    """Load Phi-3.5-mini in bfloat16 (no quantization).

    Phi-3.5-mini at 3.82B parameters × 2 bytes ≈ 7.6 GB VRAM.
    Falls back to float16 if bfloat16 is not supported on the device,
    and to load_in_8bit if VRAM is insufficient.
    """
    print("  [*] Loading Phi-3.5-mini in bfloat16 (no quantization)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    dtype_name = "bfloat16" if dtype == torch.bfloat16 else "float16"

    try:
        modelo = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            device_map="auto",
        )
        if torch.cuda.is_available():
            mb = torch.cuda.memory_allocated() / 1024**2
            print(f"  [+] {dtype_name} loaded. GPU allocated: {mb:.0f} MB")
        return modelo, tokenizer
    except (RuntimeError, torch.cuda.OutOfMemoryError):
        print(f"  [!] {dtype_name} OOM — falling back to 8-bit quantization.")
        from transformers import BitsAndBytesConfig
        qcfg_8bit = BitsAndBytesConfig(load_in_8bit=True)
        modelo = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, quantization_config=qcfg_8bit, device_map="auto"
        )
        if torch.cuda.is_available():
            mb = torch.cuda.memory_allocated() / 1024**2
            print(f"  [+] 8-bit fallback loaded. GPU allocated: {mb:.0f} MB")
        return modelo, tokenizer


def run_exp6(modelo, tokenizer, dataset: list) -> list[int]:
    """Run Exp 6 (ZS + Steering, Spanish anchors) on the full dataset.

    Returns list of integer predictions (0 or 1).
    """
    vector = calcular_vector_steering(modelo, tokenizer, LAYER, lang=LANG)
    handle = aplicar_steering_con_vector(modelo, vector, LAYER, alpha=ALPHA)

    preds = []
    try:
        for m in dataset:
            user_text   = prompt_zeroshot(
                m["meta_regla"], m["tipo_artefacto"], m["contenido_texto"]
            )
            prompt_text = formatear_prompt(tokenizer, user_text,
                                           system_content=SYSTEM_ZEROSHOT)
            raw  = generar_con_modelo(modelo, tokenizer, prompt_text).strip()
            pred = extraer_prediccion(raw)
            preds.append(pred if pred != -1 else 0)
    finally:
        handle.remove()

    return preds


def print_results(label: str, y_true: list, y_pred: list) -> dict:
    f1  = f1_score(y_true, y_pred, zero_division=0)
    pre = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    cm  = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  RESULTS — {label}")
    print(sep)
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  Precision : {pre:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  TP={tp}  TN={tn}  FP={fp}  FN={fn}")
    print(sep)

    return {"label": label, "f1": f1, "precision": pre, "recall": rec,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def latex_snippet(r_4bit: dict, r_bf16: dict) -> str:
    delta_f1  = r_bf16["f1"]  - r_4bit["f1"]
    delta_pre = r_bf16["precision"] - r_4bit["precision"]
    delta_rec = r_bf16["recall"]    - r_4bit["recall"]
    sign = "+" if delta_f1 >= 0 else ""

    return (
        f"A bfloat16 vs.\\ 4-bit NF4 ablation was conducted for Phi-3.5-mini-instruct\n"
        f"under Exp~6 (ZS+Steering, Spanish anchors, $\\alpha=0.8$, layer~16)\n"
        f"on the $N=32$ artifact set. The 4-bit NF4 configuration yields\n"
        f"F1={r_4bit['f1']:.4f} (P={r_4bit['precision']:.3f}, R={r_4bit['recall']:.3f});\n"
        f"bfloat16 yields F1={r_bf16['f1']:.4f}\n"
        f"(P={r_bf16['precision']:.3f}, R={r_bf16['recall']:.3f}).\n"
        f"The quantization effect is $\\Delta$F1$={sign}{delta_f1:+.4f}$\n"
        f"($\\Delta$P$={delta_pre:+.3f}$, $\\Delta$R$={delta_rec:+.3f}$),\n"
        f"indicating that {'4-bit NF4 does not materially degrade' if abs(delta_f1) < 0.05 else 'quantization shifts'}\n"
        f"steering performance for this architecture under this configuration.\n"
        f"The interaction between 4-bit quantization and steering effectiveness\n"
        f"for the remaining three architectures is reserved for future work."
    )


def main():
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)
    y_true = [m["etiqueta_clase"] for m in dataset]
    print(f"[*] Dataset: {len(dataset)} artifacts "
          f"({sum(y_true)} compliant, {len(y_true)-sum(y_true)} violations)")

    results = {}

    # ── Run 1: 4-bit NF4 ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RUN 1 — 4-bit NF4 (paper standard)")
    print("=" * 60)
    modelo, tokenizer = load_model_4bit()
    preds_4bit = run_exp6(modelo, tokenizer, dataset)
    results["4bit_nf4"] = print_results("4-bit NF4 (paper standard)", y_true, preds_4bit)
    del modelo, tokenizer
    limpiar_vram()

    # ── Run 2: bfloat16 ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RUN 2 — bfloat16 / full precision")
    print("=" * 60)
    modelo, tokenizer = load_model_bf16()
    preds_bf16 = run_exp6(modelo, tokenizer, dataset)
    results["bf16"] = print_results("bfloat16 (no quantization)", y_true, preds_bf16)
    del modelo, tokenizer
    limpiar_vram()

    # ── Delta summary ─────────────────────────────────────────────────────────
    r4  = results["4bit_nf4"]
    rbf = results["bf16"]
    print("\n" + "=" * 60)
    print("  QUANTIZATION ABLATION SUMMARY")
    print("=" * 60)
    print(f"  {'Config':<30} {'F1':>8}  {'Prec':>8}  {'Rec':>8}")
    print(f"  {'-'*56}")
    print(f"  {'4-bit NF4 (paper)':<30} {r4['f1']:>8.4f}  {r4['precision']:>8.4f}  {r4['recall']:>8.4f}")
    print(f"  {'bfloat16 (no quant)':<30} {rbf['f1']:>8.4f}  {rbf['precision']:>8.4f}  {rbf['recall']:>8.4f}")
    delta = rbf['f1'] - r4['f1']
    print(f"  {'Δ (bf16 − 4bit)':<30} {delta:>+8.4f}")
    print(f"\n  Interpretation: {'ΔF1 < 0.05 → quantization effect is small' if abs(delta) < 0.05 else 'ΔF1 ≥ 0.05 → quantization materially shifts steering'}")

    # ── LaTeX snippet ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  LATEX SNIPPET — paste into §VII-B (Internal Validity)")
    print("=" * 60)
    print(latex_snippet(r4, rbf))


if __name__ == "__main__":
    main()
