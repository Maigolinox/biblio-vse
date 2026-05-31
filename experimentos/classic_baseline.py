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
    print(f"  Accuracy : {accuracy_score(y_true, y_pred):.4f}")
    print(f"  Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  Recall   : {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  F1-Score : {f1_score(y_true, y_pred, zero_division=0):.4f}"
          f"  (95% CI [{ci_lo:.2f}, {ci_hi:.2f}])")
    print(sep)


if __name__ == "__main__":
    main()
