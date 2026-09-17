# ISOMORPHISM METRICS — Synthetic Repository (D_synthetic)
# Computes cyclomatic complexity V(G), AST depth, Gunning Fog Index, and
# Lexical Density for each artifact in dataset_isomorfico.json.
# Also performs TOST (Two One-Sided Tests) equivalence testing against
# D_private reference values to formally validate distributional similarity.
#
# Usage (from repo root):
#   python experimentos/isomorphism_metrics.py
#
# Output:
#   - Per-artifact table: ID, meta-rule, type, V(G), AST depth, Fog Index, LexDen%
#   - Box-plot statistics for D_synthetic
#   - TOST equivalence test results for each metric
#   - LaTeX-ready \addplot+[boxplot prepared={...}] values for access.tex

import ast as _ast
import json
import math
import os
import statistics
import sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from radon.complexity import cc_visit
import textstat

DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")

# ── D_private reference statistics (from the private industrial repository) ───
# Source: measured from D_private; only aggregate stats are disclosed.
D_PRIVATE = {
    "vg": {
        "mean": 1.844, "stdev": 3.236, "n": 37,
        "description": "McCabe V(G) from 46 Python files (Documentacion_NOMADA_2022)",
    },
    "fog": {
        "mean": 18.61, "stdev": 9.17, "n": 87,
        "description": "Gunning Fog Index from 87 documentary work products",
    },
    "ast_depth": {
        "mean": 7.84, "stdev": 4.95, "n": 37,
        "description": "AST depth from 46 Python files",
    },
    "lex_density": {
        "mean": 42.88, "stdev": 21.12, "n": 87,
        "description": "Lexical density % from 87 documentary work products",
    },
}

# ── Equivalence bounds (tolerance thresholds ε) ───────────────────────────────
# Calibration rationale documented in §III-B of the manuscript:
#   ε_vg  = 0.5  ≈ SE(µ_V(G)) = sqrt(s²/n) = sqrt(10.47/37) ≈ 0.53
#   ε_fog = 1.0  ≈ σ_F / 9 of D_private Fog stdev (strict criterion)
#   ε_ast = 2.0  = one standard-error unit above D_private AST mean SE
#   ε_ld  = 8.0  ≈ σ_LD / 3 of D_private Lexical Density stdev (lenient)
EQUIVALENCE_BOUNDS = {
    "vg":          0.5,
    "fog":         1.0,
    "ast_depth":   2.0,
    "lex_density": 8.0,
}


# ── Metric functions ──────────────────────────────────────────────────────────

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


def ast_depth(source_code: str) -> int:
    """Returns the maximum nesting depth of the Abstract Syntax Tree."""
    try:
        tree = _ast.parse(source_code)
    except SyntaxError:
        return 0

    def _depth(node: _ast.AST) -> int:
        children = list(_ast.iter_child_nodes(node))
        if not children:
            return 1
        return 1 + max(_depth(child) for child in children)

    return _depth(tree)


# ── Statistics helpers ────────────────────────────────────────────────────────

def box_stats(values: list) -> dict:
    """Returns box-plot and descriptive statistics for a list of numeric values."""
    if not values:
        return {}
    sorted_v = sorted(values)
    n = len(sorted_v)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    mean  = statistics.mean(sorted_v)
    stdev = statistics.stdev(sorted_v) if n > 1 else 0.0
    return {
        "n":      n,
        "min":    round(sorted_v[0], 2),
        "q1":     round(sorted_v[q1_idx], 2),
        "median": round(statistics.median(sorted_v), 2),
        "q3":     round(sorted_v[q3_idx], 2),
        "max":    round(sorted_v[-1], 2),
        "mean":   round(mean, 2),
        "stdev":  round(stdev, 2),
        "var":    round(stdev ** 2, 4),
    }


