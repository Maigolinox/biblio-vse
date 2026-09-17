#!/usr/bin/env python3
"""
ABLACION_ESPANOL.PY — Language-confound ablation for steering (T1-B).

Reviewer concern §4:
    The anchor prompts p+ and p- are in English, while evaluation artifacts
    and the Zero-Shot system prompt are in Spanish. The extracted compliance
    vector v_norma may encode a language/persona direction rather than a
    normative compliance distinction.

This script loads JSON result files produced by loo_steering.py (one run with
lang=en, one with lang=es) and prints a side-by-side comparison table showing
LOO-F1 for both anchor languages. The delta column (ES - EN) quantifies how
much of the steering benefit survives when the language mismatch is removed.

Prerequisites — run these first:
    python loo_steering.py --exp 4 6 --lang en --save loo_results_en.json
    python loo_steering.py --exp 4 6 --lang es --save loo_results_es.json

Usage:
    python ablacion_espanol.py
    python ablacion_espanol.py --en loo_results_en.json --es loo_results_es.json
"""
import argparse, json, os, sys

_DIR = os.path.dirname(os.path.abspath(__file__))

EXP_LABELS = {
    "4": "Exp 4 — Steering",
    "6": "Exp 6 — ZS + Steering",
}

INTERPRETATION = """
  How to read the Δ (ES - EN) column:
  ─────────────────────────────────────────────────────────────────────────
  Δ ≈ 0     Both anchor languages yield similar LOO-F1. The steering gain
            is not explained by the language mismatch; it more likely
            encodes a compliance/violation distinction that is represented
            similarly in both languages' activation space.

  Δ > 0     Spanish anchors outperform English anchors. The English vector
  (ES wins) may have injected a confounding language or persona direction
            on top of the compliance signal. Spanish anchors are preferable
            given the Spanish artifact context.

  Δ < 0     English anchors outperform Spanish anchors. This may reflect
  (EN wins) stronger compliance representations in English due to
            pretraining language distribution, or a beneficial persona
            effect from the English formulation.

  In all cases the LOO-F1 (ES) column is the methodologically correct
  estimate for the Spanish-artifact evaluation context used in the paper.
  Report both columns and the delta in the manuscript revision.
  ─────────────────────────────────────────────────────────────────────────
"""


def load_results(path: str) -> dict:
    full = os.path.join(_DIR, path) if not os.path.isabs(path) else path
    with open(full, encoding="utf-8") as fh:
        return json.load(fh)


def fmt_f1(val: float) -> str:
    return f"{val:.4f}"


def fmt_ci(lo: float, hi: float) -> str:
    return f"[{lo:.2f}, {hi:.2f}]"


