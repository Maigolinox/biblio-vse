# Edición de los artefactos de Biblio-VSE

Cada archivo de `es/` y `en/` es el contenido exacto de un artefacto del
benchmark. Edítalos con libertad: al terminar, ejecuta

    python dataset_v2/import_edited.py

que reconstruye `dataset_isomorfico_n96.json`, `_en.json` y `_noisy.json` y
vuelve a ejecutar todas las comprobaciones automáticas.

## Qué debe conservarse

1. **La etiqueta.** `metadata.json` indica, para cada artefacto, la meta-regla y
   si cumple (`etiqueta_clase` = 1) o la viola (0). El contenido editado debe
   seguir correspondiendo a esa etiqueta según el criterio de la meta-regla; si
   decides cambiar la etiqueta, edítala también en `metadata.json`.
2. **El diseño adversarial.** Los artefactos marcados `tipo_b` deben seguir
   activando el regex de su regla (contienen las palabras clave en un contexto
   que NO cumple); los `tipo_c` deben seguir cumpliendo SIN esas palabras clave.
   El importador verifica ambas condiciones y falla si dejan de cumplirse.
   `adversarial_nota` explica la intención de cada uno.
3. **El emparejamiento ES/EN.** Los archivos con el mismo nombre en `es/` y `en/`
   son el mismo artefacto en dos idiomas y deben seguir diciendo lo mismo.
4. **Los identificadores técnicos** (RF_05, HU-12, BVSE-*, nombres de host) se
   mantienen iguales en ambos idiomas.
5. **Nada de comentarios que revelen la etiqueta** (p. ej. "esto viola CALIDAD").

## Qué NO hace falta conservar

El estilo, la redacción, los nombres de variables, la longitud y los detalles
del escenario son libres. Los 32 artefactos originales (`origen=original_v1`)
pueden editarse igual, pero ten en cuenta que cambiarlos rompe la comparación
directa con los resultados del envío inicial.

Tras la edición hay que volver a ejecutar los experimentos (`run_condition.py`
para las cuatro condiciones y `experimento_gemini.py`), porque los resultados
publicados corresponden al texto actual de los artefactos.
