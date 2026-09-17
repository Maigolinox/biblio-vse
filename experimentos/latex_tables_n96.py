# LATEX TABLE / FIGURE-DATA GENERATOR FOR THE REVISED MANUSCRIPT (N=96)
#
# Reads the JSON outputs of the N=96 analyses and writes LaTeX snippets so that
# every number in the manuscript is produced programmatically:
#   full_results.tex, confusion.tex, heatmap.tex, forest.tex, delta.tex,
#   cost.tex, interactions.tex, subsets.tex, language.tex, noise.tex,
#   frontier.tex, calibration.tex
# Snippets for conditions whose results are missing are skipped.
#
# Usage (from repo root):
#   python experimentos/latex_tables_n96.py --out <directory>

import argparse
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOCAL = ["Gemma-2-9B-it", "Mistral-7B-Instruct-v0.2", "Qwen2.5-7B-Instruct", "Phi-3.5-mini-instruct"]
SHORT = {"Gemma-2-9B-it": "Gemma-2", "Mistral-7B-Instruct-v0.2": "Mistral",
         "Qwen2.5-7B-Instruct": "Qwen2.5", "Phi-3.5-mini-instruct": "Phi-3.5"}
EXPS = {"1": "Exp 1: Baseline", "2": "Exp 2: Zero-Shot", "3": "Exp 3: RAG",
        "4": "Exp 4: Steering", "5": "Exp 5: ZS + RAG", "6": "Exp 6: ZS + Steering",
        "7": "Exp 7: RAG + Steer", "8": "Exp 8: ZS + RAG + Steer"}
ABBR = {"1": "Baseline", "2": "ZS", "3": "RAG", "4": "Steer", "5": "ZS+RAG",
        "6": "ZS+Steer", "7": "RAG+Steer", "8": "ZS+RAG+Steer"}


