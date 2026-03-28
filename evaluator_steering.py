# import os
# import json
# import torch
# import gc
# from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
# from sklearn.metrics import classification_report, confusion_matrix, f1_score

# # ================= CONFIGURACIÓN =================
# MODELO_ID = "mistralai/Mistral-7B-Instruct-v0.2"
# CAPA_OBJETIVO = 15     # Capa media de Mistral (de 32 capas)
# ALPHA = 1.5            # Fuerza de la modificación
# # =================================================

# print("==================================================")
# print(f" Cargando {MODELO_ID} en 4-bits (Optimizando VRAM)...")
# print("==================================================")

# # Configuración estricta para GPUs con poca VRAM
# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_compute_dtype=torch.float16,
#     bnb_4bit_use_double_quant=True,
# )

# tokenizer = AutoTokenizer.from_pretrained(MODELO_ID)
# if tokenizer.pad_token is None:
#     tokenizer.pad_token = tokenizer.eos_token

# model = AutoModelForCausalLM.from_pretrained(
#     MODELO_ID,
#     quantization_config=bnb_config,
#     device_map="auto",
# )

# def limpiar_vram():
#     gc.collect()
#     torch.cuda.empty_cache()

# # ================= DICCIONARIO RAG =================
# # En lugar de una base vectorial pesada, simulamos la recuperación (Retrieval)
# # mapeando exactamente la regla que necesita el artefacto.
# DICCIONARIO_REGLAS = {
#     "DOCUMENTAL": "Todo documento debe tener un código único, versión y fecha de vigencia.",
#     "CALIDAD": "El código debe pasar revisión por pares, usar convenciones correctas y no tener dependencias sin usar.",
#     "GOBERNANZA": "El desarrollo debe estar justificado por un requerimiento previamente aprobado y firmado.",
#     "SEGURIDAD": "Las credenciales o contraseñas NUNCA deben estar en texto plano; deben usarse variables de entorno.",
#     "TRAZABILIDAD": "El código debe contener referencias (ej. docstrings) a los IDs de los requerimientos de negocio.",
#     "PRUEBAS": "Los tests deben tener pasos reproducibles, entorno documentado y aserciones lógicas.",
#     "RESPALDO": "Los pipelines de CI/CD deben incluir rutinas explícitas de respaldo de base de datos o código.",
#     "ACUERDOS": "Las actas de reunión deben listar acuerdos claros, con responsables asignados y estado de seguimiento.",
#     "INFRA": "La configuración de red debe restringir el acceso exclusivamente a subdominios internos autorizados."
# }

# # ================= FASE 1: LECTURA DEL CONCEPTO =================
# def obtener_estado_oculto(texto, layer_idx):
#     # Formato estricto para Mistral Instruct
#     prompt = f"[INST] Analiza este fragmento:\n{texto} [/INST]"
#     inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
#     with torch.no_grad():
#         outputs = model(**inputs, output_hidden_states=True)
    
#     # Extraemos el tensor de la capa 15 del último token
#     h_l = outputs.hidden_states[layer_idx][0, -1, :]
    
#     del inputs, outputs
#     limpiar_vram()
#     return h_l

# def calcular_vector_conceptual(dataset):
#     print(f"\n[1/3] Extrayendo vector conceptual desde la capa {CAPA_OBJETIVO}...")
#     pos_states = []
#     neg_states = []

#     for muestra in dataset:
#         h_l = obtener_estado_oculto(muestra['contenido_texto'], CAPA_OBJETIVO)
#         if muestra['etiqueta_clase'] == 1:
#             pos_states.append(h_l)
#         else:
#             neg_states.append(h_l)

#     mean_pos = torch.stack(pos_states).mean(dim=0)
#     mean_neg = torch.stack(neg_states).mean(dim=0)
    
#     v_norma = mean_pos - mean_neg
#     print(f" -> Vector 'Cumplimiento Normativo' generado. Dimensión: {v_norma.shape}")
#     return v_norma

