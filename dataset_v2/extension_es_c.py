# Biblio-VSE v2 extension, part C: RESPALDO, ACUERDOS, INFRA.
# Names of people are fictitious; IP addresses use private (RFC 1918) or
# documentation (RFC 5737) ranges.

from _schema import A

ARTIFACTS = [

# ─────────────────────────── RESPALDO ───────────────────────────
A("EXT-RESPALDO-01-POS", "RESPALDO", "pipeline_ci", ".gitlab-ci.yml", 1, "res-01", """\
stages:
  - backup
  - verificar

backup_completo_nocturno:
  stage: backup
  image: postgres:15
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - export ARCHIVO="biblio_completo_$(date +%Y%m%d).dump"
    - pg_dump -Fc -h "$DB_HOST" -U "$DB_USER" biblio > "$ARCHIVO"
    - aws s3 cp "$ARCHIVO" s3://biblio-respaldos/diarios/
    - aws s3 ls s3://biblio-respaldos/diarios/ | tail -7

verificar_restauracion:
  stage: verificar
  image: postgres:15
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
  script:
    - aws s3 cp "s3://biblio-respaldos/diarios/biblio_completo_$(date +%Y%m%d).dump" prueba.dump
    - createdb -h "$DB_HOST_PRUEBAS" -U "$DB_USER" biblio_verificacion
    - pg_restore -h "$DB_HOST_PRUEBAS" -U "$DB_USER" -d biblio_verificacion prueba.dump
"""),

A("EXT-RESPALDO-01-NEG", "RESPALDO", "pipeline_ci", ".gitlab-ci.yml", 0, "res-01", """\
stages:
  - migrar
  - deploy

aplicar_migraciones:
  stage: migrar
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python manage.py migrate --noinput

desplegar:
  stage: deploy
  needs: ["aplicar_migraciones"]
  script:
    - ./scripts/deploy.sh produccion
  only:
    - main
"""),

A("EXT-RESPALDO-02-POS", "RESPALDO", "documento_texto", "docs/operacion/procedimiento_respaldo.md", 1, "res-02", """\
# Procedimiento de respaldo y recuperación de la base de datos

## Tipo y periodicidad

- Respaldo completo: cada domingo a las 02:00 con pg_dump en formato personalizado.
- Respaldo incremental: todos los días a las 02:00 mediante el archivado continuo de los registros WAL.

## Ubicación

Los archivos se guardan en la cubeta biblio-respaldos, en una región distinta a la del servidor de producción. Se conservan cuatro respaldos completos y los incrementales de los últimos 28 días.

## Recuperación

1. Detener el servicio de la aplicación.
2. Descargar el último respaldo completo y los archivos WAL posteriores.
3. Ejecutar pg_restore sobre una base de datos vacía y aplicar los WAL hasta la hora deseada.
4. Verificar el número de préstamos del día anterior y reiniciar el servicio.

## Prueba de recuperación

El primer lunes de cada mes el responsable de infraestructura restaura el respaldo en el servidor de pruebas y anota el resultado en la bitácora de operación.
"""),

A("EXT-RESPALDO-02-NEG", "RESPALDO", "documento_texto", "docs/operacion/actualizar_version.md", 0, "res-02", """\
# Cómo actualizar el sistema a una nueva versión

1. Avisar al personal de la biblioteca que el sistema estará detenido unos minutos.
2. Entrar al servidor y descargar la nueva versión del repositorio.
3. Instalar las dependencias nuevas, si las hay.
4. Aplicar las migraciones de la base de datos directamente sobre producción.
5. Reiniciar el servicio y revisar que la página de préstamos cargue.

Si algo sale mal después de migrar, se puede intentar regresar a la versión anterior del código. Los datos que ya se hayan modificado tendrán que corregirse a mano.
"""),

A("EXT-ADVB-RESPALDO-03-NEG", "RESPALDO", "pipeline_ci", ".gitlab-ci.yml", 0, "res-03", """\
stages:
  - backup
  - deploy

backup:
  stage: backup
  script:
    - echo "TODO: implementar el backup antes de salir a producción"
    - exit 0

desplegar:
  stage: deploy
  script:
    - ./scripts/deploy.sh produccion
""",
  adv="tipo_b", note="Tiene un stage y un job llamados backup (activan el regex), pero el job solo imprime un TODO y termina; no se genera ningún respaldo."),

A("EXT-ADVC-RESPALDO-03-POS", "RESPALDO", "pipeline_ci", ".github/workflows/archivo_nocturno.yml", 1, "res-03", """\
name: Archivo nocturno de datos

on:
  schedule:
    - cron: '30 1 * * *'

jobs:
  archivar:
    runs-on: self-hosted
    steps:
      - name: Crear archivo deduplicado del volumen de PostgreSQL
        run: |
          borg create --stats --compression zstd \\
            /mnt/archivo/biblio::biblio-{now:%Y-%m-%d} /var/lib/postgresql/15/main

      - name: Retención (7 diarios, 4 semanales, 6 mensuales)
        run: borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 /mnt/archivo/biblio

      - name: Verificar integridad y que el archivo se pueda extraer
        run: |
          borg check /mnt/archivo/biblio
          borg extract --dry-run /mnt/archivo/biblio::biblio-$(date +%Y-%m-%d)
""",
  adv="tipo_c", note="Copia programada, deduplicada y verificada con BorgBackup (borg create/prune/check/extract) y política de retención, sin las palabras backup, dump, pg_dump, restore ni respaldo."),

A("EXT-ADVB-RESPALDO-04-NEG", "RESPALDO", "documento_texto", "docs/operacion/plan_respaldo.md", 0, "res-04", """\
# Plan de respaldo (situación actual)

Hasta febrero existía un script con pg_dump que se ejecutaba desde la computadora de Pedro. Ese script se eliminó cuando se cambió de servidor y no se volvió a configurar.

Por ahora no está definida la periodicidad de los respaldos, no hay una ubicación asignada para guardarlos y nadie ha probado un restore de la base de datos actual.

Pendiente: decidir quién se encarga del tema en la próxima reunión.
""",
  adv="tipo_b", note="Menciona pg_dump, respaldo y restore (activan el regex), pero declara que no existe respaldo vigente, periodicidad, ubicación ni procedimiento probado."),

# ─────────────────────────── ACUERDOS ───────────────────────────
A("EXT-ACUERDOS-01-POS", "ACUERDOS", "documento_texto", "docs/actas/BVSE-ACTA-005.md", 1, "acu-01", """\
# Acta de Revisión de la Iteración 3 — BVSE-ACTA-005
**Fecha:** 2026-03-21
**Estado:** Aprobado

## Participantes

| Nombre | Rol | Organización |
|---|---|---|
| Rosa Delgado | Directora de la biblioteca | Cliente |
| Ana García | Desarrolladora principal | Equipo Biblio-VSE |
| María Torres | Responsable de calidad | Equipo Biblio-VSE |

## Acuerdos

**Acuerdo 01:** El cliente acepta el módulo de devoluciones entregado en la iteración 3.
- **Responsable:** Rosa Delgado
- **Fecha:** 2026-03-21

**Acuerdo 02:** El equipo corregirá el formato de fechas del reporte mensual antes del 2026-03-28.
- **Responsable:** Ana García

**Acuerdo 03:** La responsable de calidad repetirá las pruebas del reporte y enviará el resultado al cliente.
- **Responsable:** María Torres

## Firmas

| Nombre | Firma |
|---|---|
| Rosa Delgado | *R. Delgado* |
| Ana García | *A. García* |
| María Torres | *M. Torres* |
"""),

A("EXT-ACUERDOS-01-NEG", "ACUERDOS", "documento_texto", "docs/resumen_chat_cliente.txt", 0, "acu-01", """\
Resumen del chat con la biblioteca (lo copio para que no se pierda)

- La directora dijo que las devoluciones se ven bien, aunque quiere verlas otra vez con calma.
- Creo que quedamos en arreglar lo de las fechas del reporte, pero no dijimos para cuándo.
- Alguien del equipo iba a repetir las pruebas del reporte, no recuerdo si Ana o María.
- Quedamos en hablar la próxima semana para cerrar todo.
"""),

A("EXT-ACUERDOS-02-POS", "ACUERDOS", "documento_texto", "docs/contratos/BVSE-CONV-001.md", 1, "acu-02", """\
# Convenio de Servicios de Mantenimiento — BVSE-CONV-001
**Estado:** Aprobado
**Vigencia:** del 2026-04-01 al 2027-03-31

## Partes

- **La Biblioteca:** Biblioteca Municipal, representada por su directora, Rosa Delgado.
- **El Proveedor:** Equipo Biblio-VSE, representado por su coordinador técnico, Jorge Ruiz.

## Obligaciones del Proveedor

1. Corregir los defectos críticos en un plazo máximo de 48 horas hábiles.
2. Entregar una versión de mantenimiento cada tres meses.
3. Informar mensualmente las incidencias atendidas.

## Obligaciones de la Biblioteca

1. Reportar los defectos por el canal acordado, con la descripción del problema.
2. Dar acceso al servidor de pruebas cuando el Proveedor lo solicite.

## Firmas

Leído el presente convenio, las partes lo firman de conformidad el 2026-03-25.

| Por la Biblioteca | Por el Proveedor |
|---|---|
| Rosa Delgado — *firma* | Jorge Ruiz — *firma* |
"""),

A("EXT-ADVB-ACUERDOS-02-NEG", "ACUERDOS", "documento_texto", "docs/contratos/convenio_borrador.md", 0, "acu-02", """\
# Convenio de Servicios de Mantenimiento — BORRADOR
Estado: borrador, pendiente de revisión jurídica

## Partes

- La Biblioteca Municipal (representante por confirmar).
- El Equipo Biblio-VSE.

## Obligaciones propuestas

Acuerdo 1: corregir defectos críticos "lo antes posible" (plazo por definir).
Responsable: por asignar

Acuerdo 2: entregar versiones de mantenimiento periódicas.
Responsable: por asignar

## Firmas

Este documento no ha sido firmado. No tiene validez hasta que ambas partes lo aprueben.
""",
  adv="tipo_b", note="Contiene 'Acuerdo 1', 'Responsable:' y 'Estado:' (activan el regex), pero es un borrador sin representantes definidos, sin responsables asignados, sin aprobación y sin firmas."),

A("EXT-ADVC-ACUERDOS-03-POS", "ACUERDOS", "documento_texto", "docs/actas/minuta_direccion_2026-03-27.md", 1, "acu-03", """\
# Minuta de la sesión con la Dirección de la Biblioteca — 27 de marzo de 2026

Asistieron la directora Rosa Delgado, en representación de la Biblioteca Municipal, y el coordinador técnico Jorge Ruiz, en representación del equipo de desarrollo.

La directora se compromete a entregar, a más tardar el 3 de abril, el reglamento actualizado de préstamos para que el sistema aplique los nuevos plazos. El coordinador técnico se compromete a que el equipo implemente esos plazos en la versión 2.2, cuya entrega se fija para el 17 de abril.

Ambas partes ratificaron los compromisos anteriores al término de la sesión y la minuta quedó rubricada por los dos representantes:

Rosa Delgado (rúbrica) — Jorge Ruiz (rúbrica)
""",
  adv="tipo_c", note="Identifica a las partes, fija compromisos con responsables y fechas, registra la ratificación y las rúbricas, sin las etiquetas 'Acuerdo N', 'Responsable:' ni 'Estado:'."),

A("EXT-ACUERDOS-04-POS", "ACUERDOS", "documento_texto", "docs/actas/BVSE-ACEP-003.md", 1, "acu-04", """\
# Carta de Aceptación de Entregable — BVSE-ACEP-003
**Estado:** Aprobado

Por medio de la presente, la Biblioteca Municipal, representada por su directora Rosa Delgado, acepta el entregable "Módulo de reservas anticipadas" desarrollado por el Equipo Biblio-VSE, representado por su coordinador técnico Jorge Ruiz.

## Condiciones de la aceptación

- **Responsable de la verificación:** María Torres, responsable de calidad, quien confirmó que el módulo pasó las pruebas TC-RES-001 a TC-RES-004.
- **Responsable de la puesta en marcha:** Pedro Ramírez, responsable de infraestructura, a más tardar el 2026-04-02.

## Firmas

| Rosa Delgado | Jorge Ruiz |
|---|---|
| *firma* | *firma* |

Fecha de firma: 2026-03-30
"""),

A("EXT-ACUERDOS-03-NEG", "ACUERDOS", "documento_texto", "docs/correo_plazos.txt", 0, "acu-03", """\
Asunto: RE: RE: plazos nuevos

Hola Jorge,

Sí, algo comentamos en la reunión sobre cambiar los plazos de préstamo, pero todavía lo tengo que platicar con el consejo. No te puedo confirmar nada por ahora.

Si ustedes quieren ir adelantando algo, adelante, pero no es seguro que se quede así.

Saludos,
Rosa
"""),

# ─────────────────────────── INFRA ───────────────────────────
A("EXT-INFRA-01-POS", "INFRA", "codigo_fuente", "config/settings_produccion_red.py", 1, "inf-01", '''\
"""Ajustes de red para el despliegue en producción de Biblio-VSE."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = [
    "prestamos.biblioteca.local",
    "api.biblioteca.local",
]

CSRF_TRUSTED_ORIGINS = [
    "https://prestamos.biblioteca.local",
    "https://api.biblioteca.local",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = False
'''),

A("EXT-INFRA-01-NEG", "INFRA", "codigo_fuente", "config/settings_produccion_red.py", 0, "inf-01", '''\
"""Ajustes de red para el despliegue en producción de Biblio-VSE."""
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://*",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
'''),

A("EXT-INFRA-02-POS", "INFRA", "pipeline_ci", ".gitlab-ci.yml", 1, "inf-02", """\
stages:
  - deploy

desplegar_intranet:
  stage: deploy
  environment:
    name: produccion-intranet
    url: https://prestamos.biblioteca.local
  tags:
    - runner-red-interna
  script:
    - rsync -az --delete ./ deploy@app01.biblioteca.local:/srv/biblio/
    - ssh deploy@app01.biblioteca.local "sudo systemctl restart biblio"
"""),

A("EXT-INFRA-02-NEG", "INFRA", "pipeline_ci", ".gitlab-ci.yml", 0, "inf-02", """\
stages:
  - deploy

desplegar_nube:
  stage: deploy
  environment:
    name: produccion
    url: http://203.0.113.25
  script:
    - rsync -az --delete ./ root@203.0.113.25:/srv/biblio/
    - ssh root@203.0.113.25 "ufw allow from any to any port 8000 && systemctl restart biblio"
    - ssh root@203.0.113.25 "gunicorn config.wsgi --bind 0.0.0.0:8000 --daemon"
"""),

A("EXT-ADVB-INFRA-03-NEG", "INFRA", "codigo_fuente", "config/settings_intranet.py", 0, "inf-03", '''\
"""Ajustes de hosts para la intranet de la biblioteca."""

DEBUG = False

ALLOWED_HOSTS = [
    "catalogo.biblioteca.local",
    "api.biblioteca.local",
    "localhost",
    "*",
]
''',
  adv="tipo_b", note="Incluye hosts biblioteca.local (activan el regex), pero la lista también contiene el comodín '*', que acepta cualquier host."),

A("EXT-ADVC-INFRA-03-POS", "INFRA", "pipeline_ci", "docker-compose.produccion.yml", 1, "inf-03", """\
services:
  web:
    image: registry.interno/biblio:2.1.0
    command: gunicorn config.wsgi --bind 0.0.0.0:8000
    networks:
      - red_aplicacion
    expose:
      - "8000"

  proxy:
    image: nginx:1.27
    ports:
      - "10.20.0.15:443:443"
    networks:
      - red_aplicacion

  db:
    image: postgres:15
    networks:
      - red_datos

networks:
  red_aplicacion:
    ipam:
      config:
        - subnet: 172.28.10.0/24
  red_datos:
    internal: true
""",
  adv="tipo_c", note="Solo el proxy publica un puerto, ligado a una IP privada (10.20.0.15); la base de datos está en una red sin salida. No aparecen biblioteca.local, '.internal' ni 'entornos autorizados'."),

A("EXT-ADVB-INFRA-04-NEG", "INFRA", "documento_texto", "docs/operacion/politica_red.md", 0, "inf-04", """\
# Política de red del servidor de aplicación

La política institucional indica que el sistema solo debe operar en entornos autorizados de la red interna (dominio biblioteca.local).

## Configuración vigente del firewall

| Regla | Origen | Puerto | Acción |
|---|---|---|---|
| 1 | 0.0.0.0/0 | 443 | Permitir |
| 2 | 0.0.0.0/0 | 22 | Permitir |
| 3 | 0.0.0.0/0 | 5432 | Permitir |

Nota: las reglas se abrieron a cualquier origen durante la migración de servidor y todavía no se han restringido.
""",
  adv="tipo_b", note="Cita 'entornos autorizados' y biblioteca.local (activan el regex), pero la configuración vigente documentada permite acceso desde cualquier origen, incluida la base de datos."),

A("EXT-INFRA-04-POS", "INFRA", "documento_texto", "docs/operacion/arquitectura_red.md", 1, "inf-04", """\
# Arquitectura de red de Biblio-VSE

El sistema se publica únicamente dentro de la red de la biblioteca. No existe ninguna regla que exponga los servicios a internet.

## Hosts permitidos

| Servicio | Nombre | Dirección |
|---|---|---|
| Aplicación web | prestamos.biblioteca.local | 10.20.0.15 |
| API | api.biblioteca.local | 10.20.0.16 |
| Base de datos | db.biblioteca.local | 10.20.1.5 |

## Reglas del firewall

| Regla | Origen | Puerto | Acción |
|---|---|---|---|
| 1 | 10.20.0.0/16 | 443 | Permitir |
| 2 | 10.20.0.15, 10.20.0.16 | 5432 | Permitir |
| 3 | Cualquier otro origen | Todos | Denegar |
"""),
]
