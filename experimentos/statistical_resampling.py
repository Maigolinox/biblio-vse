import numpy as np
from sklearn.metrics import f1_score
from scipy.stats import wilcoxon

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
    np.random.seed(42) # Fixed seed for reproducibility
    for _ in range(n_iterations):
        indices = np.random.randint(0, n_size, n_size)
        score = f1_score(y_true[indices], y_pred[indices], zero_division=0)
        f1_scores.append(score)
    alpha = (1.0 - ci) / 2.0
    return np.percentile(f1_scores, alpha * 100), np.percentile(f1_scores, (1.0 - alpha) * 100)

print("=== Comprehensive Statistical Validation Report ===")
print("Note: Wilcoxon p-value compares each experiment's predictions against Experiment 1 (Baseline).\n")

models = ["Gemma-2-9B-it", "Mistral-7B-v0.2", "Qwen2.5-7B-Instruct", "Phi-3.5-mini"]

for model in models:
    print(f"[{model.upper()}]")
    print(f"{'Experiment':<25} | {'F1-Score':<10} | {'95% CI':<15} | {'Wilcoxon p-val'}")
    print("-" * 75)
    
    # Baseline vectors for Wilcoxon test
    y1 = experiments[1][model]
    correct_1 = (y_true == y1).astype(int)
    
    for exp_num in range(1, 9):
        y_pred = experiments[exp_num][model]
        
        # F1 and CI
        f1 = f1_score(y_true, y_pred, zero_division=0)
        ci_lower, ci_upper = bootstrap_f1_ci(y_true, y_pred)
        
        # Wilcoxon Test against Baseline
        correct_current = (y_true == y_pred).astype(int)
        
        if exp_num == 1:
            p_val_str = "N/A (Baseline)"
        elif np.array_equal(correct_1, correct_current):
            p_val_str = "1.0000 (Exact Match)"
        else:
            _, p_val = wilcoxon(correct_1, correct_current)
            p_val_str = f"{p_val:.4f}"
            
        exp_label = f"Exp {exp_num}: {exp_names[exp_num]}"
        print(f"{exp_label:<25} | {f1:.4f}     | [{ci_lower:.2f}, {ci_upper:.2f}]  | {p_val_str}")
        
    print("\n")