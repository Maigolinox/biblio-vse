# FRONTIER-MODEL REFERENCE — GEMINI (Exp 1, 2, 3, 5)
#
# Evaluates a hosted frontier model with exactly the same prompts, retrieval
# pipeline, and datasets as the local open-weight models. Activation steering
# (Exp 4, 6, 7, 8) requires access to hidden states and is therefore not
# applicable to a hosted API.
#
# The API key is read from the GEMINI_API_KEY environment variable or from a
# GEMINI_API_KEY=... line in the repository's .env file (never committed).
# Every response is cached in resultados/n96/gemini_cache.jsonl, so interrupted
# runs resume without repeating (or re-billing) completed calls.
#
# Usage (from repo root):
#   python experimentos/experimento_gemini.py --condition mixed
#   python experimentos/experimento_gemini.py --condition en --model gemini-2.5-flash
#   python experimentos/experimento_gemini.py --list-models
#
# Logs: resultados/n96/<condition>/gemini_exp<N>.txt, in the same format as the
# local experiment logs (parsed by experimentos/build_matrix_n96.py).

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
for _p in (_DIR, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from run_condition import CONDITIONS


def _arg(flag, default=None):
    for i, v in enumerate(sys.argv):
        if v == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


CONDITION = _arg("--condition", "mixed")
if CONDITION not in CONDITIONS:
    sys.exit(f"--condition must be one of {sorted(CONDITIONS)}")
_cond = CONDITIONS[CONDITION]
# utils reads --dataset / --prompt-lang from sys.argv at import time.
sys.argv += ["--dataset", os.path.join(_ROOT, _cond["dataset"]),
             "--prompt-lang", _cond["prompt_lang"]]

from utils import (  # noqa: E402
    DATASET_PATH, SYSTEM_INSTRUCTION, SYSTEM_ZEROSHOT,
    prompt_baseline, prompt_zeroshot, prompt_rag, prompt_zeroshot_rag,
    extraer_prediccion, imprimir_resultados,
)

API = "https://generativelanguage.googleapis.com/v1beta"
CACHE_PATH = os.path.join(_ROOT, "resultados", "n96", "gemini_cache.jsonl")
EXPS = [int(e) for e in _arg("--exps", "1,2,3,5").split(",")]
NAMES = {1: "EXPERIMENT 1 — BASELINE (pure LLM)",
         2: "EXPERIMENT 2 — STRUCTURED ZERO-SHOT",
         3: "EXPERIMENT 3 — RAG",
         5: "EXPERIMENT 5 — ZERO-SHOT + RAG"}


def api_key():
    key = os.environ.get("GEMINI_API_KEY")
    env_file = os.path.join(_ROOT, ".env")
    if not key and os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("GEMINI_API_KEY not found (environment or .env).")
    return key


def request(method, path, body=None):
    req = urllib.request.Request(
        f"{API}/{path}", method=method,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"x-goog-api-key": api_key(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_models():
    models, token = [], None
    while True:
        page = request("GET", "models" + (f"?pageToken={token}" if token else ""))
        models += [m for m in page.get("models", [])
                   if "generateContent" in m.get("supportedGenerationMethods", [])]
        token = page.get("nextPageToken")
        if not token:
            return models


def pick_latest_flash():
    """Newest generally available Flash model (no lite/preview/experimental variants)."""
    candidates = []
    for m in list_models():
        name = m["name"].split("/", 1)[1]
        if not re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-flash", name):
            continue
        candidates.append((float(re.match(r"gemini-(\d+(?:\.\d+)?)", name).group(1)), name))
    if not candidates:
        sys.exit("No stable gemini-<version>-flash model available for this key.")
    return max(candidates)[1]


class Cache:
    def __init__(self, path):
        self.path = path
        self.data = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    rec = json.loads(line)
                    self.data[rec["key"]] = rec["text"]

    @staticmethod
    def key(model, system, user):
        return hashlib.sha256(json.dumps([model, system, user]).encode("utf-8")).hexdigest()

    def get(self, k):
        return self.data.get(k)

    def put(self, k, text):
        self.data[k] = text
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"key": k, "text": text}, ensure_ascii=False) + "\n")


