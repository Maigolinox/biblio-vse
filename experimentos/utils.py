import os, sys, gc

_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_UTILS_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, precision_score, recall_score,
)
from model_loader import CATALOGO_MODELOS

DATASET_PATH = os.path.join(_ROOT, "dataset_isomorfico.json")

# Order from largest to smallest: ensures the largest model loads with a clean GPU.
# Gemma-2-9B ~4.5 GB  →  Mistral-7B / Qwen2.5-7B ~3.5 GB  →  Phi-3.5-mini ~1.9 GB
ORDEN_MODELOS = ["gemma2", "mistral", "qwen25", "phi35"]

SYSTEM_INSTRUCTION = (
    "You are a Software Quality Auditor expert in the ISO/IEC 29110 standard. "
    "Your sole task is to evaluate artifacts and determine whether they comply with an "
    "organizational meta-rule. You must respond ONLY with the number 1 if the artifact "
    "complies with the rule, or with the number 0 if it violates it. Do not give explanations."
)

SYSTEM_ZEROSHOT = (
    "You are a certified Software Quality Auditor, specialized in the ISO/IEC 29110 standard "
    "for VSEs (Very Small Entities). Your function is to evaluate software artifacts and "
    "determine whether they comply with a specific organizational meta-rule.\n\n"
    "EVALUATION PROCESS:\n"
    "1. Analyze the artifact type and its context.\n"
    "2. Identify what the indicated meta-rule requires.\n"
    "3. Determine whether the artifact explicitly satisfies that requirement.\n"
    "4. Respond ONLY with the digit 1 (compliant) or 0 (violation). No explanations."
)

_CRITERIOS_ZEROSHOT = (
    "COMPLIANCE CRITERIA BY META-RULE (all nine ISO/IEC 29110 organizational meta-rules):\n"
    "- DOCUMENTAL / DOCUMENTATION: The document must include artifact code, formal version, and effective date.\n"
    "- CALIDAD / QUALITY: The code must follow style standards (correct indentation, clean imports, naming conventions).\n"
    "- SEGURIDAD / SECURITY: No credentials, tokens, or secrets must exist in plaintext (hardcoded).\n"
    "- TRAZABILIDAD / TRACEABILITY: The artifact must explicitly reference requirement IDs (e.g. RF_XX, US_XX).\n"
    "- INFRA: The configuration must be restricted to authorized internal hosts or environments.\n"
    "- GOBERNANZA / GOVERNANCE: The artifact must evidence formally documented controls, approvals, or policies.\n"
    "- PRUEBAS / TESTING: The artifact must include test case IDs, execution steps, expected results, "
    "and a traceable link to an associated requirement.\n"
    "- RESPALDO / BACKUP: The artifact must specify backup type (full/incremental), schedule, "
    "recovery procedure, or a verified storage location (e.g. backup, pg_dump, restore).\n"
    "- ACUERDOS / AGREEMENTS: The artifact must identify parties, state responsibilities, "
    "record a formally approved status, and include authorized signatures.\n"
)

_SISTEMA_NEUTRAL = "You are a software quality evaluation assistant."

# English anchor prompts (original, used in the paper's main experiments)
_PROMPT_ESTRICTO = (
    "Act as an extremely strict quality auditor, "
    "uncompromising and precisely adhering to the ISO/IEC 29110 standard."
)
_PROMPT_RELAJADO = (
    "Act as a relaxed, careless, and permissive auditor. "
    "You do not care about standards or security."
)

# Spanish anchor prompts for T1-B: language-confound ablation.
# The original anchors are English while artifacts and ZS prompts are Spanish.
# These Spanish equivalents allow testing whether the steering vector encodes
# compliance semantics or merely a language/persona direction.
_PROMPT_ESTRICTO_ES = (
    "Actúa como un auditor de calidad extremadamente estricto, "
    "preciso e inflexible en el cumplimiento de las normas ISO/IEC 29110."
)
_PROMPT_RELAJADO_ES = (
    "Actúa como un auditor descuidado, permisivo e indiferente "
    "a las normas de calidad y seguridad."
)


# ── Model load / unload ───────────────────────────────────────────────────────

def _log_vram(prefix: str = ""):
    if torch.cuda.is_available():
        free_gb  = torch.cuda.mem_get_info()[0] / 1024 ** 3
        total_gb = torch.cuda.get_device_properties(0).total_memory / 1024 ** 3
        alloc_mb = torch.cuda.memory_allocated() / 1024 ** 2
        tag = f"  [{prefix}] " if prefix else "  "
        print(f"{tag}VRAM free: {free_gb:.1f}/{total_gb:.1f} GB  |  torch allocated: {alloc_mb:.0f} MB")


