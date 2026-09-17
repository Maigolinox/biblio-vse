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

def _argv_value(flag: str, default=None):
    """Returns the value following `flag` in sys.argv (all experiment scripts
    share these options, so they are read once here at import time)."""
    for i, v in enumerate(sys.argv):
        if v == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


# --dataset PATH: evaluation dataset (default: the original N=32 benchmark).
DATASET_PATH = os.path.abspath(
    _argv_value("--dataset", os.path.join(_ROOT, "dataset_isomorfico.json"))
)

# --prompt-lang mixed|es|en: language of the system/user prompt templates.
#   mixed : English instructions with bilingual rule names (the configuration
#           used for all results of the original submission; default).
#   es    : fully Spanish instructions and Spanish rule names.
#   en    : fully English instructions and English rule names.
PROMPT_LANG = _argv_value("--prompt-lang", "mixed")
if PROMPT_LANG not in {"mixed", "es", "en"}:
    raise ValueError("--prompt-lang must be one of: mixed, es, en")

# Order from largest to smallest: ensures the largest model loads with a clean GPU.
# Gemma-2-9B ~4.5 GB  →  Mistral-7B / Qwen2.5-7B ~3.5 GB  →  Phi-3.5-mini ~1.9 GB
ORDEN_MODELOS = ["gemma2", "mistral", "qwen25", "phi35"]
# --models k1,k2: optional subset of model keys (order preserved).
if _argv_value("--models"):
    _wanted = _argv_value("--models").split(",")
    ORDEN_MODELOS = [m for m in ORDEN_MODELOS if m in _wanted]

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


# ── Monolingual prompt templates (language-specific pipeline, revision R1) ────
# "mixed" keeps the original strings above byte-for-byte. "en" differs from
# "mixed" only in using English rule names; "es" is a faithful Spanish
# translation of every instruction string.

_CRITERIOS_ZEROSHOT_EN = (
    "COMPLIANCE CRITERIA BY META-RULE (all nine ISO/IEC 29110 organizational meta-rules):\n"
    "- DOCUMENTATION: The document must include artifact code, formal version, and effective date.\n"
    "- QUALITY: The code must follow style standards (correct indentation, clean imports, naming conventions).\n"
    "- SECURITY: No credentials, tokens, or secrets must exist in plaintext (hardcoded).\n"
    "- TRACEABILITY: The artifact must explicitly reference requirement IDs (e.g. RF_XX, US_XX).\n"
    "- INFRA: The configuration must be restricted to authorized internal hosts or environments.\n"
    "- GOVERNANCE: The artifact must evidence formally documented controls, approvals, or policies.\n"
    "- TESTING: The artifact must include test case IDs, execution steps, expected results, "
    "and a traceable link to an associated requirement.\n"
    "- BACKUP: The artifact must specify backup type (full/incremental), schedule, "
    "recovery procedure, or a verified storage location (e.g. backup, pg_dump, restore).\n"
    "- AGREEMENTS: The artifact must identify parties, state responsibilities, "
    "record a formally approved status, and include authorized signatures.\n"
)

_SYSTEM_INSTRUCTION_ES = (
    "Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. "
    "Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla "
    "organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple "
    "la regla, o con el número 0 si la viola. No des explicaciones."
)

_SYSTEM_ZEROSHOT_ES = (
    "Eres un Auditor de Calidad de Software certificado, especializado en el estándar "
    "ISO/IEC 29110 para VSE (Entidades Muy Pequeñas). Tu función es evaluar artefactos "
    "de software y determinar si cumplen con una meta-regla organizacional específica.\n\n"
    "PROCESO DE EVALUACIÓN:\n"
    "1. Analiza el tipo de artefacto y su contexto.\n"
    "2. Identifica lo que exige la meta-regla indicada.\n"
    "3. Determina si el artefacto satisface explícitamente ese requisito.\n"
    "4. Responde ÚNICAMENTE con el dígito 1 (cumple) o 0 (violación). Sin explicaciones."
)

_CRITERIOS_ZEROSHOT_ES = (
    "CRITERIOS DE CUMPLIMIENTO POR META-REGLA (las nueve meta-reglas organizacionales ISO/IEC 29110):\n"
    "- DOCUMENTAL: El documento debe incluir código de artefacto, versión formal y fecha de vigencia.\n"
    "- CALIDAD: El código debe seguir estándares de estilo (indentación correcta, imports limpios, convenciones de nombres).\n"
    "- SEGURIDAD: No deben existir credenciales, tokens ni secretos en texto plano (hardcoded).\n"
    "- TRAZABILIDAD: El artefacto debe referenciar explícitamente IDs de requerimientos (p. ej. RF_XX, US_XX).\n"
    "- INFRA: La configuración debe estar restringida a hosts o entornos internos autorizados.\n"
    "- GOBERNANZA: El artefacto debe evidenciar controles, aprobaciones o políticas formalmente documentados.\n"
    "- PRUEBAS: El artefacto debe incluir IDs de casos de prueba, pasos de ejecución, resultados esperados "
    "y un vínculo trazable a un requerimiento asociado.\n"
    "- RESPALDO: El artefacto debe especificar el tipo de respaldo (completo/incremental), la periodicidad, "
    "el procedimiento de recuperación o una ubicación de almacenamiento verificada (p. ej. backup, pg_dump, restore).\n"
    "- ACUERDOS: El artefacto debe identificar a las partes, establecer responsabilidades, "
    "registrar un estado formalmente aprobado e incluir firmas autorizadas.\n"
)

