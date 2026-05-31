# BASE LINE: ZERO-SHOT
import json
import time
import google.generativeai as genai
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# --- Importaciones para el modelo local ---
from model_loader import cargar_modelo, generar_con_modelo, formatear_prompt, CATALOGO_MODELOS, MODELO_ACTIVO

# ==========================================
# CONFIGURACIÓN DE ENTORNO
# ==========================================
MODO_EJECUCION = "LOCAL" # Cambia este valor a "API" o "LOCAL"

# ==========================================
# 1. INICIALIZACIÓN DE MODELOS
# ==========================================

# A. Configuración de Gemini (API)
genai.configure(api_key="AIzaSyCiZyEE19gFMkIxfGDohFSGV68Z2e47SxE")
modelo_gemini = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple la regla, o con el número 0 si la viola. No des explicaciones."
)

# B. Configuración del modelo local
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


# ==========================================
# 2. FUNCIÓN DE EVALUACIÓN
# ==========================================

def evaluar_artefacto(meta_regla, tipo_artefacto, contenido_texto):
    """
    Evaluación Zero-Shot: Solo se inyecta la regla y el artefacto. Cero ejemplos.
    """
    
    prompt_base = f"""
    Contexto de la Meta-Regla a evaluar ({meta_regla}):
    El artefacto debe demostrar cumplimiento estricto con las políticas corporativas.

    Artefacto a auditar (Tipo: {tipo_artefacto}):
    ```
    {contenido_texto}
    ```

    ¿Cumple este artefacto con los estándares exigidos para la meta-regla {meta_regla}?
    Responde solo 1 (Cumple) o 0 (Viola).
    """
    
    if MODO_EJECUCION == "API":
        try:
            respuesta = modelo_gemini.generate_content(prompt_base)
            resultado = respuesta.text.strip()
            if "1" in resultado: return 1
            elif "0" in resultado: return 0
            else: return -1
        except Exception as e:
            print(f"[!] Error de API Gemini: {e}")
            return -1

    elif MODO_EJECUCION == "LOCAL":
        assert modelo_local is not None and tokenizer_local is not None
        prompt_local = formatear_prompt(tokenizer_local, prompt_base)
        try:
            resultado = generar_con_modelo(modelo_local, tokenizer_local, prompt_local).strip()
            
            if "1" in resultado: return 1
            elif "0" in resultado: return 0
            else:
                print(f"[!] Respuesta no binaria recibida del modelo local: {resultado}")
                return -1
        except Exception as e:
            print(f"[!] Error del Modelo Local: {e}")
            return -1

# ==========================================
# 3. EJECUCIÓN PRINCIPAL
# ==========================================

def ejecutar_auditoria():
    print(f"Iniciando Auditoría LLM sobre Dataset Isomórfico (MODO: {MODO_EJECUCION} | METODOLOGÍA: ZERO-SHOT)...")
    
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
        
        if MODO_EJECUCION == "API":
            time.sleep(2)

        # Manejo de respuestas y control estricto de las 20 muestras
        y_verdadero.append(etiqueta_real)
        if prediccion != -1:
            y_prediccion.append(prediccion)
            print(f" -> Predicción LLM: {prediccion}")
        else:
            # Castigo: Si el modelo falla en dar una respuesta binaria, lo marcamos como violación (0)
            print(" -> [!] Falla de inferencia. Contabilizado como 0 (Viola)")
            y_prediccion.append(0)

    # Calcular resultados
    print("\n" + "="*50)
    print("RESULTADOS DEL EXPERIMENTO: ZERO-SHOT (Base Line)")
    print("="*50)
    
    matriz = confusion_matrix(y_verdadero, y_prediccion)
    print("\nMatriz de Confusión [TN, FP], [FN, TP]:\n", matriz)
    
    reporte = classification_report(y_verdadero, y_prediccion, target_names=["Viola (0)", "Cumple (1)"])
    print("\nMétricas Detalladas:\n", reporte)
    
    f1 = f1_score(y_verdadero, y_prediccion)
    print(f"\nF1-Score Global (Baseline F1-Score): {f1:.4f}")

if __name__ == '__main__':
    ejecutar_auditoria()