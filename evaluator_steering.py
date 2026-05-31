



# RAG, FEW-SHOT Y ACTIVATION STEERING
import json
import time
import google.generativeai as genai
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# --- Importaciones para el modelo local y Steering ---
import torch
from model_loader import cargar_modelo, generar_con_modelo, formatear_prompt, CATALOGO_MODELOS, MODELO_ACTIVO

# ==========================================
# CONFIGURACIÓN DE ENTORNO Y STEERING
# ==========================================
MODO_EJECUCION = "LOCAL" # Cambia a "API" o "LOCAL"

# Parámetros del Activation Steering (Solo aplicable en MODO LOCAL)
USAR_STEERING = True
CAPA_STEERING = None    # Se asigna automáticamente desde el catálogo al cargar el modelo
ALPHA_STEERING = 0.8    # Multiplicador de fuerza (α). Valores típicos: 0.5 a 3.0

# 1. Configuración de la IA (Ajusta tu API Key real aquí)
genai.configure(api_key="AIzaSyCiZyEE19gFMkIxfGDohFSGV68Z2e47SxE")
modelo_gemini = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple la regla, o con el número 0 si la viola. No des explicaciones."
)

# --- Configuración del modelo local ---
modelo_local = None
tokenizer_local = None
vector_direccion = None
hook_handle = None

# ==========================================
# FUNCIONES DE ACTIVATION STEERING
# ==========================================

def calcular_vector_steering(modelo, tokenizer, capa):
    """Calcula el vector de dirección conceptual (Auditor Estricto vs Relajado)"""
    print("[*] Calculando vector conceptual de Steering...")
    
    # Prompts antagónicos para extraer la representación latente
    sistema_neutral = "Eres un asistente de evaluación de calidad de software."
    prompt_pos = formatear_prompt(
        tokenizer,
        "Actúa como un auditor de calidad extremadamente estricto, implacable y apegado milimétricamente a la norma.",
        system_content=sistema_neutral,
    )
    prompt_neg = formatear_prompt(
        tokenizer,
        "Actúa como un auditor relajado, descuidado y permisivo. No te importan las normas ni la seguridad.",
        system_content=sistema_neutral,
    )

    inputs_pos = tokenizer(prompt_pos, return_tensors="pt").to(modelo.device)
    inputs_neg = tokenizer(prompt_neg, return_tensors="pt").to(modelo.device)
    
    with torch.no_grad():
        out_pos = modelo(**inputs_pos, output_hidden_states=True)
        out_neg = modelo(**inputs_neg, output_hidden_states=True)
        
    # Extraemos el estado oculto de la capa deseada. 
    # output_hidden_states es una tupla, tomamos el índice 'capa'.
    # Shape: (batch_size=1, seq_len, hidden_size). Tomamos el último token [-1] que encapsula el contexto.
    h_pos = out_pos.hidden_states[capa][:, -1, :] 
    h_neg = out_neg.hidden_states[capa][:, -1, :] 
    
    # Vector delta (Estricto - Relajado)
    vector = h_pos - h_neg 
    
    # Redimensionamos para que se pueda sumar correctamente durante la generación (1, 1, hidden_size)
    print("[+] Vector conceptual calculado.")
    return vector.unsqueeze(1)

def steering_hook(module, input_args, output):
    """Función Hook que intercepta e inyecta el vector en el forward pass.
    Soporta dos formatos de salida de capa:
    - Tensor directo (transformers 5.x: Qwen2, Gemma2, Phi3.5)
    - Tupla (transformers 4.x: Mistral/LLaMA legacy)
    """
    assert vector_direccion is not None
    if isinstance(output, torch.Tensor):
        return output + (ALPHA_STEERING * vector_direccion.to(output.device))
    # Formato tupla: (hidden_states, *resto)
    hidden_states = output[0]
    hidden_steered = hidden_states + (ALPHA_STEERING * vector_direccion.to(hidden_states.device))
    return (hidden_steered,) + output[1:]

# ==========================================
# INICIALIZACIÓN LOCAL Y APLICACIÓN DE HOOK
# ==========================================

if MODO_EJECUCION == "LOCAL":
    _conf = CATALOGO_MODELOS[MODELO_ACTIVO]
    print(f"[*] Inicializando {_conf['nombre']} en local. Esto puede tardar...")
    try:
        modelo_local, tokenizer_local, _conf = cargar_modelo()
        CAPA_STEERING = _conf["capa_steering"]

        if USAR_STEERING:
            vector_direccion = calcular_vector_steering(modelo_local, tokenizer_local, CAPA_STEERING)
            capa_objetivo = modelo_local.model.layers[CAPA_STEERING]
            hook_handle = capa_objetivo.register_forward_hook(steering_hook)
            print(f"[+] Activation Steering inyectado en Capa {CAPA_STEERING} con Fuerza {ALPHA_STEERING}.")

        print("[+] Modelo local cargado exitosamente.")
    except Exception as e:
        print(f"[!] Error al cargar el modelo local: {e}")
        exit(1)

# ==========================================
# FUNCIÓN DE EVALUACIÓN
# ==========================================

