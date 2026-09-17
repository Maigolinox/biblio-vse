# RUN ONE EXPERIMENTAL CONDITION (Exp 1-8 x 4 local models) ON THE N=96 BENCHMARK
#
# Each condition fixes the dataset language, the prompt language, the steering
# anchor language, and the RAG corpus:
#
#   mixed : Spanish artifacts, English instructions (bilingual rule names),
#           Spanish anchors, official English guide  -> original submission design
#   es    : Spanish artifacts, Spanish instructions, Spanish anchors,
#           official Spanish guide                    -> monolingual Spanish
#   en    : English artifacts, English instructions, English anchors,
#           official English guide                    -> monolingual English
#   noisy : "mixed" design on the noise-injected dataset (robustness stress test)
#
# Every experiment writes its own log to resultados/n96/<condition>/exp<N>.txt.
# Completed logs (ending with the "completed" marker) are skipped, so the runner
# can be restarted after an interruption.
#
# Usage (from repo root, inside the aud_llm environment):
#   python experimentos/run_condition.py --condition mixed
#   python experimentos/run_condition.py --condition noisy --exps 1,2,5,6
#   python experimentos/run_condition.py --condition en --models phi35

import argparse
import os
import subprocess
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)

SCRIPTS = {
    1: "experimento_baseline_1.py",
    2: "experimento_zeroshot_2.py",
    3: "experimento_rag_3.py",
    4: "experimento_steering_4.py",
    5: "experimento_zeroshot_rag_5.py",
    6: "experimento_zeroshot_steering_6.py",
    7: "experimento_rag_steering_7.py",
    8: "experimento_zeroshot_rag_steering_8.py",
}
RAG_EXPS = {3, 5, 7, 8}
STEERING_EXPS = {4, 6, 7, 8}

CONDITIONS = {
    "mixed": {"dataset": "dataset_isomorfico_n96.json", "prompt_lang": "mixed",
              "anchors": "es", "corpus": "official"},
    "es":    {"dataset": "dataset_isomorfico_n96.json", "prompt_lang": "es",
              "anchors": "es", "corpus": "official_es"},
    "en":    {"dataset": "dataset_isomorfico_n96_en.json", "prompt_lang": "en",
              "anchors": "en", "corpus": "official"},
    "noisy": {"dataset": "dataset_isomorfico_n96_noisy.json", "prompt_lang": "mixed",
              "anchors": "es", "corpus": "official"},
}

DONE_MARKER = "completed."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=sorted(CONDITIONS))
    ap.add_argument("--exps", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--models", default=None,
                    help="comma-separated model keys (default: all four)")
    args = ap.parse_args()

    cond = CONDITIONS[args.condition]
    out_dir = os.path.join(_ROOT, "resultados", "n96", args.condition)
    os.makedirs(out_dir, exist_ok=True)

    for exp in [int(e) for e in args.exps.split(",")]:
        log_path = os.path.join(out_dir, f"exp{exp}.txt")
        if os.path.exists(log_path):
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                if DONE_MARKER in fh.read()[-400:]:
                    print(f"[=] {args.condition} Exp {exp}: already complete, skipping")
                    continue

        cmd = [sys.executable, "-u", os.path.join(_DIR, SCRIPTS[exp]),
               "--dataset", os.path.join(_ROOT, cond["dataset"]),
               "--prompt-lang", cond["prompt_lang"]]
        if exp in RAG_EXPS:
            cmd += ["--rag-corpus", cond["corpus"]]
        if exp in STEERING_EXPS:
            cmd += ["--lang", cond["anchors"]]
        if args.models:
            cmd += ["--models", args.models]

        print(f"[>] {args.condition} Exp {exp}: {' '.join(cmd[2:])}", flush=True)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        with open(log_path, "w", encoding="utf-8") as log:
            log.write(f"# condition={args.condition} " + " ".join(cmd[2:]) + "\n")
            log.flush()
            proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                                  cwd=_ROOT, env=env)
        if proc.returncode != 0:
            print(f"[!] {args.condition} Exp {exp} failed (exit {proc.returncode}); "
                  f"see {log_path}")
            sys.exit(proc.returncode)
        print(f"[+] {args.condition} Exp {exp} done", flush=True)


if __name__ == "__main__":
    main()