def main():
    parser = argparse.ArgumentParser(
        description="Compare EN vs ES anchor steering results (language-confound ablation)"
    )
    parser.add_argument(
        "--en", default="loo_results_en.json",
        metavar="FILE",
        help="JSON from: loo_steering.py --lang en --save FILE (default: loo_results_en.json)",
    )
    parser.add_argument(
        "--es", default="loo_results_es.json",
        metavar="FILE",
        help="JSON from: loo_steering.py --lang es --save FILE (default: loo_results_es.json)",
    )
    args = parser.parse_args()

    try:
        data_en = load_results(args.en)
        data_es = load_results(args.es)
    except FileNotFoundError as exc:
        print(f"\n[!] File not found: {exc}")
        print(    "    Run the two loo_steering.py commands shown in the module docstring first.")
        sys.exit(1)

    sep = "=" * 100

    print(f"\n{sep}")
    print(f"  LANGUAGE-CONFOUND ABLATION: English (EN) vs Spanish (ES) Anchor Prompts")
    print(f"  Reviewer concern §4 — steering vector extracted from {data_en['lang'].upper()} "
          f"anchors vs {data_es['lang'].upper()} anchors")
    print(f"  EN run: {args.en}  ({data_en['date']})")
    print(f"  ES run: {args.es}  ({data_es['date']})")
    print(sep)

    # Header
    col_w = {"model": 28, "exp": 22, "f1": 12, "ci": 16, "delta": 10}
    hdr = (
        f"  {'Model':<{col_w['model']}}  "
        f"{'Experiment':<{col_w['exp']}}  "
        f"{'LOO-F1 (EN)':>{col_w['f1']}}  "
        f"{'95% CI (EN)':>{col_w['ci']}}  "
        f"{'LOO-F1 (ES)':>{col_w['f1']}}  "
        f"{'95% CI (ES)':>{col_w['ci']}}  "
        f"{'Δ (ES-EN)':>{col_w['delta']}}"
    )
    print(f"\n{hdr}")
    print("  " + "─" * 98)

    # Track whether any delta is large (>0.05) as a flag for the paper
    large_delta = []

    for model_name in data_en["results"]:
        res_en = data_en["results"].get(model_name, {})
        res_es = data_es["results"].get(model_name, {})

        for exp_id, exp_label in EXP_LABELS.items():
            r_en = res_en.get(exp_id)
            r_es = res_es.get(exp_id)

            if r_en is None or r_es is None:
                print(f"  {model_name:<{col_w['model']}}  {exp_label:<{col_w['exp']}}  "
                      f"[data missing for exp_id={exp_id}]")
                continue

            delta = r_es["loo_f1"] - r_en["loo_f1"]
            flag  = " *" if abs(delta) > 0.05 else ""

            if abs(delta) > 0.05:
                large_delta.append((model_name, exp_label, delta))

            print(
                f"  {model_name:<{col_w['model']}}  "
                f"{exp_label:<{col_w['exp']}}  "
                f"{fmt_f1(r_en['loo_f1']):>{col_w['f1']}}  "
                f"{fmt_ci(r_en['ci_lo'], r_en['ci_hi']):>{col_w['ci']}}  "
                f"{fmt_f1(r_es['loo_f1']):>{col_w['f1']}}  "
                f"{fmt_ci(r_es['ci_lo'], r_es['ci_hi']):>{col_w['ci']}}  "
                f"{delta:>+{col_w['delta']}.4f}{flag}"
            )

    print(f"\n  * |Δ| > 0.05: potentially meaningful difference at N=20.")

    # In-sample vs LOO comparison (optimism audit per run)
    print(f"\n{sep}")
    print(f"  OPTIMISM AUDIT — In-Sample F1 vs LOO-F1")
    print(f"  (positive optimism = in-sample overstates out-of-sample performance)")
    print(sep)

    opt_hdr = (
        f"  {'Model':<{col_w['model']}}  "
        f"{'Experiment':<{col_w['exp']}}  "
        f"{'In-sample':>10}  "
        f"{'LOO (EN)':>10}  "
        f"{'Opt. (EN)':>10}  "
        f"{'LOO (ES)':>10}  "
        f"{'Opt. (ES)':>10}"
    )
    print(f"\n{opt_hdr}")
    print("  " + "─" * 90)

    for model_name in data_en["results"]:
        res_en = data_en["results"].get(model_name, {})
        res_es = data_es["results"].get(model_name, {})

        for exp_id, exp_label in EXP_LABELS.items():
            r_en = res_en.get(exp_id)
            r_es = res_es.get(exp_id)
            if r_en is None or r_es is None:
                continue

            print(
                f"  {model_name:<{col_w['model']}}  "
                f"{exp_label:<{col_w['exp']}}  "
                f"{r_en['insample_f1']:>10.4f}  "
                f"{r_en['loo_f1']:>10.4f}  "
                f"{r_en['optimism']:>+10.4f}  "
                f"{r_es['loo_f1']:>10.4f}  "
                f"{r_es['optimism']:>+10.4f}"
            )

    print(INTERPRETATION)

    if large_delta:
        print("  Cases with |Δ| > 0.05 (worth discussing in §VII-A of the manuscript):")
        for model_name, exp_label, delta in large_delta:
            direction = "ES > EN" if delta > 0 else "EN > ES"
            print(f"    • {model_name}  {exp_label}  Δ={delta:+.4f}  ({direction})")
        print()

    print(f"[✓] Language-confound ablation completed.\n")


if __name__ == "__main__":
    main()