def cargar_modelo_por_clave(clave: str):
    conf = CATALOGO_MODELOS[clave]
    model_id = conf["model_id"]
    _log_vram("before loading")
    print(f"  [*] Loading {conf['nombre']} ({model_id})...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    try:
        from transformers import BitsAndBytesConfig
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            # DO NOT use llm_int8_enable_fp32_cpu_offload=True:
            # that flag activates CPU dispatch, incompatible with Params4bit in this bnb version
        )
        modelo = AutoModelForCausalLM.from_pretrained(
            model_id, quantization_config=quant_config, device_map="auto"
        )
        print("  [+] 4-bit NF4 quantization active.")
    except ImportError:
        modelo = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float16, device_map="auto"
        )
        print("  [!] bitsandbytes not available — float16 without quantization.")
    print(f"  [+] {conf['nombre']} ready.")
    return modelo, tokenizer, conf


def limpiar_vram():
    """Clears VRAM. Call AFTER doing `del model, tokenizer` in the caller's scope."""
    # Three cycles: the first frees simple objects, subsequent ones break reference cycles
    for _ in range(3):
        gc.collect()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        if hasattr(torch.cuda, "ipc_collect"):
            torch.cuda.ipc_collect()
    _log_vram("after freeing")


# ── Prompt helpers ────────────────────────────────────────────────────────────

def formatear_prompt(tokenizer, user_content: str, system_content: str = SYSTEM_INSTRUCTION) -> str:
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": user_content},
    ]
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        combined = f"{system_content}\n\n{user_content}"
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": combined}],
            tokenize=False, add_generation_prompt=True,
        )


def formatear_prompt_sin_sistema(tokenizer, user_content: str) -> str:
    """Version without system role for the pure baseline experiment."""
    messages = [{"role": "user", "content": user_content}]
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        return user_content


