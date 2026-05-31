# ISOMORPHISM METRICS — Synthetic Repository (D_synthetic)
# Computes cyclomatic complexity V(G) and Gunning Fog Index for each artifact
# in dataset_isomorfico.json and prints box-plot statistics for the article.
#
# Usage (from repo root):
#   conda run -n aud_llm python experimentos/isomorphism_metrics.py
#
# Output:
#   - Per-artifact table: ID, meta-rule, type, V(G), Fog Index, lexical density
#   - Box-plot statistics (min, Q1, median, Q3, max) for D_synthetic
#   - LaTeX-ready \addplot+[boxplot prepared={...}] values for article.tex
#
# For D_private statistics: run the same logic on your private repository
# files and fill in the LaTeX values manually.

import json
import os
import sys
import statistics

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from radon.complexity import cc_visit
from radon.metrics import mi_visit
import textstat

DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")


def cyclomatic_complexity(source_code: str) -> float:
    """Returns mean cyclomatic complexity V(G) across all functions/classes.
    Returns 1.0 for code with no explicit control flow (linear scripts)."""
    try:
        results = cc_visit(source_code)
        if not results:
            return 1.0
        return round(sum(r.complexity for r in results) / len(results), 2)
    except Exception:
        return 1.0


def gunning_fog(text: str) -> float:
    """Returns Gunning Fog Index for natural language text."""
    try:
        return round(textstat.gunning_fog(text), 2)
    except Exception:
        return 0.0


def lexical_density(text: str) -> float:
    """Returns lexical density as (unique_words / total_words) * 100."""
    words = text.split()
    if not words:
        return 0.0
    return round(len(set(w.lower() for w in words)) / len(words) * 100, 2)


def box_stats(values: list) -> dict:
    """Returns box-plot statistics for a list of numeric values."""
    if not values:
        return {}
    sorted_v = sorted(values)
    n = len(sorted_v)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    return {
        "min":    round(sorted_v[0], 2),
        "q1":     round(sorted_v[q1_idx], 2),
        "median": round(statistics.median(sorted_v), 2),
        "q3":     round(sorted_v[q3_idx], 2),
        "max":    round(sorted_v[-1], 2),
        "mean":   round(statistics.mean(sorted_v), 2),
        "stdev":  round(statistics.stdev(sorted_v) if len(sorted_v) > 1 else 0.0, 2),
    }


def main():
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    print("=" * 90)
    print("  ISOMORPHISM METRICS — D_synthetic (Biblio-VSE)")
    print("=" * 90)

    # Separate code vs document artifacts
    vg_code_values  = []
    fog_doc_values  = []
    ld_doc_values   = []

    print(f"\n{'ID':<30} {'Meta-Rule':<15} {'Type':<15} {'V(G)':<8} {'Fog':<8} {'LexDen%':<10}")
    print("-" * 90)

    for sample in dataset:
        sid   = sample["id_muestra"]
        rule  = sample["meta_regla"]
        atype = sample["tipo_artefacto"]
        text  = sample["contenido_texto"]
        label = sample["etiqueta_clase"]

        if atype == "codigo_fuente":
            vg  = cyclomatic_complexity(text)
            fog = "—"
            ld  = "—"
            vg_code_values.append(vg)
            flag = " [CODE]"
        elif atype in ("documento_texto", "pipeline_ci"):
            vg  = "—"
            fog = gunning_fog(text)
            ld  = lexical_density(text)
            fog_doc_values.append(fog)
            ld_doc_values.append(ld)
            flag = " [DOC]"
        else:
            vg = fog = ld = "?"
            flag = ""

        print(f"{sid:<30} {rule:<15} {atype:<15} {str(vg):<8} {str(fog):<8} {str(ld):<10}  label={label}")

    # Distribution statistics
    print("\n" + "=" * 90)
    print("  BOX-PLOT STATISTICS FOR D_synthetic")
    print("=" * 90)

    if vg_code_values:
        stats = box_stats(vg_code_values)
        print(f"\n[Cyclomatic Complexity V(G)] — code artifacts (n={len(vg_code_values)})")
        print(f"  mean={stats['mean']}  stdev={stats['stdev']}")
        print(f"  min={stats['min']}  Q1={stats['q1']}  median={stats['median']}  Q3={stats['q3']}  max={stats['max']}")
        print("\n  -- LaTeX for article.tex (D_synthetic box, fill D_private box similarly) --")
        print(f"""  \\addplot+[boxplot prepared={{
      lower whisker={stats['min']},
      lower quartile={stats['q1']},
      median={stats['median']},
      upper quartile={stats['q3']},
      upper whisker={stats['max']}}},
      fill=green!20, draw=green!70
  ] coordinates {{}};""")

    if fog_doc_values:
        stats = box_stats(fog_doc_values)
        print(f"\n[Gunning Fog Index] — document/CI artifacts (n={len(fog_doc_values)})")
        print(f"  mean={stats['mean']}  stdev={stats['stdev']}")
        print(f"  min={stats['min']}  Q1={stats['q1']}  median={stats['median']}  Q3={stats['q3']}  max={stats['max']}")
        print("\n  -- LaTeX for article.tex (D_synthetic box, fill D_private box similarly) --")
        print(f"""  \\addplot+[boxplot prepared={{
      lower whisker={stats['min']},
      lower quartile={stats['q1']},
      median={stats['median']},
      upper quartile={stats['q3']},
      upper whisker={stats['max']}}},
      fill=green!20, draw=green!70
  ] coordinates {{}};""")

    if ld_doc_values:
        stats = box_stats(ld_doc_values)
        print(f"\n[Lexical Density %] — document/CI artifacts (n={len(ld_doc_values)})")
        print(f"  mean={stats['mean']}  stdev={stats['stdev']}")
        print(f"  min={stats['min']}  Q1={stats['q1']}  median={stats['median']}  Q3={stats['q3']}  max={stats['max']}")

    print("\n[!] For D_private: run the same analysis on your private repository's Python files")
    print("    and documentary artifacts, then fill the \\addplot+ D_private box with those values.")
    print()


if __name__ == "__main__":
    main()
