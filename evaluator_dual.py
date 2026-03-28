#FEW SHOT
import json
import time
import google.generativeai as genai
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# 1. Configuración de la IA (Ajusta tu API Key real aquí)
# Obtén tu API key en: https://aistudio.google.com/
genai.configure(api_key="AIzaSyBm1KV-r1ogQuZDA5JG0O7tlh7TRvh14Gs")

# Usamos el modelo más capaz para seguir instrucciones estrictas
modelo = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="Eres un Auditor de Calidad de Software experto en el estándar ISO/IEC 29110. Tu única tarea es evaluar artefactos y determinar si cumplen con una meta-regla organizacional. Debes responder ÚNICAMENTE con el número 1 si el artefacto cumple la regla, o con el número 0 si la viola. No des explicaciones."
)

def evaluar_artefacto(meta_regla, tipo_artefacto, contenido_texto):
    """
    Ensambla el Prompt usando principios de RAG (inyectando la regla exacta)
    """
    prompt_rag = f"""
    Eres un Auditor ISO/IEC 29110.

    Contexto de la Meta-Regla a evaluar ({meta_regla}):
    El artefacto debe demostrar cumplimiento estricto.

    --- EJEMPLOS DE CALIBRACIÓN ---
    Ejemplo Positivo (1): Si la regla es de SEGURIDAD y el código usa 'os.environ.get()', eso CUMPLE (1).
    Ejemplo Negativo (0): Si la regla es de CALIDAD y el código tiene mala indentación o imports no usados, eso VIOLA (0).
    -------------------------------

    Artefacto a auditar (Tipo: {tipo_artefacto}):
    ```
    {contenido_texto}
    ```

    ¿Cumple este artefacto con los estándares exigidos para la meta-regla {meta_regla}?
    Responde solo 1 (Cumple) o 0 (Viola).
    """
    try:
        respuesta = modelo.generate_content(prompt_rag)
        resultado = respuesta.text.strip()
        # Limpieza por si la IA añade un salto de línea
        if "1" in resultado:
            return 1
        elif "0" in resultado:
            return 0
        else:
            print(f"[!] Respuesta no binaria recibida: {resultado}")
            return -1 # Error de inferencia
    except Exception as e:
        print(f"[!] Error de API: {e}")
        return -1

def ejecutar_auditoria():
    print("Iniciando Auditoría LLM sobre Dataset Isomórfico...")
    
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
        
        # Pausa para evitar límites de la API (Rate Limits)
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