def generate(model, system, user, cache):
    k = Cache.key(model, system, user)
    cached = cache.get(k)
    if cached is not None:
        return cached
    body = {
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        # Deterministic decoding; the thinking budget is disabled so that the
        # output budget is spent on the binary label, as for the local models.
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 64,
                             "thinkingConfig": {"thinkingBudget": 0}},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    for attempt in range(8):
        try:
            resp = request("POST", f"models/{model}:generateContent", body)
            cands = resp.get("candidates", [])
            parts = cands[0].get("content", {}).get("parts", []) if cands else []
            text = "".join(p.get("text", "") for p in parts).strip()
            cache.put(k, text)
            return text
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", "replace")
            if err.code == 400 and "thinking" in detail.lower() and "thinkingConfig" in body["generationConfig"]:
                body["generationConfig"].pop("thinkingConfig")
                continue
            if err.code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 2 ** attempt * 2))
                continue
            raise RuntimeError(f"HTTP {err.code}: {detail[:500]}") from err
        except (urllib.error.URLError, TimeoutError):
            time.sleep(min(60, 2 ** attempt * 2))
    raise RuntimeError("Gemini request failed after retries")


def build(exp, sample, documentos):
    rule, kind, content = sample["meta_regla"], sample["tipo_artefacto"], sample["contenido_texto"]
    if exp == 1:
        return None, prompt_baseline(rule, kind, content)
    if exp == 2:
        return SYSTEM_ZEROSHOT, prompt_zeroshot(rule, kind, content)
    from rag_utils import recuperar_contexto
    ctx = recuperar_contexto(documentos, rule, content)
    if exp == 3:
        return SYSTEM_INSTRUCTION, prompt_rag(rule, kind, content, ctx)
    return SYSTEM_ZEROSHOT, prompt_zeroshot_rag(rule, kind, content, ctx)


def main():
    if "--list-models" in sys.argv:
        for m in list_models():
            print(m["name"])
        return

    model = _arg("--model") or pick_latest_flash()
    label = "Gemini-" + model.replace("gemini-", "")
    with open(DATASET_PATH, encoding="utf-8") as fh:
        dataset = json.load(fh)
    cache = Cache(CACHE_PATH)
    out_dir = os.path.join(_ROOT, "resultados", "n96", CONDITION)
    os.makedirs(out_dir, exist_ok=True)

    documentos = None
    for exp in EXPS:
        if exp in (3, 5) and documentos is None:
            from rag_utils import cargar_documentos
            documentos = cargar_documentos(_cond["corpus"])
        log_path = os.path.join(out_dir, f"gemini_exp{exp}.txt")
        orig_stdout = sys.stdout
        with open(log_path, "w", encoding="utf-8") as log:
            sys.stdout = log
            try:
                print(f"# condition={CONDITION} model={model}")
                print(f"\n{'#' * 70}\n  {NAMES[exp]}\n{'#' * 70}")
                print(f"\n{'─' * 65}\n  Modelo: {label}\n{'─' * 65}")
                y_true, y_pred, fallos = [], [], 0
                for sample in dataset:
                    system, user = build(exp, sample, documentos)
                    pred = extraer_prediccion(generate(model, system, user, cache))
                    if pred == -1:
                        fallos += 1
                        pred = 0
                    y_true.append(sample["etiqueta_clase"])
                    y_pred.append(pred)
                    print(f"    {sample['id_muestra']}: real={sample['etiqueta_clase']} pred={pred}")
                    log.flush()
                imprimir_resultados(label, y_true, y_pred, fallos)
                print(f"\n[✓] {NAMES[exp]} completed.\n")
            finally:
                sys.stdout = orig_stdout
        print(f"[+] {CONDITION} Gemini Exp {exp} done ({label}) -> {log_path}")


if __name__ == "__main__":
    main()
