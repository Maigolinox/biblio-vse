"""
MEASURE PRIVATE REPOSITORY — D_private isomorphism statistics
=============================================================
Walks a directory tree of the private industrial repository and computes
the same structural metrics used for D_synthetic:
  - Cyclomatic complexity V(G)  [Python .py files]
  - Gunning Fog Index           [documents: .txt .md .rst .docx .pdf]
  - Lexical density             [same document set]

Then prints:
  1. Per-file metric table
  2. Box-plot statistics (mean, variance, min/Q1/median/Q3/max)
  3. Comparison table against D_synthetic (read from dataset_isomorfico.json)
  4. LaTeX-ready \\addplot+ D_private block to paste into article.tex
  5. Tolerance-threshold verdict (does D_private satisfy isomorphism criteria?)

Usage (from repo root, replace path with your private repo root):
    conda run -n aud_llm python experimentos/measure_private_repo.py --dir "C:/path/to/private_repo"

    # Only Python files:
    conda run -n aud_llm python experimentos/measure_private_repo.py --dir "C:/path/to/private_repo" --only py

    # Only documents:
    conda run -n aud_llm python experimentos/measure_private_repo.py --dir "C:/path/to/private_repo" --only docs
"""

import argparse
import ast as _ast
import json
import os
import statistics
import sys

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from radon.complexity import cc_visit
import textstat

DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")

# Isomorphism tolerance thresholds (from article §3)
EPS_VG_MEAN = 0.5    # |μ_private - μ_synthetic| ≤ ε for V(G)
DELTA_VG_VAR = 0.25  # |σ²_private - σ²_synthetic| ≤ δ for V(G) variance
EPS_FOG_MEAN = 1.0   # |μ_private - μ_synthetic| ≤ ε_F for Fog Index


# ── Metric functions (same as isomorphism_metrics.py) ────────────────────────

def cyclomatic_complexity(source_code: str) -> float:
    try:
        results = cc_visit(source_code)
        if not results:
            return 1.0
        return round(sum(r.complexity for r in results) / len(results), 2)
    except Exception:
        return 1.0


def gunning_fog(text: str) -> float:
    try:
        return round(textstat.gunning_fog(text), 2)
    except Exception:
        return 0.0


def lexical_density(text: str) -> float:
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