# # ================= FASE 2: INYECCIÓN Y AUDITORÍA =================
# def evaluar_con_steering_y_rag(dataset, v_norma):
#     print(f"\n[2/3] Iniciando Auditoría (RAG + Steering) con Alpha = {ALPHA}...")
    
#     y_verdadero = []
#     y_prediccion = []

#     def steering_hook(module, args, kwargs, output):
#         # Hugging Face puede devolver una tupla o un tensor dependiendo del paso de generación
#         if isinstance(output, tuple):
#             h_l = output[0] 
#             h_l_modificado = h_l + (ALPHA * v_norma.to(h_l.device))
#             return (h_l_modificado,) + output[1:] # Reconstruimos la tupla
#         else:
#             h_l = output
#             h_l_modificado = h_l + (ALPHA * v_norma.to(h_l.device))
#             return h_l_modificado # Devolvemos solo el tensor

#     capa_intervenida = model.model.layers[CAPA_OBJETIVO]
#     handle = capa_intervenida.register_forward_hook(steering_hook, with_kwargs=True)

#     for muestra in dataset:
#         regla_id = muestra['meta_regla']
#         contexto_rag = DICCIONARIO_REGLAS.get(regla_id, "Debe cumplir estándares corporativos.")
        
#         prompt = f"""[INST] Eres un Auditor ISO/IEC 29110. Evalúa el siguiente artefacto.

# CONTEXTO NORMATIVO (Regla {regla_id}):
# {contexto_rag}

# ARTEFACTO:
# {muestra['contenido_texto']}
# ¿Cumple este artefacto la normativa? Responde SOLO con el número 1 (Sí cumple) o el número 0 (Viola la norma). [/INST]"""
        
#         inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
#         with torch.no_grad():
#             outputs = model.generate(
#                 **inputs, 
#                 max_new_tokens=5, 
#                 do_sample=False, # Corrección: Inferencia 100% determinista (Greedy Decoding)
#                 pad_token_id=tokenizer.eos_token_id
#             )
            
#         respuesta_cruda = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
        
#         # Limpieza robusta del output
#         prediccion = 1 if "1" in respuesta_cruda else 0
#         y_verdadero.append(muestra['etiqueta_clase'])
#         y_prediccion.append(prediccion)
        
#         print(f" [{muestra['id_muestra']}] Esperado: {muestra['etiqueta_clase']} | Mistral Steered: {prediccion}")
        
#         del inputs, outputs
#         limpiar_vram()

#     handle.remove() # Restaurar el modelo a su estado natural
#     return y_verdadero, y_prediccion

# def ejecutar_auditoria():
#     with open('dataset_isomorfico.json', 'r', encoding='utf-8') as f:
#         dataset = json.load(f)

#     # 1. Leer el concepto
#     v_norma = calcular_vector_conceptual(dataset)
    
#     # 2. Auditar con el cerebro modificado y contexto recuperado (RAG simulado)
#     y_real, y_pred = evaluar_con_steering_y_rag(dataset, v_norma)

#     # 3. Métricas para el Paper
#     print("\n[3/3] " + "="*50)
#     print("RESULTADOS DEL EXPERIMENTO 4 (MISTRAL-7B + RAG + STEERING)")
#     print("="*50)
#     print("\nMatriz de Confusión:\n", confusion_matrix(y_real, y_pred))
#     print("\nMétricas Detalladas:\n", classification_report(y_real, y_pred, target_names=["Viola (0)", "Cumple (1)"], zero_division=0))
#     print(f"\nF1-Score Global: {f1_score(y_real, y_pred):.4f}")

# if __name__ == '__main__':
#     ejecutar_auditoria()


import os
import json
import torch
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# ================= LIBRERÍAS RAG =================
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore

