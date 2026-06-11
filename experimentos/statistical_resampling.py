import numpy as np
from sklearn.metrics import f1_score, confusion_matrix
from scipy.stats import wilcoxon, binomtest

# True Labels (Constant across all experiments)
# 0 = Viola (NEG), 1 = Cumple (POS)
y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1])

# Dictionary containing all predictions extracted from the experiment logs
experiments = {
    1: { # BASELINE
        "Gemma-2-9B-it":       np.array([0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0]),
        "Qwen2.5-7B-Instruct": np.array([1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0])
    },
    2: { # ZERO-SHOT
        "Gemma-2-9B-it":       np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    },
    3: { # RAG (semantic dense retrieval, all-MiniLM-L6-v2)
        "Gemma-2-9B-it":       np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Qwen2.5-7B-Instruct": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0])
    },
    4: { # ACTIVATION STEERING
        "Gemma-2-9B-it":       np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1]),
        "Mistral-7B-v0.2":     np.array([1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1])
    },
    5: { # ZERO-SHOT + RAG (semantic dense retrieval)
        "Gemma-2-9B-it":       np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    },
    6: { # ZERO-SHOT + STEERING
        "Gemma-2-9B-it":       np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1])
    },
    7: { # RAG + STEERING (semantic dense retrieval)
        "Gemma-2-9B-it":       np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1])
    },
    8: { # ZERO-SHOT + RAG + STEERING (semantic dense retrieval)
        "Gemma-2-9B-it":       np.array([0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1]),
        "Mistral-7B-v0.2":     np.array([0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]),
        "Qwen2.5-7B-Instruct": np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0]),
        "Phi-3.5-mini":        np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1])
    }
}

# Names of the experiments for display
exp_names = {
    1: "Baseline", 2: "Zero-Shot", 3: "RAG", 4: "Steering", 
    5: "ZS + RAG", 6: "ZS + Steering", 7: "RAG + Steering", 8: "ZS + RAG + Steering"
}

def bootstrap_f1_ci(y_true, y_pred, n_iterations=1000, ci=0.95):
    n_size = len(y_true)
    f1_scores = []
    np.random.seed(42)
    for _ in range(n_iterations):
        indices = np.random.randint(0, n_size, n_size)
        score = f1_score(y_true[indices], y_pred[indices], zero_division=0)
        f1_scores.append(score)
    alpha = (1.0 - ci) / 2.0
    return np.percentile(f1_scores, alpha * 100), np.percentile(f1_scores, (1.0 - alpha) * 100)


def mcnemar_exact(y_base, y_curr, y_true_vec):
    """McNemar's exact binomial test for paired binary classifiers.

    b = samples where baseline is correct but current is wrong.
    c = samples where baseline is wrong but current is correct.
    Uses an exact two-sided binomial test (appropriate for n ≤ 25).
    Returns (p_value, b, c).
    """
    b = int(np.sum((y_base == y_true_vec) & (y_curr != y_true_vec)))
    c = int(np.sum((y_base != y_true_vec) & (y_curr == y_true_vec)))
    if b + c == 0:
        return 1.0, b, c
    p = binomtest(min(b, c), b + c, 0.5, alternative="two-sided").pvalue
    return float(p), b, c


def holm_adjust(p_values):
    """Holm step-down family-wise error rate correction.

    Receives a list of raw p-values and returns an array of adjusted p-values
    in the same order. More powerful than Bonferroni while still controlling FWER.
    """
    n = len(p_values)
    if n == 0:
        return np.array([])
    p = np.array(p_values, dtype=float)
    order = np.argsort(p)
    adjusted = p.copy()
    for rank, idx in enumerate(order):
        adjusted[idx] = min(1.0, p[idx] * (n - rank))
    cummax = 0.0
    for idx in order:
        adjusted[idx] = max(adjusted[idx], cummax)
        cummax = adjusted[idx]
    return adjusted

