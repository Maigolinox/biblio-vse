# CLASSICAL RULE-BASED BASELINE (REGEX)
# Classifies each artifact by searching for compliance keywords
# specific to each ISO/IEC 29110 meta-rule. Does not use LLMs.
import re
import json
import os
import sys
import numpy as np
from sklearn.metrics import (
    f1_score, precision_score, recall_score, accuracy_score,
    classification_report, confusion_matrix,
)

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")

# COMPLIANCE keywords by meta-rule.
# Presence → predicts 1 (Compliant). Absence → predicts 0 (Violation).
PATTERNS: dict[str, str] = {
    "DOCUMENTAL":   r"Código|Versión|Fecha de Vigencia|BVSE-[A-Z]+-\d+",
    "CALIDAD":      r"linter|flake8|Lista de Cotejo|pruebas unitarias|magic numbers",
    "GOBERNANZA":   r"Aprobado|Firma Digital|Autoriza|BVSE-REQ-\d+",
    "SEGURIDAD":    r"os\.environ|environ\.get|getenv",
    "TRAZABILIDAD": r"RF_\d+|US_\d+|ID Requerimiento|Caso de Prueba Asociado",
    "PRUEBAS":      r"Resultado Esperado|Entorno:|Pasos:|Caso de Prueba:",
    "RESPALDO":     r"backup|pg_dump|dump|restore|respaldo",
    "ACUERDOS":     r"Acuerdo\s+\d+|Responsable:|Estado:",
    "INFRA":        r"biblioteca\.local|\.internal|entornos?\s+autorizado",
}

# Generic fallback pattern for meta-rules not explicitly covered
_FALLBACK = r"\b(documentado|aprobado|revisión|revisado|trazabilidad|evidencia|registro|versión|validado|plan|pruebas)\b"


def predecir(texto: str, meta_regla: str) -> tuple[int, str | None]:
    pattern = PATTERNS.get(meta_regla, _FALLBACK)
    m = re.search(pattern, texto, re.IGNORECASE)
    return (1, m.group()) if m else (0, None)


def bootstrap_f1_ci(y_true: np.ndarray, y_pred: np.ndarray,
                    n_iterations: int = 1000, ci: float = 0.95) -> tuple[float, float]:
    np.random.seed(42)
    n = len(y_true)
    scores = []
    for _ in range(n_iterations):
        idx = np.random.randint(0, n, n)
        scores.append(f1_score(y_true[idx], y_pred[idx], zero_division=0))
    alpha = (1.0 - ci) / 2.0
    return np.percentile(scores, alpha * 100), np.percentile(scores, (1.0 - alpha) * 100)


