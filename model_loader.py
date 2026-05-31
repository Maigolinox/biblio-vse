import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ==============================================================
# SELECTOR DE MODELO — cambia este valor para elegir el LLM
# Opciones: "mistral" | "qwen25" | "gemma2" | "phi35"
# ==============================================================
MODELO_ACTIVO = "phi35"

CATALOGO_MODELOS = {
    "mistral": {
        "model_id":      "mistralai/Mistral-7B-Instruct-v0.2",
        "nombre":        "Mistral-7B-Instruct-v0.2",
        "capa_steering": 15,   # ~50% de 32 capas
    },
    "qwen25": {
        "model_id":      "Qwen/Qwen2.5-7B-Instruct",
        "nombre":        "Qwen2.5-7B-Instruct",
        "capa_steering": 14,   # ~50% de 28 capas
    },
    "gemma2": {
        "model_id":      "google/gemma-2-9b-it",
        "nombre":        "Gemma-2-9B-it",
        "capa_steering": 21,   # ~50% de 42 capas
    },
    "phi35": {
        "model_id":      "microsoft/Phi-3.5-mini-instruct",
        "nombre":        "Phi-3.5-mini-instruct",
        "capa_steering": 16,   # ~50% de 32 capas
    },
}

SYSTEM_INSTRUCTION = (
    "Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. "
    "Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla "
    "organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple "
    "la regla, o con el número 0 si la viola. No des explicaciones."
)


def cargar_modelo():
    """
    Carga el modelo definido en MODELO_ACTIVO con cuantización 4-bit NF4.
    No usa pipeline para evitar el error '.to() not supported for 4-bit models'.
    Retorna: (modelo, tokenizer, config_dict)
    """
    conf = CATALOGO_MODELOS[MODELO_ACTIVO]
    model_id = conf["model_id"]
    print(f"[*] Cargando {conf['nombre']} ({model_id})...")

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    try:
        from transformers import BitsAndBytesConfig
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )
        modelo = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quant_config,
            device_map="auto",
        )
        print("[+] Cuantización 4-bit NF4 activada — uso VRAM ~3-5 GB.")
    except ImportError:
        print("[!] bitsandbytes no instalado. Ejecuta: pip install bitsandbytes")
        print("[!] Cargando en float16 — puede requerir offload a RAM.")
        modelo = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=torch.float16,
            device_map="auto",
        )

    print(f"[+] {conf['nombre']} listo.")
    return modelo, tokenizer, conf


def generar_con_modelo(modelo, tokenizer, prompt_text):
    """
    Llama directamente a model.generate() evitando pipeline.
    Compatible con modelos cuantizados (bitsandbytes 4-bit/8-bit).
    Retorna el texto generado como string.
    """
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


def formatear_prompt(tokenizer, user_content, system_content=SYSTEM_INSTRUCTION):
    """
    Aplica el chat template del tokenizer para formatear el prompt correctamente
    según el modelo activo (Mistral, Qwen, Gemma, Phi, etc.).
    """
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user",   "content": user_content},
    ]
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        # Fallback para modelos que no aceptan rol "system" separado
        combined = f"{system_content}\n\n{user_content}"
        return tokenizer.apply_chat_template(
            [{"role": "user", "content": combined}],
            tokenize=False,
            add_generation_prompt=True,
        )
