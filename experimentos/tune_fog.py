"""Verify final metrics after SMP-ACUERDOS-POS rewrite."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import textstat, statistics, json, ast as _ast
from radon.complexity import cc_visit

# Current n=8 Fog values (measured)
other_fogs = [18.79, 20.51, 20.52, 22.96, 17.51, 10.21, 22.27]  # all except ACUERDOS-POS
PRIVATE_MEAN = 18.61
THRESHOLD = 1.0

# Candidate rewrite of SMP-ACUERDOS-POS
# Goal: shorter sentences, same compliance signals (Acuerdo N, Responsable:, Estado:, Autoriza:)
candidate = """# Acta de Reunion de Diseno del Sistema - BVSE-ACTA-002
**Codigo:** BVSE-ACTA-002
**Version:** V1.0.0
**Fecha de Vigencia:** 2026-03-10
**Estado:** Aprobado

## Datos Generales de la Reunion

- **Fecha de Reunion:** 2026-03-10
- **Lugar:** Sala de reuniones del proyecto Biblio-VSE
- **Responsable de Coordinacion:** Coordinador del Proyecto

## Participantes del Proyecto

| Nombre | Rol | Presencia |
|---|---|---|
| Ana Garcia | Desarrolladora Principal | Presente |
| Luis Martinez | Responsable de Base de Datos | Presente |
| Maria Torres | Responsable de Calidad | Presente |
| Pedro Ramirez | Responsable de Infraestructura | Presente |

## Acuerdos Formalizados

**Acuerdo 01:** El equipo migrara las vistas funcionales al patron Class-Based Views de Django.
El objetivo es mejorar la mantenibilidad y extensibilidad del modulo.
El patron separa la logica de negocio de la capa de presentacion.
- **Responsable:** Ana Garcia, Desarrolladora Principal
- **Fecha de Implementacion:** 2026-03-20
- **Estado:** En Proceso

**Acuerdo 02:** Luis Martinez agregara indices de optimizacion en las tablas de prestamos y usuarios.
Esta mejora reducira el tiempo de respuesta en las consultas del sistema.
Los indices se aplicaran sobre las columnas de fecha y estado del registro.
- **Responsable:** Luis Martinez, Responsable de Base de Datos
- **Fecha de Implementacion:** 2026-03-17
- **Estado:** Pendiente

**Acuerdo 03:** Maria Torres ejecutara la validacion del modulo de autenticacion antes del despliegue.
La cobertura incluira los flujos de ingreso y gestion de sesiones del usuario.
El resultado se documentara en el informe de calidad del sistema.
- **Responsable:** Maria Torres, Responsable de Calidad
- **Fecha de Validacion:** 2026-03-15
- **Estado:** En Proceso

## Aprobacion del Acta

**Autoriza:** Director del Proyecto del Sistema Biblio-VSE
**Estado del Documento:** Aprobado
"""

fog_new = textstat.gunning_fog(candidate)
all_fogs = other_fogs + [fog_new]
new_mean = statistics.mean(all_fogs)
delta = abs(new_mean - PRIVATE_MEAN)

print(f"Candidate SMP-ACUERDOS-POS Fog: {fog_new:.2f}  (was 33.31)")
print(f"New n=8 mean Fog: {new_mean:.2f}  (was 20.76, private=18.61)")
print(f"|Delta_mu| = {delta:.2f}  (threshold = {THRESHOLD})")
print(f"STATUS: {'PASSES' if delta <= THRESHOLD else 'FAILS'}")
print()
print("All n=8 fogs:", [round(f,2) for f in all_fogs])