def tost_welch(
    mu_synth: float, sd_synth: float, n_synth: int,
    mu_priv:  float, sd_priv:  float, n_priv:  int,
    epsilon:  float,
    alpha:    float = 0.05,
) -> dict:
    """
    Two One-Sided t-Tests (TOST) for equivalence between two independent means.

    H0₁: µ_synth - µ_priv ≤ -ε   (lower bound)
    H0₂: µ_synth - µ_priv ≥ +ε   (upper bound)

    Equivalence is declared when BOTH H0 are rejected at level alpha.

    Uses Welch's (unequal-variance) t-statistic and Satterthwaite df.
    """
    diff = mu_synth - mu_priv
    # Pooled standard error (Welch)
    se = math.sqrt(sd_synth**2 / n_synth + sd_priv**2 / n_priv)
    if se == 0:
        return {"equivalent": True, "p_lower": 0.0, "p_upper": 0.0, "se": 0.0,
                "t_lower": float("inf"), "t_upper": float("-inf"), "df": 0}

    # Satterthwaite degrees of freedom
    num   = (sd_synth**2 / n_synth + sd_priv**2 / n_priv) ** 2
    denom = ((sd_synth**2 / n_synth)**2 / (n_synth - 1) +
             (sd_priv**2  / n_priv) **2 / (n_priv  - 1))
    df    = num / denom if denom > 0 else 1.0

    t_lower = (diff + epsilon) / se   # test H0₁: diff ≤ -ε → reject if t_lower > t_crit
    t_upper = (diff - epsilon) / se   # test H0₂: diff ≥ +ε → reject if t_upper < -t_crit

    # p-values from one-tailed t distribution
    # Use normal approximation for large df (df > 30); otherwise use scipy if available
    def t_cdf_upper(t: float, df: float) -> float:
        """P(T > t) for df degrees of freedom — upper tail."""
        try:
            from scipy.stats import t as t_dist
            return float(t_dist.sf(t, df))
        except ImportError:
            # Normal approximation (adequate for df > 15)
            z = t
            return max(0.0, 0.5 * math.erfc(z / math.sqrt(2)))

    p_lower = t_cdf_upper(t_lower, df)   # p for H0₁ (lower)
    p_upper = t_cdf_upper(-t_upper, df)  # p for H0₂ (upper); reject when t_upper < -t_crit

    equivalent = (p_lower < alpha) and (p_upper < alpha)

    return {
        "equivalent": equivalent,
        "diff":       round(diff, 4),
        "se":         round(se, 4),
        "epsilon":    epsilon,
        "t_lower":    round(t_lower, 3),
        "t_upper":    round(t_upper, 3),
        "p_lower":    round(p_lower, 4),
        "p_upper":    round(p_upper, 4),
        "df":         round(df, 1),
        "alpha":      alpha,
    }