def evaluar_artefacto(meta_regla, tipo_artefacto, contenido_texto):
    """
    Ensambla el Prompt usando RAG y Few-Shot.
    Si estamos en LOCAL y USAR_STEERING es True, el modelo ya está modificado a nivel neuronal.
    """
    prompt_rag = f"""
    Eres un Auditor de Calidad de Software estricto pero justo, experto en ISO/IEC 29110.
    Tu tarea es clasificar el siguiente artefacto según la meta-regla proporcionada.

    CONTEXTO DE LA META-REGLA A EVALUAR: [{meta_regla}]
    Debes verificar si el artefacto demuestra cumplimiento explícito con esta política.

    --- EJEMPLOS DE CALIBRACIÓN (FEW-SHOT) ---
    EJEMPLO 1 (Regla: SEGURIDAD | Clase: 1 - Cumple)
    Artefacto: `DATABASES_PASSWORD = os.environ.get('DB_PASSWORD')`
    Razón de éxito: Las credenciales no están expuestas, se obtienen dinámicamente.

    EJEMPLO 2 (Regla: SEGURIDAD | Clase: 0 - Viola)
    Artefacto: `DATABASES_PASSWORD = 'super_secret_password'`
    Razón de fallo: Contraseña escrita en texto plano (hardcoded).

    EJEMPLO 3 (Regla: TRAZABILIDAD | Clase: 1 - Cumple)
    Artefacto: `def registrar_prestamo():\n    \"\"\"ID Requerimiento: RF_05\"\"\"`
    Razón de éxito: Referencias explícitas (docstrings) hacia los requerimientos de negocio.

    EJEMPLO 4 (Regla: DOCUMENTAL | Clase: 0 - Viola)
    Artefacto: `la arquitectura va a usar django y html normal. creo que base de datos postgres.`
    Razón de fallo: Lenguaje informal, carece de estructura normativa.
    ------------------------------------------

    ARTEFACTO A AUDITAR (Tipo: {tipo_artefacto}):
    ```
    {contenido_texto}
    ```

    ¿Cumple este artefacto con los estándares corporativos para la meta-regla {meta_regla}?
    Responde ÚNICAMENTE con el número 1 (si cumple) o el número 0 (si viola). No añadas ninguna explicación ni texto adicional.
    """
    
    if MODO_EJECUCION == "API":
        try:
            respuesta = modelo_gemini.generate_content(prompt_rag)
            resultado = respuesta.text.strip()
            if "1" in resultado: return 1
            elif "0" in resultado: return 0
            else: return -1
        except Exception as e:
            print(f"[!] Error de API: {e}")
            return -1

    elif MODO_EJECUCION == "LOCAL":
        assert modelo_local is not None and tokenizer_local is not None
        prompt_local = formatear_prompt(tokenizer_local, prompt_rag)
        try:
            resultado = generar_con_modelo(modelo_local, tokenizer_local, prompt_local).strip()
            if "1" in resultado: return 1
            elif "0" in resultado: return 0
            else: return -1
        except Exception as e:
            print(f"[!] Error del Modelo Local: {e}")
            return -1

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================

def ejecutar_auditoria():
    metodologia = "RAG + FEW-SHOT"
    if MODO_EJECUCION == "LOCAL" and USAR_STEERING:
        metodologia += f" + STEERING (α={ALPHA_STEERING})"
        
    print(f"Iniciando Auditoría LLM (MODO: {MODO_EJECUCION} | METODOLOGÍA: {metodologia})...")
    
    with open('dataset_isomorfico.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    y_verdadero = []
    y_prediccion = []

    for muestra in dataset:
        id_muestra = muestra['id_muestra']
        etiqueta_real = muestra['etiqueta_clase']
        print(f"Evaluando {id_muestra} (Esperado: {etiqueta_real})...")
        
        prediccion = evaluar_artefacto(
            muestra['meta_regla'], 
            muestra['tipo_artefacto'], 
            muestra['contenido_texto']
        )
        
        if MODO_EJECUCION == "API": time.sleep(2)

        if prediccion != -1:
            y_verdadero.append(etiqueta_real)
            y_prediccion.append(prediccion)
            print(f" -> Predicción LLM: {prediccion}")
        else:
            # Si el modelo alucina o falla, lo contamos como Viola (0)
            print(" -> [!] Falla de inferencia: Contabilizado como 0")
            y_verdadero.append(etiqueta_real)
            y_prediccion.append(0)

    print("\n" + "="*50)
    print(f"RESULTADOS DEL EXPERIMENTO: {metodologia}")
    print("="*50)
    
    matriz = confusion_matrix(y_verdadero, y_prediccion)
    print("\nMatriz de Confusión [TN, FP], [FN, TP]:\n", matriz)
    
    reporte = classification_report(y_verdadero, y_prediccion, target_names=["Viola (0)", "Cumple (1)"])
    print("\nMétricas Detalladas:\n", reporte)
    
    f1 = f1_score(y_verdadero, y_prediccion)
    print(f"\nF1-Score Global (El número clave para tu abstract): {f1:.4f}")
    
    # Limpieza: Si usamos un hook, debemos quitarlo al terminar para no dañar el modelo en RAM
    if hook_handle is not None:
        hook_handle.remove()

if __name__ == '__main__':
    ejecutar_auditoria()