def main() -> None:
    import sys, io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    y_true = np.array([s["etiqueta_clase"] for s in dataset])

    print(f"\n{'#'*70}")
    print("  CLASSICAL RULE-BASED BASELINE (REGEX — ISO/IEC 29110)")
    print(f"{'#'*70}\n")
    print(f"  {'ID':<28}  {'Meta-Rule':<14}  GT    Pred  Detected keyword")
    print(f"  {'-'*70}")

    y_pred_list: list[int] = []
    for s in dataset:
        pred, kw = predecir(s["contenido_texto"], s["meta_regla"])
        ok     = "✓" if pred == s["etiqueta_clase"] else "✗"
        kw_str = f"'{kw}'" if kw else "—"
        print(f"  {s['id_muestra']:<28}  {s['meta_regla']:<14}  "
              f"  {s['etiqueta_clase']}     {pred}  {ok}  {kw_str}")
        y_pred_list.append(pred)

    y_pred  = np.array(y_pred_list)
    ci_lo, ci_hi = bootstrap_f1_ci(y_true, y_pred)

    sep = "=" * 70
    print(f"\n{sep}")
    print("  RESULTS — Classical Baseline (Regex per Meta-Rule)")
    print(sep)
    print("\n  Predictions:", y_pred)
    print("  True Labels:", y_true)
    print(f"\n  Confusion Matrix (rows=actual, cols=predicted) [0,1]:")
    print(confusion_matrix(y_true, y_pred))
    print("\n  Detailed metrics:")
    print(classification_report(y_true, y_pred,
                                target_names=["Violation (0)", "Compliant (1)"],
                                zero_division=0))
    f1_regex = f1_score(y_true, y_pred, zero_division=0)
    print(f"  Accuracy : {accuracy_score(y_true, y_pred):.4f}")
    print(f"  Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  Recall   : {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  F1-Score : {f1_regex:.4f}  (95% CI [{ci_lo:.2f}, {ci_hi:.2f}])")
    print(sep)

    # ── T1-C: Majority-class baseline ────────────────────────────────────────
    # A trivial classifier that predicts "compliant" for every artifact.
    # On the 11/9 split (11 compliant, 9 violations) this achieves non-trivial
    # F1 and serves as the floor against which all LLM configurations must be
    # compared. Reviewer concern §6: several reported LLM F1 values (~0.70)
    # were close to or below this floor, which readers need to calibrate against.
    y_majority   = np.ones(len(y_true), dtype=int)
    f1_maj       = f1_score(y_true, y_majority, zero_division=0)
    pre_maj      = precision_score(y_true, y_majority, zero_division=0)
    rec_maj      = recall_score(y_true, y_majority, zero_division=0)
    ci_maj_lo, ci_maj_hi = bootstrap_f1_ci(y_true, y_majority)

    print(f"\n{sep}")
    print("  MAJORITY-CLASS BASELINE — 'always predict Compliant (1)'")
    print(f"  Dataset split: {int(y_true.sum())} compliant / "
          f"{int((1 - y_true).sum())} violations  (N={len(y_true)})")
    print(sep)
    print(f"  Precision : {pre_maj:.4f}  ({int(y_true.sum())}/{len(y_true)} = "
          f"{y_true.mean():.2f} — fraction of true positives in the dataset)")
    print(f"  Recall    : {rec_maj:.4f}  (detects all compliant artifacts by construction)")
    print(f"  F1-Score  : {f1_maj:.4f}  (95% CI [{ci_maj_lo:.2f}, {ci_maj_hi:.2f}])")
    print()
    print(f"  Any LLM configuration with F1 <= {f1_maj:.4f} does not outperform")
    print(f"  a zero-cost classifier that ignores the artifact entirely.")
    print(f"  Add this value as a dashed reference line to the forest plot (Fig. 13).")
    print(sep)

    n_adv = sum(1 for s in dataset if "adversarial" in s)
    n_orig = len(dataset) - n_adv
    print(f"""
  BENCHMARK DESIGN NOTES (N={len(dataset)}: {n_orig} original + {n_adv} adversarial)
  ─────────────────────────────────────────────────────────────────────

  ORIGINAL {n_orig} ARTIFACTS (N=20 proof-of-concept set):
    Every compliant artifact contains at least one explicit keyword from
    the PATTERNS dict; every violating artifact deliberately omits them.
    A regex therefore achieved F1=1.000 on this subset — the perfect score
    was a label-validity check (§V-E), not evidence that the benchmark was
    hard.

  ADVERSARIAL {n_adv} ARTIFACTS (added for reviewer revision):
    Type-B (6 negatives, label=0): contain compliance keywords in contexts
      that do NOT satisfy the rule (pending approval, removed references,
      commented-out code, hollow test stubs). Regex predicts 1 (FP).
    Type-C (6 positives, label=1): genuinely comply without any of the
      expected keywords (decouple.config, HU-XX traceability, narrative
      governance, tar+S3 backup, alternative document field names, private
      IPs). Regex predicts 0 (FN).
    Overall regex F1 on all {len(dataset)} artifacts: {f1_regex:.4f} — the LLM pipeline
    must outperform this to demonstrate semantic value over pattern matching.

  REMAINING LIMITATIONS:
    1. N={len(dataset)} is still small; confidence intervals are wide (see forest plot).
    2. All artifacts are single-file; cross-artifact compliance evidence
       (e.g., traceability verified across SRS + test file) is not tested.
    3. The adversarial set targets 6 of the 9 rules; CALIDAD, RESPALDO,
       and DOCUMENTAL type-C cases remain relatively easy for regexes.
    4. PATTERNS dict is published in this file for full transparency —
       include it as an appendix item in the manuscript.
""")
    print(sep)


if __name__ == "__main__":
    main()