def load(name):
    path = os.path.join(_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def short(model):
    return SHORT.get(model, model.replace("Gemini-", "Gemini "))


def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def confusion(y, p):
    tp = sum(a == 1 and b == 1 for a, b in zip(y, p))
    fp = sum(a == 0 and b == 1 for a, b in zip(y, p))
    fn = sum(a == 1 and b == 0 for a, b in zip(y, p))
    return tp, len(y) - tp - fp - fn, fp, fn


def full_results(stats):
    lines = []
    for model, exps in stats["models"].items():
        best = max(exps, key=lambda e: exps[e]["f1"])
        rows = []
        for e in sorted(exps, key=int):
            c = exps[e]
            f1 = f"\\textbf{{{c['f1']:.4f}}}" if e == best else f"{c['f1']:.4f}"
            ci = c["ci_scenario"]
            if e == "1":
                tests = "-- & -- & --"
            else:
                tests = (f"{fmt_p(c['perm_scenario']['p_raw'])} & {fmt_p(c['perm_meta_rule']['p_raw'])} "
                         f"& {fmt_p(c['mcnemar']['p_raw'])}")
            rows.append(f"& {EXPS[e]:<24} & {f1} & [{ci[0]:.2f}, {ci[1]:.2f}] & {c['mcc']:.3f} "
                        f"& {c['balanced_accuracy']:.3f} & {c['macro_f1_per_rule']:.3f} & {tests} \\\\")
        lines.append(f"\\multirow{{{len(rows)}}}{{*}}{{{model}}}")
        lines += rows
        lines.append("\\hline")
    return "\n".join(lines)


def confusion_table(matrix, stats):
    y = matrix["ground_truth"]
    out = []
    for model in LOCAL:
        exps = matrix["predictions"][model]
        best = max(exps, key=lambda e: stats["models"][model][e]["f1"])
        chosen = ["1", "3", "4"] + ([best] if best not in ("1", "3", "4") else [])
        out.append(f"\\multirow{{{len(chosen)}}}{{*}}{{{short(model)}}}")
        for e in chosen:
            tp, tn, fp, fn = confusion(y, exps[e])
            f1 = stats["models"][model][e]["f1"]
            f1s = f"\\textbf{{{f1:.4f}}}" if e == best else f"{f1:.4f}"
            out.append(f"& {e} & {ABBR[e]} & {tp} & {tn} & {fp} & {fn} & {f1s} \\\\")
        out.append("\\hline")
    return "\n".join(out)


def heatmap(stats):
    out = []
    for row, model in zip([4, 3, 2, 1], LOCAL):
        exps = stats["models"][model]
        best = max(exps, key=lambda e: exps[e]["f1"])
        out.append(f"% {short(model)} row (y={row})")
        for e in sorted(exps, key=int):
            v = exps[e]["f1"]
            x = (int(e) - 1) * 2 + 0.5
            green = max(0, min(100, int(round((v - 0.40) / 0.50 * 100))))
            label = f"\\textbf{{{v:.3f}}}" if e == best else f"{v:.3f}"
            out.append(f"\\fill[green!{green}!red!55] ({x},{row - 0.5}) rectangle ({x + 1.8},{row + 0.5}); "
                       f"\\node[font=\\small] at ({x + 0.9},{row}) {{{label}}};")
    return "\n".join(out)


def forest(stats):
    out = []
    for block, model in enumerate(reversed(LOCAL)):
        exps = stats["models"][model]
        out.append(f"% {short(model)} (positions {block * 8 + 1}-{block * 8 + 8}, Exp8 down to Exp1)")
        for pos, e in enumerate(sorted(exps, key=int, reverse=True), start=block * 8 + 1):
            c = exps[e]
            lo, hi = c["ci_scenario"]
            out.append(f"    ({c['f1']:.4f},{pos}) +- ({c['f1'] - lo:.4f},{hi - c['f1']:.4f}) "
                       f"% Exp{e} CI [{lo:.2f}, {hi:.2f}]")
    return "\n".join(out)


def delta(stats):
    out = []
    for model in LOCAL:
        exps = stats["models"][model]
        base = exps["1"]["f1"]
        coords = " ".join(f"({ABBR[e]}, {exps[e]['f1'] - base:.3f})" for e in sorted(exps, key=int) if e != "1")
        out.append(f"% {short(model)} (baseline={base:.4f})\n\\addplot coordinates {{{coords}}};")
    return "\n".join(out)


def cost(stats):
    out = []
    for model in stats["models"]:
        cm = stats["cost_minimizing"][model]
        cells = " & ".join(f"{ABBR[cm[r]['exp']]} ({cm[r]['cost']:.3f})" for r in ("1", "2", "5", "10"))
        out.append(f"{short(model)} & {cells} \\\\")
    return "\n".join(out)


def interactions(inter):
    out = []
    for model, res in inter["models"].items():
        cells = []
        for contrast in ("structured_prompting", "rag"):
            v = res["scenario"][contrast]["metrics"]["f1"]
            cells.append(f"${v['estimate']:+.3f}$ [${v['ci_grouped_95'][0]:+.3f}$, ${v['ci_grouped_95'][1]:+.3f}$]")
        out.append(f"{short(model)} & {cells[0]} & {cells[1]} \\\\")
    return "\n".join(out)


def subsets(sub):
    out = []
    reg = sub["cells"]["regex_baseline"]["-"]
    out.append(f"Regex baseline & -- & {reg['f1']:.3f} & {reg['acc_original32']:.3f} & {reg['acc_extension64']:.3f} "
               f"& {reg['specificity_typeB']:.3f} & {reg['recall_typeC']:.3f} \\\\ \\hline")
    for model, b in sub["best_per_model"].items():
        c = sub["cells"][model][b["exp"]]
        out.append(f"{short(model)} & {ABBR[b['exp']]} & {c['f1']:.3f} & {c['acc_original32']:.3f} "
                   f"& {c['acc_extension64']:.3f} & {c['specificity_typeB']:.3f} & {c['recall_typeC']:.3f} \\\\")
    return "\n".join(out)


def comparison(cmp, a, b, exps=None):
    out = []
    for r in cmp["rows"]:
        if exps and r["exp"] not in exps:
            continue
        lo, hi = r["delta_f1_ci_scenario"]
        out.append(f"{short(r['model'])} & {ABBR[r['exp']]} & {r[f'f1_{a}']:.3f} & {r[f'f1_{b}']:.3f} "
                   f"& ${r['delta_f1']:+.3f}$ & [${lo:+.3f}$, ${hi:+.3f}$] & {fmt_p(r['p_raw'])} "
                   f"& {fmt_p(r['p_holm'])} \\\\")
    s = cmp["summary"]
    out.append(f"% summary: cells={s['cells']} mean_delta={s['mean_delta_f1']:+.4f} "
               f"{b}_better={s['b_better']} {b}_worse={s['b_worse']}")
    return "\n".join(out)


def frontier(conds):
    out = []
    for cond, stats in conds.items():
        for model, exps in stats["models"].items():
            if not model.startswith("Gemini"):
                continue
            for e in sorted(exps, key=int):
                c = exps[e]
                p = "--" if e == "1" else fmt_p(c["perm_scenario"]["p_raw"])
                out.append(f"{cond} & {short(model)} & {ABBR[e]} & {c['f1']:.3f} & [{c['ci_scenario'][0]:.2f}, "
                           f"{c['ci_scenario'][1]:.2f}] & {c['mcc']:.3f} & {c['balanced_accuracy']:.3f} & {p} \\\\")
    return "\n".join(out)


def calibration(cal32, cal96):
    names = {"vg": "V(G) mean", "ast_depth": "AST depth mean", "fog": "Gunning Fog mean",
             "lex_density": "TTR (``lexical density'')", "mattr50": "MATTR-50",
             "content_density": "Content-word density", "ttr_first150": "TTR, first 150 words",
             "word_count": "Words per document"}
    out = []
    priv = cal96["private_remeasured"]
    for key, label in names.items():
        p = priv.get(key)
        cells = [label, f"{p['mean']:.2f}" if p else "--"]
        for cal in (cal32, cal96):
            s = cal["synthetic"].get(key)
            c = cal.get("comparison", {}).get(key, {})
            if not s:
                cells += ["--", "--"]
                continue
            verdict = ""
            if "within_tolerance" in c:
                verdict = ("\\checkmark" if c["within_tolerance"] else "\\texttimes") + \
                          (" (TOST)" if c.get("tost_equivalent") else "")
            cells += [f"{s['mean']:.2f} (n={s['n']})", verdict or "--"]
        out.append(" & ".join(cells) + " \\\\")
    return "\n".join(out)


def pr_scatter(matrix, stats):
    y = matrix["ground_truth"]
    out = []
    for model in LOCAL:
        exps = matrix["predictions"][model]
        best = max(exps, key=lambda e: stats["models"][model][e]["f1"])
        chosen = ["1", "2", "3", "4"] + ([best] if best not in ("1", "2", "3", "4") else [])
        out.append(f"% {short(model)}")
        for e in chosen:
            tp, tn, fp, fn = confusion(y, exps[e])
            prec = tp / (tp + fp) if tp + fp else 0.0
            out.append(f"    ({prec:.3f}, {tp / (tp + fn):.3f})  % Exp{e} {ABBR[e]}: TP={tp} FP={fp} FN={fn}")
    return "\n".join(out)


def radar(stats):
    out = []
    for model in LOCAL:
        e = stats["models"][model]
        out.append(f"% {short(model)}: Baseline={e['1']['f1']:.3f} ZS={e['2']['f1']:.3f} "
                   f"Steer={e['4']['f1']:.3f} Synergy(Exp8)={e['8']['f1']:.3f}")
    return "\n".join(out)


def confmat_figure(matrix, stats):
    y = matrix["ground_truth"]
    out = []
    for model in LOCAL:
        exps = matrix["predictions"][model]
        best = max(exps, key=lambda e: stats["models"][model][e]["f1"])
        cells = []
        for e in ("1", "3", "4", best):
            tp, tn, fp, fn = confusion(y, exps[e])
            cells.append(f"Exp{e}: TP={tp} FP={fp} FN={fn} TN={tn} F1={stats['models'][model][e]['f1']:.3f}")
        out.append(f"% {short(model)}: " + " | ".join(cells))
    return "\n".join(out)


def hardest(sub, k=12):
    out = []
    for h in sub["hardest"][:k]:
        adv = {"tipo_b": "Type-B", "tipo_c": "Type-C"}.get(h["adversarial"], "core")
        ident = h["id"].replace("_", "\\_")
        out.append(f"\\texttt{{{ident}}} & {h['meta_rule']} & {h['label']} & {adv} & {h['errors']}/{h['cells']} \\\\")
    out.append("% common best-configuration errors: " + ", ".join(sub["common_best_config_errors"]))
    return "\n".join(out)


def language_table(stats_by_cond, cmp_es_en):
    rows = {(r["model"], r["exp"]): r for r in cmp_es_en["rows"]}
    out = []
    for model in LOCAL:
        out.append(f"\\multirow{{8}}{{*}}{{{short(model)}}}")
        for e in map(str, range(1, 9)):
            vals = [stats_by_cond[c]["models"][model][e]["f1"] for c in ("mixed", "es", "en")]
            r = rows[(model, e)]
            lo, hi = r["delta_f1_ci_scenario"]
            star = "$^{*}$" if r["p_holm"] < 0.05 else ""
            out.append(f"& {ABBR[e]} & {vals[0]:.3f} & {vals[1]:.3f} & {vals[2]:.3f} & "
                       f"${r['delta_f1']:+.3f}${star} & [${lo:+.3f}$, ${hi:+.3f}$] \\\\")
        out.append("\\hline")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    def write(name, text):
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"[+] {name}")

    stats = {c: load(f"statistical_analysis_n96_{c}.json") for c in ("mixed", "es", "en", "noisy")}
    matrix = load("predictions_n96_mixed.json")
    if stats["mixed"]:
        local_stats = {"models": {m: v for m, v in stats["mixed"]["models"].items() if m in LOCAL},
                       "cost_minimizing": stats["mixed"]["cost_minimizing"]}
        write("full_results.tex", full_results(local_stats))
        write("confusion.tex", confusion_table(matrix, local_stats))
        write("heatmap.tex", heatmap(local_stats))
        write("forest.tex", forest(local_stats))
        write("delta.tex", delta(local_stats))
        write("cost.tex", cost(local_stats))
        write("pr_scatter.tex", pr_scatter(matrix, local_stats))
        write("radar.tex", radar(local_stats))
        write("confmat_figure.tex", confmat_figure(matrix, local_stats))
    for cond in ("mixed", "es", "en"):
        inter = load(f"steering_interaction_n96_{cond}.json")
        if inter:
            write(f"interactions_{cond}.tex", interactions(inter))
    sub = load("subset_analysis_n96_mixed.json")
    if sub:
        write("subsets.tex", subsets(sub))
        write("hardest.tex", hardest(sub))
    cmp_es_en = load("compare_n96_es_vs_en.json")
    if cmp_es_en and all(stats[c] for c in ("mixed", "es", "en")):
        write("language_table.tex", language_table(stats, cmp_es_en))
    for a, b, name, exps in (("es", "en", "language_es_en.tex", None),
                             ("mixed", "es", "language_mixed_es.tex", None),
                             ("mixed", "en", "language_mixed_en.tex", None),
                             ("mixed", "noisy", "noise.tex", None)):
        cmp = load(f"compare_n96_{a}_vs_{b}.json")
        if cmp:
            write(name, comparison(cmp, a, b, exps))
    conds = {c: s for c, s in stats.items() if s and any(m.startswith("Gemini") for m in s["models"])}
    if conds:
        write("frontier.tex", frontier(conds))
    cal32, cal96 = load("calibration_n32.json"), load("calibration_n96.json")
    if cal32 and cal96:
        write("calibration.tex", calibration(cal32, cal96))


if __name__ == "__main__":
    main()
