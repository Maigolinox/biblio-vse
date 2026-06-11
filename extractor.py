import os
import json
from git import Repo
from radon.complexity import cc_visit

def calcular_complejidad_ast(codigo_fuente):
    """
    Calcula la complejidad ciclomática promedio de un script de Python 
    analizando su Árbol de Sintaxis Abstracta (AST).
    """
    try:
        bloques = cc_visit(codigo_fuente)
        if not bloques:
            return 1 # Complejidad base
        # Promedio de la complejidad de todas las funciones/clases en el archivo
        return sum([b.complexity for b in bloques]) / len(bloques)
    except SyntaxError:
        # Si el ejemplo negativo tiene errores de sintaxis intencionales
        return 0 

# Directories / files that contain ISO/IEC 29110 artifacts in the Biblio-VSE Django project.
# All other paths (experiment scripts, article, evaluators, IDE config) are excluded.
ARTIFACT_DIRS = (
    'catalogo/', 'prestamos/', 'scripts/', 'docs/', 'config/',
    '.gitlab/', 'appserver/',
)
ARTIFACT_FILES = frozenset({'.gitlab-ci.yml'})


def es_artefacto(ruta: str) -> bool:
    """Returns True only for files inside the Django application and documentation tree."""
    if ruta in ARTIFACT_FILES:
        return True
    return any(ruta.startswith(prefix) for prefix in ARTIFACT_DIRS)


def construir_dataset():
    ruta_repo = '.'
    repo = Repo(ruta_repo)
    dataset = []

    print("Iniciando escaneo del repositorio Biblio-VSE...\n")

    # Iterar sobre todas las ramas inyectadas
    for rama in repo.branches:
        if not rama.name.startswith('feat/'):
            continue

        # Analizar metadatos de la rama
        es_cumplimiento = 'positiva' in rama.name
        etiqueta = 1 if es_cumplimiento else 0
        regla = rama.name.split('-')[1].upper() # Extrae R1, R2, etc.

        # Diff the branch tip against master: captures ALL changes introduced
        # by the branch regardless of how many intermediate commits exist.
        # The es_artefacto() filter below then discards non-artifact files.
        master_commit = repo.commit('master')
        branch_commit = rama.commit
        diferencias = master_commit.diff(branch_commit)

        for diff in diferencias:
            # Solo analizamos archivos agregados (A) o modificados (M)
            if diff.change_type not in ['A', 'M']:
                continue

            ruta_archivo = diff.b_path

            # Skip files outside the Django application / docs tree
            if not es_artefacto(ruta_archivo):
                continue

            blob = diff.b_blob

            if blob is None:
                continue
                
            contenido = blob.data_stream.read().decode('utf-8', errors='ignore')
            
            # Inicializar métricas base
            metricas = {
                "lineas_totales": len(contenido.splitlines()),
                "longitud_caracteres": len(contenido)
            }
            
            # Tipado y métricas específicas por artefacto
            if ruta_archivo.endswith('.py'):
                tipo_artefacto = "codigo_fuente"
                metricas["complejidad_ciclomatica_VG"] = round(calcular_complejidad_ast(contenido), 2)
            elif ruta_archivo.endswith('.md') or ruta_archivo.endswith('.txt'):
                tipo_artefacto = "documento_texto"
                metricas["conteo_palabras"] = len(contenido.split())
            elif ruta_archivo.endswith('.yml') or ruta_archivo.endswith('.yaml'):
                tipo_artefacto = "pipeline_ci"
            else:
                tipo_artefacto = "otro"

            # Construir la muestra
            muestra = {
                "id_muestra": f"SMP-{regla}-{'POS' if etiqueta else 'NEG'}",
                "meta_regla": regla,
                "tipo_artefacto": tipo_artefacto,
                "archivo": ruta_archivo,
                "contenido_texto": contenido,
                "etiqueta_clase": etiqueta,
                "metricas_isomorfismo": metricas
            }
            dataset.append(muestra)

    # Exportar el Dataset Sintético Isomórfico
    with open('dataset_isomorfico.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)

    # Validar e imprimir el resumen tabular
    print(f"{'ID MUESTRA':<14} | {'REGLA':<6} | {'CLASE':<6} | {'ARTEFACTO':<18} | {'MÉTRICAS'}")
    print("-" * 80)
    for d in dataset:
        clase_str = 'x+ (1)' if d['etiqueta_clase'] == 1 else 'x- (0)'
        metricas_str = ", ".join([f"{k}: {v}" for k, v in d['metricas_isomorfismo'].items()])
        print(f"{d['id_muestra']:<14} | {d['meta_regla']:<6} | {clase_str:<6} | {d['tipo_artefacto']:<18} | {metricas_str}")

    print(f"\n[+] Extracción completada. {len(dataset)} artefactos guardados en 'dataset_isomorfico.json'.")

if __name__ == '__main__':
    construir_dataset()