print("=== Comprehensive Statistical Validation Report ===")
print("Primary test : McNemar's exact binomial test (b/c = disagreement pairs vs. Baseline).")
print("Secondary    : Wilcoxon signed-rank on per-sample correctness vectors (shown for comparison).")
print("Correction   : Holm step-down applied within each model's comparison family (7 tests).")
print("Effect size  : b/c disagreement counts; odds-ratio = b/c (>1 means baseline was better).")
print("Bootstrap CI : 1 000 resamples, seed=42. Wide intervals reflect n=20 — treat as exploratory.")
print("Interpretation: No result survives Holm correction at α=0.05. Report directional evidence only.\n")

models = ["Gemma-2-9B-it", "Mistral-7B-v0.2", "Qwen2.5-7B-Instruct", "Phi-3.5-mini"]
HDR = f"{'Experiment':<27} | {'F1':<6} | {'95% CI (boot)':<15} | {'McNemar p':<11} | {'Holm p':<8} | {'b/c':<5} | Wilcoxon p"
SEP = "-" * 100

for model in models:
    print(f"\n{'='*100}")
    print(f"  MODEL: {model}")
    print(f"{'='*100}")

    y1        = experiments[1][model]
    correct_1 = (y_true == y1).astype(int)

    # ── Collect p-values for Holm correction ──────────────────────────────
    non_baseline_exps = list(range(2, 9))
    raw_p_mc = []
    row_cache = {}

    for exp_num in non_baseline_exps:
        y_pred        = experiments[exp_num][model]
        f1            = f1_score(y_true, y_pred, zero_division=0)
        ci_lo, ci_hi  = bootstrap_f1_ci(y_true, y_pred)
        p_mc, b, c    = mcnemar_exact(y1, y_pred, y_true)
        correct_curr  = (y_true == y_pred).astype(int)
        if np.array_equal(correct_1, correct_curr):
            p_wil = 1.0
        else:
            _, p_wil = wilcoxon(correct_1, correct_curr)
        raw_p_mc.append(p_mc)
        row_cache[exp_num] = dict(f1=f1, ci=(ci_lo, ci_hi),
                                  p_mc=p_mc, p_wil=p_wil, b=b, c=c)

    holm_p = holm_adjust(raw_p_mc)

    # ── Per-experiment metrics (confusion matrix shown separately below) ──
    print(f"\n{HDR}")
    print(SEP)

    # Baseline row
    f1_b         = f1_score(y_true, y1, zero_division=0)
    ci_b_lo, ci_b_hi = bootstrap_f1_ci(y_true, y1)
    print(f"  {'Exp 1: Baseline':<25} | {f1_b:.4f} | [{ci_b_lo:.2f}, {ci_b_hi:.2f}]       | {'—':<11} | {'—':<8} | {'—':<5} | — (reference)")

    for i, exp_num in enumerate(non_baseline_exps):
        d     = row_cache[exp_num]
        b, c  = d["b"], d["c"]
        odds  = f"{b/c:.2f}" if c > 0 else "∞"
        p_mc  = d["p_mc"]
        p_h   = holm_p[i]
        label = f"Exp {exp_num}: {exp_names[exp_num]}"

        if b == 0 and c == 0:
            p_mc_str = "1.0000*"
            p_h_str  = "1.0000"
        else:
            p_mc_str = f"{p_mc:.4f}"
            p_h_str  = f"{p_h:.4f}"

        bc_str = f"{b}/{c}"
        print(
            f"  {label:<25} | {d['f1']:.4f} | [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]       "
            f"| {p_mc_str:<11} | {p_h_str:<8} | {bc_str:<5} | {d['p_wil']:.4f}"
        )

    print(f"\n  * p=1.0000 with asterisk = no disagreements between this experiment and Baseline.")
    print(f"  Odds-ratio interpretation: b/c > 1 means Baseline was correct where current was wrong more often.")

    # ── Confusion matrices ────────────────────────────────────────────────
    print(f"\n  CONFUSION MATRICES (rows=actual [0,1], cols=predicted [0,1]):")
    for exp_num in range(1, 9):
        y_pred = experiments[exp_num][model]
        cm     = confusion_matrix(y_true, y_pred, labels=[0, 1])
        label  = f"Exp {exp_num}: {exp_names[exp_num]}"
        tn, fp, fn, tp = cm.ravel()
        print(f"    {label:<27}  TN={tn}  FP={fp}  FN={fn}  TP={tp}")

print("\n")