def box_stats(values: list) -> dict:
    if not values:
        return {}
    s = sorted(values)
    n = len(s)
    mean  = statistics.mean(s)
    stdev = statistics.stdev(s) if n > 1 else 0.0
    return {
        "n":      n,
        "mean":   round(mean, 4),
        "stdev":  round(stdev, 4),
        "var":    round(stdev ** 2, 4),
        "min":    round(s[0], 2),
        "q1":     round(s[n // 4], 2),
        "median": round(statistics.median(s), 2),
        "q3":     round(s[(3 * n) // 4], 2),
        "max":    round(s[-1], 2),
    }


# ── File readers ──────────────────────────────────────────────────────────────

def read_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        print(f"  [!] python-docx not installed — skipping {os.path.basename(path)}")
        return ""
    except Exception as e:
        print(f"  [!] Could not read {os.path.basename(path)}: {e}")
        return ""


def read_pdf(path: str) -> str:
    for mod_name in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(mod_name)
            reader = getattr(mod, "PdfReader")(open(path, "rb"))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except ImportError:
            continue
        except Exception as e:
            print(f"  [!] Could not read {os.path.basename(path)}: {e}")
            return ""
    print(f"  [!] pypdf/PyPDF2 not installed — skipping {os.path.basename(path)}")
    return ""


def read_text(path: str) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


# ── Directory walker ──────────────────────────────────────────────────────────

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    "node_modules", ".tox", ".mypy_cache", "dist", "build",
}

PY_EXTS   = {".py"}
DOC_EXTS  = {".txt", ".md", ".rst", ".docx", ".doc", ".pdf"}


def collect_files(root: str, only: str) -> tuple[list[str], list[str]]:
    """Returns (py_files, doc_files) under root, skipping common non-source dirs."""
    py_files, doc_files = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune non-source directories in-place so os.walk won't descend
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            full = os.path.join(dirpath, fname)
            if ext in PY_EXTS and only in ("all", "py"):
                py_files.append(full)
            elif ext in DOC_EXTS and only in ("all", "docs"):
                doc_files.append(full)
    return sorted(py_files), sorted(doc_files)


# ── D_synthetic baseline (read from dataset_isomorfico.json) ─────────────────

def synthetic_stats() -> dict:
    """Recomputes D_synthetic stats from dataset_isomorfico.json for comparison."""
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)
    vg, depth, fog, ld = [], [], [], []
    for s in dataset:
        t = s["contenido_texto"]
        if s["tipo_artefacto"] == "codigo_fuente":
            vg.append(cyclomatic_complexity(t))
            depth.append(ast_depth(t))
        else:
            fog.append(gunning_fog(t))
            ld.append(lexical_density(t))
    return {"vg": box_stats(vg), "depth": box_stats(depth), "fog": box_stats(fog), "ld": box_stats(ld)}


# ── Tolerance verdict ─────────────────────────────────────────────────────────

def tolerance_check(label: str, priv: dict, synth: dict,
                    eps_mean: float, eps_var: float | None = None):
    if not priv or not synth:
        print(f"  {label}: cannot compare — insufficient data")
        return
    delta_mean = abs(priv["mean"] - synth["mean"])
    ok_mean = delta_mean <= eps_mean
    result = f"  {label} mean diff = {delta_mean:.4f}  (threshold <= {eps_mean})  {'OK' if ok_mean else 'FAILS'}"
    print(result)
    if eps_var is not None:
        delta_var = abs(priv["var"] - synth["var"])
        ok_var = delta_var <= eps_var
        print(f"  {label} var  diff = {delta_var:.4f}  (threshold <= {eps_var})   {'OK' if ok_var else 'FAILS'}")


# ── LaTeX block generator ─────────────────────────────────────────────────────

def latex_block(stats: dict, color: str = "blue") -> str:
    if not stats:
        return "  % no data"
    return (
        f"  \\addplot+[boxplot prepared={{\n"
        f"      lower whisker={stats['min']},\n"
        f"      lower quartile={stats['q1']},\n"
        f"      median={stats['median']},\n"
        f"      upper quartile={stats['q3']},\n"
        f"      upper whisker={stats['max']}}},\n"
        f"      fill={color}!20, draw={color}!70\n"
        f"  ] coordinates {{}};  %% D_private: n={stats['n']}, "
        f"mean={stats['mean']}, var={stats['var']}"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Measure D_private isomorphism statistics for article.tex"
    )
    parser.add_argument(
        "--dir", required=True,
        help="Root directory of the private repository"
    )
    parser.add_argument(
        "--only", choices=["all", "py", "docs"], default="all",
        help="Measure only Python files, only documents, or both (default: all)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        sys.exit(f"[ERROR] Directory not found: {args.dir}")

    print("=" * 90)
    print("  D_private ISOMORPHISM METRICS")
    print(f"  Repository root: {args.dir}")
    print("=" * 90)

    py_files, doc_files = collect_files(args.dir, args.only)
    print(f"\n  Found {len(py_files)} Python file(s) and {len(doc_files)} document(s).\n")

    # ── Python files → cyclomatic complexity + AST depth ─────────────────────
    vg_values, depth_values = [], []
    if py_files:
        print(f"{'File':<60} {'V(G)':<8} {'ASTdepth'}")
        print("-" * 80)
        for path in py_files:
            src = read_text(path)
            if not src.strip():
                continue
            vg    = cyclomatic_complexity(src)
            depth = ast_depth(src)
            vg_values.append(vg)
            depth_values.append(depth)
            rel = os.path.relpath(path, args.dir)
            print(f"  {rel:<58} {vg:<8} {depth}")

    # ── Document files → Gunning Fog + Lexical Density ───────────────────────
    fog_values, ld_values, doc_names = [], [], []
    if doc_files:
        print(f"\n{'File':<55} {'Fog':<8} {'LexDen%'}")
        print("-" * 75)
        for path in doc_files:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".docx" or ext == ".doc":
                text = read_docx(path)
            elif ext == ".pdf":
                text = read_pdf(path)
            else:
                text = read_text(path)
            if not text.strip():
                continue
            fog = gunning_fog(text)
            ld  = lexical_density(text)
            fog_values.append(fog)
            ld_values.append(ld)
            doc_names.append(os.path.basename(path))
            rel = os.path.relpath(path, args.dir)
            print(f"  {rel:<53} {fog:<8} {ld}")

    # ── Box-plot statistics ───────────────────────────────────────────────────
    synth     = synthetic_stats()
    vg_priv   = box_stats(vg_values)
    depth_priv = box_stats(depth_values)
    fog_priv  = box_stats(fog_values)
    ld_priv   = box_stats(ld_values)

    sep = "=" * 90

    print(f"\n{sep}")
    print("  BOX-PLOT STATISTICS — D_private")
    print(sep)

    if vg_priv:
        print(f"\n[Cyclomatic Complexity V(G)]  n={vg_priv['n']} Python files")
        print(f"  mean={vg_priv['mean']}  stdev={vg_priv['stdev']}  var={vg_priv['var']}")
        print(f"  min={vg_priv['min']}  Q1={vg_priv['q1']}  median={vg_priv['median']}  Q3={vg_priv['q3']}  max={vg_priv['max']}")

    if depth_priv:
        print(f"\n[AST Depth]  n={depth_priv['n']} Python files")
        print(f"  mean={depth_priv['mean']}  stdev={depth_priv['stdev']}  var={depth_priv['var']}")
        print(f"  min={depth_priv['min']}  Q1={depth_priv['q1']}  median={depth_priv['median']}  Q3={depth_priv['q3']}  max={depth_priv['max']}")

    if fog_priv:
        print(f"\n[Gunning Fog Index]  n={fog_priv['n']} documents")
        print(f"  mean={fog_priv['mean']}  stdev={fog_priv['stdev']}  var={fog_priv['var']}")
        print(f"  min={fog_priv['min']}  Q1={fog_priv['q1']}  median={fog_priv['median']}  Q3={fog_priv['q3']}  max={fog_priv['max']}")

    if ld_priv:
        print(f"\n[Lexical Density %]  n={ld_priv['n']} documents")
        print(f"  mean={ld_priv['mean']}  stdev={ld_priv['stdev']}  var={ld_priv['var']}")
        print(f"  min={ld_priv['min']}  Q1={ld_priv['q1']}  median={ld_priv['median']}  Q3={ld_priv['q3']}  max={ld_priv['max']}")

    # ── Comparison against D_synthetic ────────────────────────────────────────
    print(f"\n{sep}")
    print("  COMPARISON: D_private vs D_synthetic")
    print(sep)

    if synth["vg"] and vg_priv:
        print(f"\n  D_synthetic V(G):   mean={synth['vg']['mean']}  var={synth['vg']['var']}  n={synth['vg']['n']}")
        print(f"  D_private   V(G):   mean={vg_priv['mean']}     var={vg_priv['var']}     n={vg_priv['n']}")
        tolerance_check("V(G)", vg_priv, synth["vg"], EPS_VG_MEAN, DELTA_VG_VAR)

    if synth["depth"] and depth_priv:
        print(f"\n  D_synthetic AST depth:  mean={synth['depth']['mean']}  n={synth['depth']['n']}")
        print(f"  D_private   AST depth:  mean={depth_priv['mean']}     n={depth_priv['n']}")
        delta = abs(depth_priv['mean'] - synth['depth']['mean'])
        print(f"  AST depth mean diff = {delta:.4f}  (no formal threshold defined — reported descriptively)")

    if synth["fog"] and fog_priv:
        print(f"\n  D_synthetic Fog:    mean={synth['fog']['mean']}  n={synth['fog']['n']}")
        print(f"  D_private   Fog:    mean={fog_priv['mean']}     n={fog_priv['n']}")
        tolerance_check("Fog Index", fog_priv, synth["fog"], EPS_FOG_MEAN)

    # ── LaTeX output ──────────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  LATEX — paste these blocks into article.tex replacing D_private placeholders")
    print(sep)

    if vg_priv:
        print("\n  %% --- Cyclomatic Complexity V(G) figure (D_private box) ---")
        print(latex_block(vg_priv, "blue"))

    if depth_priv:
        print(f"\n  %% --- AST Depth (D_private, descriptive) ---")
        print(f"  %%  n={depth_priv['n']}, mean={depth_priv['mean']}, stdev={depth_priv['stdev']}")
        print(f"  %%  min={depth_priv['min']}  Q1={depth_priv['q1']}  median={depth_priv['median']}  Q3={depth_priv['q3']}  max={depth_priv['max']}")

    if fog_priv:
        print("\n  %% --- Gunning Fog Index figure (D_private box) ---")
        print(latex_block(fog_priv, "blue"))

    print(f"\n{sep}")
    print("  NEXT STEPS")
    print(sep)
    print("""
  1. Copy each \\addplot+ block above into article.tex, replacing the
     placeholder D_private box (lines ~414-429 for V(G), ~447-460 for Fog).
     The placeholder comment reads:
       % Placeholder D_private values below mirror D_synthetic and must be replaced

  2. Update the numerical claims in section 3 with the real values:
       |mean_private(V(G)) - mean_synthetic(V(G))| = <your delta mean>
       |var_private(V(G)) - var_synthetic(V(G))| = <your delta var>
       |mean_private(F) - mean_synthetic(F)| = <your delta fog>

  3. If any tolerance check above shows FAILS, soften the isomorphism
     claim to "partially isomorphic under selected observable metrics."
""")


if __name__ == "__main__":
    main()