_PLANTILLAS = {
    "en": {
        "rule": "Meta-rule", "type": "Artifact type", "content": "Content",
        "artifact": "Artifact",
        "ask": "Does this artifact comply with meta-rule {r}?",
        "only": "Respond ONLY with 1 (compliant) or 0 (violation).",
        "base_ask": "Does it comply (1) or violate (0) the meta-rule? Respond only 1 or 0.",
        "to_eval": "META-RULE TO EVALUATE", "to_audit": "ARTIFACT TO AUDIT",
        "ctx_for": "RETRIEVED NORMATIVE CONTEXT FOR '{r}'",
        "ctx": "RETRIEVED NORMATIVE CONTEXT",
        "rag_ask": "Based on the normative context above, does this artifact comply with "
                   "meta-rule {r}?",
        "type_inline": "Type",
    },
    "es": {
        "rule": "Meta-regla", "type": "Tipo de artefacto", "content": "Contenido",
        "artifact": "Artefacto",
        "ask": "¿Este artefacto cumple con la meta-regla {r}?",
        "only": "Responde ÚNICAMENTE con 1 (cumple) o 0 (violación).",
        "base_ask": "¿Cumple (1) o viola (0) la meta-regla? Responde solo 1 o 0.",
        "to_eval": "META-REGLA A EVALUAR", "to_audit": "ARTEFACTO A AUDITAR",
        "ctx_for": "CONTEXTO NORMATIVO RECUPERADO PARA '{r}'",
        "ctx": "CONTEXTO NORMATIVO RECUPERADO",
        "rag_ask": "Con base en el contexto normativo anterior, ¿este artefacto cumple con "
                   "la meta-regla {r}?",
        "type_inline": "Tipo",
    },
}
_PLANTILLAS["mixed"] = _PLANTILLAS["en"]
_T = _PLANTILLAS[PROMPT_LANG]

if PROMPT_LANG == "es":
    SYSTEM_INSTRUCTION = _SYSTEM_INSTRUCTION_ES
    SYSTEM_ZEROSHOT = _SYSTEM_ZEROSHOT_ES
    _CRITERIOS_ZEROSHOT = _CRITERIOS_ZEROSHOT_ES
elif PROMPT_LANG == "en":
    _CRITERIOS_ZEROSHOT = _CRITERIOS_ZEROSHOT_EN


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


def prompt_baseline(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    """Unstructured prompt of Exp 1 (no system role)."""
    return (
        f"{_T['rule']}: {meta_rule}\n"
        f"{_T['type']}: {artifact_type}\n"
        f"{_T['artifact']}:\n{artifact_content}\n\n"
        f"{_T['base_ask']}"
    )


def prompt_basico(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    return (
        f"{_T['rule']}: {meta_rule}\n"
        f"{_T['type']}: {artifact_type}\n"
        f"{_T['content']}:\n```\n{artifact_content}\n```\n\n"
        f"{_T['ask'].format(r=meta_rule)}\n"
        f"{_T['only']}"
    )


def prompt_zeroshot(meta_rule: str, artifact_type: str, artifact_content: str) -> str:
    return (
        f"{_T['to_eval']}: {meta_rule}\n\n"
        f"{_CRITERIOS_ZEROSHOT}\n"
        f"{_T['to_audit']}\n"
        f"{_T['type_inline']}: {artifact_type}\n"
        f"{_T['content']}:\n```\n{artifact_content}\n```\n\n"
        f"{_T['ask'].format(r=meta_rule)}\n"
        f"{_T['only']}"
    )


def prompt_rag(meta_rule: str, artifact_type: str, artifact_content: str,
               documentary_context: str) -> str:
    return (
        f"{_T['ctx_for'].format(r=meta_rule)}:\n"
        f"{documentary_context}\n\n"
        f"───\n"
        f"{_T['to_audit']} ({_T['type_inline']}: {artifact_type}):\n"
        f"```\n{artifact_content}\n```\n\n"
        f"{_T['rag_ask'].format(r=meta_rule)}\n"
        f"{_T['only']}"
    )


def prompt_zeroshot_rag(meta_rule: str, artifact_type: str, artifact_content: str,
                        documentary_context: str) -> str:
    return (
        f"{_T['to_eval']}: {meta_rule}\n\n"
        f"{_CRITERIOS_ZEROSHOT}\n"
        f"{_T['ctx']}:\n"
        f"{documentary_context}\n\n"
        f"───\n"
        f"{_T['to_audit']} ({_T['type_inline']}: {artifact_type}):\n"
        f"```\n{artifact_content}\n```\n\n"
        f"{_T['ask'].format(r=meta_rule)}\n"
        f"{_T['only']}"
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