def tost_report(metric_key: str, synth_stats: dict, label: str) -> str:
    """Run TOST and return a formatted report string."""
    priv   = D_PRIVATE[metric_key]
    eps    = EQUIVALENCE_BOUNDS[metric_key]

    result = tost_welch(
        mu_synth=synth_stats["mean"], sd_synth=synth_stats["stdev"], n_synth=synth_stats["n"],
        mu_priv=priv["mean"],         sd_priv=priv["stdev"],          n_priv=priv["n"],
        epsilon=eps,
    )

    verdict = "EQUIVALENT (p_L<0.05 and p_U<0.05)" if result["equivalent"] \
              else "NOT EQUIVALENT"
    delta = abs(synth_stats["mean"] - priv["mean"])

    lines = [
        f"  [{label}] TOST equivalence test (ε = {eps})",
        f"    D_private:  mean={priv['mean']:.3f}, SD={priv['stdev']:.3f}, n={priv['n']}",
        f"    D_synthetic: mean={synth_stats['mean']:.3f}, SD={synth_stats['stdev']:.3f}, n={synth_stats['n']}",
        f"    |Δmean| = {delta:.4f}  (threshold ε = {eps})",
        f"    t_lower={result['t_lower']:.3f}, p_lower={result['p_lower']:.4f}",
        f"    t_upper={result['t_upper']:.3f}, p_upper={result['p_upper']:.4f}",
        f"    df={result['df']:.1f}",
        f"    Verdict: {verdict}",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    print("=" * 90)
    print("  ISOMORPHISM METRICS — D_synthetic (Biblio-VSE)")
    print("=" * 90)

    vg_code_values    = []
    depth_code_values = []
    fog_doc_values    = []
    ld_doc_values     = []

    print(f"\n{'ID':<30} {'Meta-Rule':<15} {'Type':<15} {'V(G)':<8} {'ASTdepth':<10} {'Fog':<8} {'LexDen%':<10}")
    print("-" * 100)

    for sample in dataset:
        sid   = sample["id_muestra"]
        rule  = sample["meta_regla"]
        atype = sample["tipo_artefacto"]
        text  = sample["contenido_texto"]
        label = sample["etiqueta_clase"]

        if atype == "codigo_fuente":
            vg    = cyclomatic_complexity(text)
            depth = ast_depth(text)
            fog   = "—"
            ld    = "—"
            vg_code_values.append(vg)
            depth_code_values.append(depth)
        elif atype in ("documento_texto", "pipeline_ci"):
            vg    = "—"
            depth = "—"
            fog   = gunning_fog(text)
            ld    = lexical_density(text)
            fog_doc_values.append(fog)
            ld_doc_values.append(ld)
        else:
            vg = depth = fog = ld = "?"

        print(f"{sid:<30} {rule:<15} {atype:<15} {str(vg):<8} {str(depth):<10} {str(fog):<8} {str(ld):<10}  label={label}")

    # ── Distribution statistics ───────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  BOX-PLOT STATISTICS FOR D_synthetic")
    print("=" * 90)

    vg_stats    = box_stats(vg_code_values)    if vg_code_values    else {}
    depth_stats = box_stats(depth_code_values) if depth_code_values else {}
    fog_stats   = box_stats(fog_doc_values)    if fog_doc_values    else {}
    ld_stats    = box_stats(ld_doc_values)     if ld_doc_values     else {}

    if vg_stats:
        print(f"\n[Cyclomatic Complexity V(G)] — code artifacts (n={vg_stats['n']} files)")
        print(f"  mean={vg_stats['mean']}  stdev={vg_stats['stdev']}  var={vg_stats['var']}")
        print(f"  min={vg_stats['min']}  Q1={vg_stats['q1']}  med={vg_stats['median']}  Q3={vg_stats['q3']}  max={vg_stats['max']}")

    if depth_stats:
        print(f"\n[AST Depth] — code artifacts (n={depth_stats['n']} files)")
        print(f"  mean={depth_stats['mean']}  stdev={depth_stats['stdev']}  var={depth_stats['var']}")
        print(f"  min={depth_stats['min']}  Q1={depth_stats['q1']}  med={depth_stats['median']}  Q3={depth_stats['q3']}  max={depth_stats['max']}")

    if fog_stats:
        print(f"\n[Gunning Fog Index] — document/CI artifacts (n={fog_stats['n']} documents)")
        print(f"  mean={fog_stats['mean']}  stdev={fog_stats['stdev']}  var={fog_stats['var']}")
        print(f"  min={fog_stats['min']}  Q1={fog_stats['q1']}  med={fog_stats['median']}  Q3={fog_stats['q3']}  max={fog_stats['max']}")

    if ld_stats:
        print(f"\n[Lexical Density %] — document/CI artifacts (n={ld_stats['n']} documents)")
        print(f"  mean={ld_stats['mean']}  stdev={ld_stats['stdev']}  var={ld_stats['var']}")
        print(f"  min={ld_stats['min']}  Q1={ld_stats['q1']}  med={ld_stats['median']}  Q3={ld_stats['q3']}  max={ld_stats['max']}")

    # ── TOST equivalence tests ────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  TOST EQUIVALENCE TESTS (Two One-Sided t-Tests, α=0.05)")
    print("  Equivalence declared iff BOTH p_lower < α AND p_upper < α")
    print("=" * 90)

    if vg_stats:
        print()
        print(tost_report("vg", vg_stats, "V(G) Mean"))

    if depth_stats:
        print()
        print(tost_report("ast_depth", depth_stats, "AST Depth Mean"))

    if fog_stats:
        print()
        print(tost_report("fog", fog_stats, "Fog Index Mean"))

    if ld_stats:
        print()
        print(tost_report("lex_density", ld_stats, "Lexical Density Mean"))

    # ── Summary table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  ISOMORPHISM SUMMARY")
    print("=" * 90)
    print(f"  {'Metric':<22} {'|Δmean|':<12} {'ε':<8} {'Pass?':<8} {'TOST equivalent?'}")
    print("  " + "-" * 66)

    checks = []
    for key, label, synth_st in [
        ("vg",          "V(G) mean",       vg_stats),
        ("ast_depth",   "AST depth mean",  depth_stats),
        ("fog",         "Fog mean",        fog_stats),
        ("lex_density", "Lexical Density", ld_stats),
    ]:
        if not synth_st:
            continue
        priv  = D_PRIVATE[key]
        eps   = EQUIVALENCE_BOUNDS[key]
        delta = abs(synth_st["mean"] - priv["mean"])
        mean_pass = delta <= eps

        r = tost_welch(
            synth_st["mean"], synth_st["stdev"], synth_st["n"],
            priv["mean"],     priv["stdev"],     priv["n"],
            eps,
        )
        checks.append((key, label, delta, eps, mean_pass, r["equivalent"]))
        print(f"  {label:<22} {delta:<12.4f} {eps:<8.1f} "
              f"{'YES' if mean_pass else 'NO':<8} {'EQUIVALENT' if r['equivalent'] else 'NOT EQUIVALENT'}")

    all_mean_pass = all(c[4] for c in checks)
    all_tost      = all(c[5] for c in checks)
    print(f"\n  All mean-threshold checks pass: {all_mean_pass}")
    print(f"  All TOST equivalences declared: {all_tost}")

    if not all_mean_pass or not all_tost:
        print("\n  NOTE: Metrics that fail equivalence testing should NOT be claimed as")
        print("  isomorphic. Characterize the benchmark as 'distributionally proximate")
        print("  on passing metrics' rather than 'structurally isomorphic'.")

    # ── LaTeX snippets ────────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("  LATEX BOXPLOT VALUES — paste into access.tex Fig isomorphism_boxplots")
    print("=" * 90)

    if vg_stats:
        print(f"""
  %% D_synthetic V(G): n={vg_stats['n']}, mean={vg_stats['mean']}, var={vg_stats['var']}
  \\addplot+[boxplot prepared={{
      lower whisker={vg_stats['min']},
      lower quartile={vg_stats['q1']},
      median={vg_stats['median']},
      upper quartile={vg_stats['q3']},
      upper whisker={vg_stats['max']}}},
      fill=green!20, draw=green!70
  ] coordinates {{}};""")

    if fog_stats:
        print(f"""
  %% D_synthetic Fog: n={fog_stats['n']}, mean={fog_stats['mean']}, var={fog_stats['var']}
  \\addplot+[boxplot prepared={{
      lower whisker={fog_stats['min']},
      lower quartile={fog_stats['q1']},
      median={fog_stats['median']},
      upper quartile={fog_stats['q3']},
      upper whisker={fog_stats['max']}}},
      fill=green!20, draw=green!70
  ] coordinates {{}};""")


if __name__ == "__main__":
    main()
