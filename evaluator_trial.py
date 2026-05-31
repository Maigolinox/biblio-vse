# PRINCIPIOS DE RAG Y FEW-SHOT
import json
import time
import google.generativeai as genai
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# --- Importaciones para el modelo local ---
from model_loader import cargar_modelo, generar_con_modelo, formatear_prompt, CATALOGO_MODELOS, MODELO_ACTIVO

# ==========================================
# CONFIGURACIÓN DE ENTORNO
# ==========================================
# Cambia este valor a "API" o "LOCAL" según el modelo que quieras usar
MODO_EJECUCION = "LOCAL" 

# 1. Configuración de la IA (Ajusta tu API Key real aquí)
# Obtén tu API key en: https://aistudio.google.com/
genai.configure(api_key="AIzaSyCiZyEE19gFMkIxfGDohFSGV68Z2e47SxE")

# Usamos el modelo más capaz para seguir instrucciones estrictas
modelo = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple la regla, o con el número 0 si la viola. No des explicaciones."
)

# --- Configuración del modelo local ---
modelo_local = None
tokenizer_local = None
if MODO_EJECUCION == "LOCAL":
    _conf = CATALOGO_MODELOS[MODELO_ACTIVO]
    print(f"[*] Inicializando {_conf['nombre']} en local. Esto puede tardar...")
    try:
        modelo_local, tokenizer_local, _ = cargar_modelo()
        print("[+] Modelo local cargado exitosamente.")
    except Exception as e:
        print(f"[!] Error al cargar el modelo local: {e}")
        exit(1)


def evaluar_artefacto(meta_regla, tipo_artefacto, contenido_texto):
    """
    Ensambla el Prompt usando RAG y Few-Shot Prompting para calibrar la inferencia.
    """
    prompt_rag = f"""
    Eres un Auditor de Calidad de Software estricto pero justo, experto en ISO/IEC 29110.
    Tu tarea es clasificar el siguiente artefacto según la meta-regla proporcionada.

    CONTEXTO DE LA META-REGLA A EVALUAR: [{meta_regla}]
    Debes verificar si el artefacto demuestra cumplimiento explícito con esta política.

    --- EJEMPLOS DE CALIBRACIÓN (FEW-SHOT) ---
    A continuación, te presento ejemplos de cómo debes clasificar diferentes escenarios:

    EJEMPLO 1 (Regla: SEGURIDAD | Clase: 1 - Cumple)
    Artefacto: `DATABASES_PASSWORD = os.environ.get('DB_PASSWORD')`
    Razón de éxito: Las credenciales no están expuestas, se obtienen dinámicamente del entorno.

    EJEMPLO 2 (Regla: SEGURIDAD | Clase: 0 - Viola)
    Artefacto: `DATABASES_PASSWORD = 'super_secret_password'`
    Razón de fallo: Contraseña escrita en texto plano (hardcoded).

    EJEMPLO 3 (Regla: TRAZABILIDAD | Clase: 1 - Cumple)
    Artefacto: `def registrar_prestamo():\n    \"\"\"ID Requerimiento: RF_05\"\"\"`
    Razón de éxito: El código contiene referencias explícitas (docstrings) hacia los requerimientos de negocio.

    EJEMPLO 4 (Regla: DOCUMENTAL | Clase: 0 - Viola)
    Artefacto: `la arquitectura va a usar django y html normal. creo que base de datos postgres.`
    Razón de fallo: Lenguaje informal, carece de códigos de versión, fechas o estructura normativa.

    EJEMPLO 5 (Regla: INFRA | Clase: 1 - Cumple)
    Artefacto: `ALLOWED_HOSTS = ['catalogo.biblioteca.local']`
    Razón de éxito: El subdominio está estrictamente limitado a la red interna solicitada.
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
            respuesta = modelo.generate_content(prompt_rag)
            resultado = respuesta.text.strip()
            # Limpieza estricta
            if "1" in resultado:
                return 1
            elif "0" in resultado:
                return 0
            else:
                print(f"[!] Respuesta no binaria recibida de la API: {resultado}")
                return -1
        except Exception as e:
            print(f"[!] Error de API: {e}")
            return -1

    elif MODO_EJECUCION == "LOCAL":
        assert modelo_local is not None and tokenizer_local is not None
        prompt_local = formatear_prompt(tokenizer_local, prompt_rag)
        try:
            resultado = generar_con_modelo(modelo_local, tokenizer_local, prompt_local).strip()
            
            # Limpieza estricta
            if "1" in resultado:
                return 1
            elif "0" in resultado:
                return 0
            else:
                print(f"[!] Respuesta no binaria recibida del modelo local: {resultado}")
                return -1
        except Exception as e:
            print(f"[!] Error del Modelo Local: {e}")
            return -1


def ejecutar_auditoria():
    print(f"Iniciando Auditoría LLM sobre Dataset Isomórfico (MODO: {MODO_EJECUCION})...")
    
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
        
        # Pausa para evitar límites de la API (Rate Limits) solo si es necesario
        if MODO_EJECUCION == "API":
            time.sleep(2)

        if prediccion != -1:
            y_verdadero.append(etiqueta_real)
            y_prediccion.append(prediccion)
            print(f" -> Predicción LLM: {prediccion}")

    # Calcular resultados y formalismo matemático
    print("\n" + "="*50)
    print("RESULTADOS DEL EXPERIMENTO (Para el Artículo JCR)")
    print("="*50)
    
    matriz = confusion_matrix(y_verdadero, y_prediccion)
    print("\nMatriz de Confusión [TN, FP], [FN, TP]:\n", matriz)
    
    reporte = classification_report(y_verdadero, y_prediccion, target_names=["Viola (0)", "Cumple (1)"])
    print("\nMétricas Detalladas:\n", reporte)
    
    f1 = f1_score(y_verdadero, y_prediccion)
    print(f"\nF1-Score Global (El número clave para tu abstract): {f1:.4f}")

if __name__ == '__main__':
    ejecutar_auditoria()

"""
models/gemini-2.5-flash
models/gemini-2.5-pro
models/gemini-2.0-flash
models/gemini-2.0-flash-001
models/gemini-2.0-flash-lite-001
models/gemini-2.0-flash-lite
models/gemini-2.5-flash-preview-tts
models/gemini-2.5-pro-preview-tts
models/gemma-3-1b-it
models/gemma-3-4b-it
models/gemma-3-12b-it
models/gemma-3-27b-it
models/gemma-3n-e4b-it
models/gemma-3n-e2b-it
models/gemini-flash-latest
models/gemini-flash-lite-latest
models/gemini-pro-latest
models/gemini-2.5-flash-lite
models/gemini-2.5-flash-image
models/gemini-2.5-flash-lite-preview-09-2025
models/gemini-3-pro-preview
models/gemini-3-flash-preview
models/gemini-3.1-pro-preview
models/gemini-3.1-pro-preview-customtools
models/gemini-3.1-flash-lite-preview
models/gemini-3-pro-image-preview
models/nano-banana-pro-preview
models/gemini-3.1-flash-image-preview
models/gemini-robotics-er-1.5-preview
models/gemini-2.5-computer-use-preview-10-2025
models/deep-research-pro-preview-12-2025
"""