# ================= CONFIGURACIÓN =================
MODELO_ID = "mistralai/Mistral-7B-Instruct-v0.2"
CAPA_OBJETIVO = 15     # Capa media de Mistral
ALPHA = 0.3            # Fuerza de la modificación (ajustado a 0.3 para evitar colapso tensorial)
RUTA_ESTANDARES = "./documentos_estandar" # Tu carpeta con la ISO/IEC 29110
# =================================================

# ================= 1. CARGA DE DOCUMENTOS MIXTOS (De tu código funcional) =================
def cargar_documentos_mixtos(ruta_directorio):
    """Carga recursivamente PDFs, DOCXs, TXTs y MDs de un directorio."""
    if not os.path.exists(ruta_directorio):
        os.makedirs(ruta_directorio)
        print(f" [!] Se creó la carpeta '{ruta_directorio}'. Coloca tus normas ISO ahí.")
        return []

    documentos = []
    loaders = [
        DirectoryLoader(ruta_directorio, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(ruta_directorio, glob="**/*.docx", loader_cls=Docx2txtLoader),
        DirectoryLoader(ruta_directorio, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(ruta_directorio, glob="**/*.md", loader_cls=TextLoader),
    ]
    print(f" Escaneando directorio de estándares en: {ruta_directorio} ...")
    for loader in loaders:
        try:
            docs = loader.load()
            documentos.extend(docs)
            if docs:
                print(f"   - Encontrados {len(docs)} fragmentos con {loader.loader_cls.__name__}")
        except Exception as e:
            print(f"   [!] Error cargando: {e}")
    return documentos

def configurar_rag():
    print("==================================================")
    print(" Configurando Base de Conocimiento RAG (ISO/IEC 29110)")
    print("==================================================")
    
    docs_estandar = cargar_documentos_mixtos(RUTA_ESTANDARES)
    
    if not docs_estandar:
        print(" [!] No se encontraron documentos. El contexto estará vacío.")
        return None

    print(f" -> {len(docs_estandar)} páginas/documentos cargados de los estándares.")
    # Ajustado al chunk size de tu código anterior (800) para mayor contexto normativo
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    splits = text_splitter.split_documents(docs_estandar)
    print(f" -> Total fragmentos vectorizados: {len(splits)}")

    # Embeddings en CPU para salvar VRAM
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'} 
    )
    
    vectorstore = SKLearnVectorStore.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    print(" -> Base vectorial lista y cargada en memoria RAM.")
    return retriever

# ================= 2. CARGA DEL MODELO (EN GPU) =================
print(f"\n Cargando {MODELO_ID} en 4-bits (GPU VRAM)...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODELO_ID)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODELO_ID,
    quantization_config=bnb_config,
    device_map="auto",
)

def limpiar_vram():
    gc.collect()
    torch.cuda.empty_cache()

# ================= 3. EXTRACCIÓN DEL CONCEPTO =================
def obtener_estado_oculto(texto, layer_idx):
    prompt = f"[INST] Analiza este fragmento:\n{texto} [/INST]"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    
    h_l = outputs.hidden_states[layer_idx][0, -1, :]
    del inputs, outputs
    limpiar_vram()
    return h_l

def calcular_vector_conceptual(dataset):
    print(f"\n[1/3] Extrayendo vector conceptual desde la capa {CAPA_OBJETIVO}...")
    pos_states = []
    neg_states = []

    for muestra in dataset:
        h_l = obtener_estado_oculto(muestra['contenido_texto'], CAPA_OBJETIVO)
        if muestra['etiqueta_clase'] == 1:
            pos_states.append(h_l)
        else:
            neg_states.append(h_l)

    mean_pos = torch.stack(pos_states).mean(dim=0)
    mean_neg = torch.stack(neg_states).mean(dim=0)
    
    v_norma = mean_pos - mean_neg
    print(f" -> Vector 'Cumplimiento Normativo' generado. Dimensión: {v_norma.shape}")
    return v_norma

# ================= 4. INYECCIÓN Y AUDITORÍA AL REPOSITORIO =================
def evaluar_con_steering_y_rag(dataset, v_norma, retriever):
    print(f"\n[2/3] Iniciando Auditoría RAG-Steering combinada (Alpha = {ALPHA})...")
    
    y_verdadero = []
    y_prediccion = []

    def steering_hook(module, args, kwargs, output):
        if isinstance(output, tuple):
            h_l = output[0] 
            h_l_modificado = h_l + (ALPHA * v_norma.to(h_l.device))
            return (h_l_modificado,) + output[1:] 
        else:
            h_l = output
            h_l_modificado = h_l + (ALPHA * v_norma.to(h_l.device))
            return h_l_modificado

    capa_intervenida = model.model.layers[CAPA_OBJETIVO]
    handle = capa_intervenida.register_forward_hook(steering_hook, with_kwargs=True)

    for muestra in dataset:
        regla_id = muestra['meta_regla']
        
        # 1. Recuperación con filtro estricto
        contexto_rag = ""
        if retriever:
            # Forzamos la búsqueda de la regla específica
            query = f"Regla, normativa o política para {regla_id}"
            docs_recuperados = retriever.invoke(query)
            if docs_recuperados:
                contexto_rag = docs_recuperados[0].page_content
        
        # 2. Prompt optimizado para Mistral Instruct con Assistant Prefilling y Few-Shot
        prompt = f"""[INST] Actúa como un riguroso Auditor de Software. 
Evalúa el ARTEFACTO basándote ÚNICAMENTE en la NORMA recuperada.

NORMA A CUMPLIR ({regla_id}):
{contexto_rag}

--- EJEMPLO DE CÓMO DEBES RESPONDER ---
¿El artefacto cumple con la norma?
1
---------------------------------------

ARTEFACTO A EVALUAR:
{muestra['contenido_texto']}


¿El artefacto cumple con la norma? Responde ESTRICTAMENTE con un solo dígito: 1 (si cumple) o 0 (si viola la norma). NO escribas texto, introducciones ni explicaciones. [/INST]
"""
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # 3. Inferencia
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=5, 
                do_sample=False, 
                pad_token_id=tokenizer.eos_token_id
            )
            
        respuesta_cruda = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
        
        # Extracción segura del primer número encontrado
        import re
        numeros = re.findall(r'[01]', respuesta_cruda)
        prediccion = int(numeros[0]) if numeros else 0
        
        y_verdadero.append(muestra['etiqueta_clase'])
        y_prediccion.append(prediccion)
        
        print(f"\n[{muestra['id_muestra']}] Esperado: {muestra['etiqueta_clase']} | IA: {prediccion}")
        print(f" ↳ Respuesta cruda: '{respuesta_cruda}'")
        
        del inputs, outputs
        limpiar_vram()

    handle.remove() 
    return y_verdadero, y_prediccion

def ejecutar_experimento_4():
    # Inicializa el RAG leyendo los PDFs/DOCX
    retriever = configurar_rag()
    
    # Carga el repositorio de prueba
    with open('dataset_isomorfico.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Ejecuta el experimento matemático
    v_norma = calcular_vector_conceptual(dataset)
    y_real, y_pred = evaluar_con_steering_y_rag(dataset, v_norma, retriever)

    print("\n[3/3] " + "="*50)
    print("RESULTADOS EXPERIMENTO 4: RAG (ISO 29110) + ACTIVATION STEERING")
    print("="*50)
    print("\nMatriz de Confusión:\n", confusion_matrix(y_real, y_pred))
    print("\nMétricas Detalladas:\n", classification_report(y_real, y_pred, target_names=["Viola (0)", "Cumple (1)"], zero_division=0))
    print(f"\nF1-Score Global: {f1_score(y_real, y_pred):.4f}")

if __name__ == '__main__':
    ejecutar_experimento_4()