def prompt_basico(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    return (
        f"Meta-rule: {meta_rule}\n"
        f"Artifact type: {artifact_type}\n"
        f"Content:\n```\n{artifact_content}\n```\n\n"
        f"Does this artifact comply with meta-rule {meta_rule}?\n"
        f"Respond ONLY with 1 (compliant) or 0 (violation)."
    )


def prompt_zeroshot(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    return (
        f"META-RULE TO EVALUATE: {meta_rule}\n\n"
        f"{_CRITERIOS_ZEROSHOT}\n"
        f"ARTIFACT TO AUDIT\n"
        f"Type: {artifact_type}\n"
        f"Content:\n```\n{artifact_content}\n```\n\n"
        f"Does this artifact comply with meta-rule {meta_rule}?\n"
        f"Respond ONLY with 1 (compliant) or 0 (violation)."
    )


def prompt_rag(meta_rule: str, artifact_type: str, artifact_content: str,
               documentary_context: str) -> str:
    return (
        f"RETRIEVED NORMATIVE CONTEXT FOR '{meta_rule}':\n"
        f"{documentary_context}\n\n"
        f"───\n"
        f"ARTIFACT TO AUDIT (Type: {artifact_type}):\n"
        f"```\n{artifact_content}\n```\n\n"
        f"Based on the normative context above, does this artifact comply with "
        f"meta-rule {meta_rule}?\n"
        f"Respond ONLY with 1 (compliant) or 0 (violation)."
    )


def prompt_zeroshot_rag(meta_rule: str, artifact_type: str, artifact_content: str,
                        documentary_context: str) -> str:
    return (
        f"META-RULE TO EVALUATE: {meta_rule}\n\n"
        f"{_CRITERIOS_ZEROSHOT}\n"
        f"RETRIEVED NORMATIVE CONTEXT:\n"
        f"{documentary_context}\n\n"
        f"───\n"
        f"ARTIFACT TO AUDIT (Type: {artifact_type}):\n"
        f"```\n{artifact_content}\n```\n\n"
        f"Does this artifact comply with meta-rule {meta_rule}?\n"
        f"Respond ONLY with 1 (compliant) or 0 (violation)."
    )


# ── Inference ────────────────────────────────────────────────────────────────

def generar_con_modelo(modelo, tokenizer, prompt_text: str) -> str:
    inputs = tokenizer(prompt_text, return_tensors="pt").to(modelo.device)
    eos_id = tokenizer.eos_token_id
    if isinstance(eos_id, list):
        eos_id = eos_id[0]
    with torch.no_grad():
        output_ids = modelo.generate(
            **inputs,
            max_new_tokens=10,
            do_sample=False,
            temperature=None,
            top_p=None,
            top_k=None,
            pad_token_id=eos_id,
        )
    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


def extraer_prediccion(resultado: str) -> int:
    """Returns 1, 0 or -1 if the response is not binary."""
    if "1" in resultado:
        return 1
    elif "0" in resultado:
        return 0
    return -1


# ── Metrics ───────────────────────────────────────────────────────────────────

def imprimir_resultados(nombre_modelo: str, y_verdadero: list, y_prediccion: list,
                        fallos_inferencia: int = 0):
    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  RESULTS — {nombre_modelo}")
    print(sep)
    if fallos_inferencia:
        print(f"  [!] Non-binary responses (penalized as 0): {fallos_inferencia}")
    print("\n  Confusion Matrix (rows=actual, cols=predicted) [0,1]:")
    print(confusion_matrix(y_verdadero, y_prediccion))
    print("\n  Detailed metrics:")
    print(
        classification_report(
            y_verdadero, y_prediccion,
            target_names=["Violation (0)", "Compliant (1)"],
            zero_division=0,
        )
    )
    f1  = f1_score(y_verdadero, y_prediccion, zero_division=0)
    pre = precision_score(y_verdadero, y_prediccion, zero_division=0)
    rec = recall_score(y_verdadero, y_prediccion, zero_division=0)
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  Precision : {pre:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(sep)


# ── Activation Steering ───────────────────────────────────────────────────────

def calcular_vector_steering(modelo, tokenizer, capa: int, lang: str = "en"):
    """Compute the compliance steering direction v = H(p⁺) - H(p⁻) at layer `capa`.

    lang="en" uses English anchors (original paper).
    lang="es" uses Spanish anchors (T1-B ablation: language-confound control).
    """
    if lang == "es":
        p_pos, p_neg = _PROMPT_ESTRICTO_ES, _PROMPT_RELAJADO_ES
    else:
        p_pos, p_neg = _PROMPT_ESTRICTO, _PROMPT_RELAJADO
    print(f"  [*] Computing steering vector at layer {capa} (anchors: {lang})...")
    prompt_pos = formatear_prompt(tokenizer, p_pos, _SISTEMA_NEUTRAL)
    prompt_neg = formatear_prompt(tokenizer, p_neg, _SISTEMA_NEUTRAL)

    inputs_pos = tokenizer(prompt_pos, return_tensors="pt").to(modelo.device)
    inputs_neg = tokenizer(prompt_neg, return_tensors="pt").to(modelo.device)

    with torch.no_grad():
        out_pos = modelo(**inputs_pos, output_hidden_states=True)
        out_neg = modelo(**inputs_neg, output_hidden_states=True)

    h_pos = out_pos.hidden_states[capa][:, -1, :]
    h_neg = out_neg.hidden_states[capa][:, -1, :]
    vector = (h_pos - h_neg).unsqueeze(1)
    print("  [+] Steering vector computed.")
    return vector


def crear_steering_hook(vector_dir, alpha: float):
    def hook(module, input_args, output):
        if isinstance(output, torch.Tensor):
            return output + (alpha * vector_dir.to(output.device))
        hidden_states = output[0]
        steered = hidden_states + (alpha * vector_dir.to(hidden_states.device))
        return (steered,) + output[1:]
    return hook


def aplicar_steering(modelo, tokenizer, capa: int, alpha: float = 0.8,
                     lang: str = "en"):
    """Compute steering vector and register hook. Convenience wrapper for single runs."""
    vector = calcular_vector_steering(modelo, tokenizer, capa, lang=lang)
    hook_fn = crear_steering_hook(vector, alpha)
    handle = modelo.model.layers[capa].register_forward_hook(hook_fn)
    print(f"  [+] Steering active at layer {capa} (α={alpha}, lang={lang}).")
    return handle


def aplicar_steering_con_vector(modelo, vector, capa: int, alpha: float = 0.8):
    """Register steering hook with a pre-computed vector.

    Use this inside α sweeps and LOO loops to avoid recomputing the vector
    (which requires two forward passes) on every iteration.
    """
    hook_fn = crear_steering_hook(vector, alpha)
    handle = modelo.model.layers[capa].register_forward_hook(hook_fn)
    return handle
