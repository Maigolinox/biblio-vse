# Biblio-VSE v2 extension (N=32 -> N=96), part A: DOCUMENTAL, CALIDAD, GOBERNANZA.
# Each entry follows the mutation protocol of the original benchmark: a compliant
# (POS) and a violating (NEG) variant of the same scenario, plus adversarial
# Type-B negatives (compliance keywords in a non-compliant context) and Type-C
# positives (compliant without the keywords used by the regex baseline).
# Artifacts contain no comments that state their own label.

from _schema import A

ARTIFACTS = [

# ─────────────────────────── DOCUMENTAL ───────────────────────────
A("EXT-DOCUMENTAL-01-POS", "DOCUMENTAL", "documento_texto", "docs/BVSE-PP-001_V1.2.0.md", 1, "doc-01", """\
# Plan del Proyecto Biblio-VSE
**Código:** BVSE-PP-001
**Versión:** V1.2.0
**Fecha de Vigencia:** 2026-02-02

## 1. Propósito

Este plan describe cómo el equipo va a construir y entregar la segunda versión del sistema de préstamos de la biblioteca municipal. Aquí se indican las tareas, los tiempos y las personas que participan, para que el cliente y el equipo tengan la misma idea de lo que se va a entregar y en qué fecha.

## 2. Alcance

El proyecto incluye el módulo de catálogo, el módulo de préstamos y devoluciones, y el cálculo de multas por retraso. No se incluye en esta etapa la aplicación móvil ni la integración con el sistema de nómina del municipio.

## 3. Calendario

| Hito | Fecha estimada |
|---|---|
| Catálogo en ambiente de pruebas | 2026-02-27 |
| Préstamos y devoluciones | 2026-03-20 |
| Entrega final al cliente | 2026-04-10 |

## 4. Riesgos

Si el cliente tarda en revisar los entregables, las fechas del calendario se moverán la misma cantidad de días. Para reducir este riesgo, las revisiones se agendan con una semana de anticipación.
"""),

A("EXT-DOCUMENTAL-01-NEG", "DOCUMENTAL", "documento_texto", "docs/plan_proyecto_nuevo.md", 0, "doc-01", """\
# Plan del proyecto (lo que vamos a hacer)

## 1. Propósito

Este plan describe cómo el equipo va a construir y entregar la segunda versión del sistema de préstamos de la biblioteca municipal. Aquí se indican las tareas, los tiempos y las personas que participan, para que el cliente y el equipo tengan la misma idea de lo que se va a entregar y en qué fecha.

## 2. Alcance

El proyecto incluye el módulo de catálogo, el módulo de préstamos y devoluciones, y el cálculo de multas por retraso. No se incluye en esta etapa la aplicación móvil ni la integración con el sistema de nómina del municipio.

## 3. Calendario

| Hito | Fecha estimada |
|---|---|
| Catálogo en ambiente de pruebas | finales de febrero |
| Préstamos y devoluciones | marzo |
| Entrega final al cliente | abril, más o menos |

## 4. Riesgos

Si el cliente tarda en revisar los entregables, las fechas del calendario se moverán. Hay que ver cómo lo manejamos.
"""),

A("EXT-DOCUMENTAL-02-POS", "DOCUMENTAL", "documento_texto", "docs/diseno/BVSE-DIS-003.md", 1, "doc-02", """\
# Especificación de Diseño — Módulo de Multas
**Código:** BVSE-DIS-003
**Versión:** V2.0.1
**Fecha de Vigencia:** 2026-03-05

## Descripción general

El módulo de multas calcula el monto que debe pagar un usuario cuando devuelve un libro después de la fecha acordada. El cálculo se hace una sola vez, en el momento en que se registra la devolución, y el resultado se guarda para que no cambie si después se modifica la tarifa.

## Componentes

- `CalculadoraMulta`: recibe el préstamo y la fecha real de devolución, y regresa el monto.
- `TarifaVigente`: consulta la tarifa diaria que estaba activa el día en que venció el préstamo.
- `RegistroMulta`: guarda el monto, la fecha y el usuario en la tabla de multas.

## Decisiones de diseño

Se decidió no calcular multas en tiempo real porque el cliente pidió que el monto quede fijo desde la devolución. También se decidió que los días feriados sí cuentan como días de retraso, de acuerdo con el reglamento de la biblioteca.
"""),

A("EXT-ADVB-DOCUMENTAL-02-NEG", "DOCUMENTAL", "documento_texto", "docs/diseno/diseno_multas_borrador.md", 0, "doc-02", """\
# Especificación de Diseño — Módulo de Multas
**Código:** (se asignará cuando se registre en el control documental)
**Versión:** borrador, sin número
**Fecha de Vigencia:** por definir

## Descripción general

El módulo de multas calcula el monto que debe pagar un usuario cuando devuelve un libro después de la fecha acordada. El cálculo se hace una sola vez, en el momento en que se registra la devolución, y el resultado se guarda para que no cambie si después se modifica la tarifa.

## Componentes

- `CalculadoraMulta`: recibe el préstamo y la fecha real de devolución, y regresa el monto.
- `TarifaVigente`: consulta la tarifa diaria que estaba activa el día en que venció el préstamo.
- `RegistroMulta`: guarda el monto, la fecha y el usuario en la tabla de multas.

## Decisiones de diseño

Se decidió no calcular multas en tiempo real porque el cliente pidió que el monto quede fijo desde la devolución.
""",
  adv="tipo_b", note="Los campos Código, Versión y Fecha de Vigencia existen (activan el regex) pero sus valores están vacíos o pendientes; el documento no tiene identificación formal."),

A("EXT-ADVB-DOCUMENTAL-03-NEG", "DOCUMENTAL", "documento_texto", "docs/manual_usuario.md", 0, "doc-03", """\
# Manual de uso del sistema de préstamos

Este manual explica a los bibliotecarios cómo registrar un préstamo, cómo recibir una devolución y cómo consultar las multas de un usuario. Para entender la arquitectura del sistema consulte el documento BVSE-ARQ-001, Versión V1.0.0, cuya Fecha de Vigencia es 2026-03-16.

## Registrar un préstamo

1. Entre al sistema con su usuario de bibliotecario.
2. Busque el libro por título o por ISBN.
3. Escriba el número de credencial del usuario y presione "Prestar".

## Recibir una devolución

1. Busque el préstamo por el número de credencial del usuario.
2. Presione "Devolver". Si el libro llega tarde, el sistema le mostrará la multa que corresponde.

## Consultar multas

En el menú "Usuarios" seleccione la persona y abra la pestaña "Multas". Ahí aparecen las multas pagadas y las que siguen pendientes.
""",
  adv="tipo_b", note="Las palabras Versión, Fecha de Vigencia y el patrón BVSE-ARQ-001 aparecen, pero se refieren a OTRO documento citado; el manual mismo no tiene código, versión ni fecha."),

A("EXT-ADVC-DOCUMENTAL-03-POS", "DOCUMENTAL", "documento_texto", "docs/reportes/RP-2026-07.md", 1, "doc-03", """\
# Informe de resultados de la iteración 3

| Clave del documento | RP-2026-07 |
|---|---|
| Revisión | 3 |
| En vigor desde | 15 de marzo de 2026 |
| Elaboró | Luis Martínez |

## Resumen

Durante la tercera iteración se terminaron el módulo de devoluciones y la pantalla de consulta de multas. Quedó pendiente la exportación de reportes a hoja de cálculo, que pasa a la siguiente iteración por petición del cliente.

## Avance por módulo

- Catálogo: terminado y en uso por el personal de la biblioteca.
- Préstamos y devoluciones: terminado; se corrigieron dos defectos reportados por el cliente.
- Multas: la consulta funciona; falta el reporte mensual.

## Observaciones

El cliente pidió que los avisos de retraso se envíen también por mensaje de texto. Se registró como una solicitud nueva y se evaluará en la siguiente reunión de planeación.
""",
  adv="tipo_c", note="Tiene identificador (RP-2026-07), número de revisión y fecha en vigor, pero con los términos Clave/Revisión/En vigor desde en lugar de Código/Versión/Fecha de Vigencia/BVSE-*."),

A("EXT-DOCUMENTAL-04-POS", "DOCUMENTAL", "documento_texto", "docs/BVSE-SC-004_V1.0.0.md", 1, "doc-04", """\
# Registro de Solicitudes de Cambio
**Código:** BVSE-SC-004
**Versión:** V1.0.0
**Fecha de Vigencia:** 2026-03-18

## Uso de este registro

Cada vez que el cliente o el equipo pidan un cambio a lo que ya se había acordado, el cambio se anota en esta tabla. Así se puede saber quién lo pidió, por qué, y qué se decidió hacer con él.

| Solicitud | Descripción | Solicitante | Decisión |
|---|---|---|---|
| SC-01 | Enviar avisos de retraso por mensaje de texto | Director de biblioteca | Se evaluará en la iteración 4 |
| SC-02 | Mostrar la portada del libro en el catálogo | Personal de préstamo | Aceptada |
| SC-03 | Permitir renovar un préstamo desde casa | Usuarios | Aceptada con cambios |

## Notas

Las solicitudes aceptadas se agregan al plan de la siguiente iteración. Las que no se aceptan se quedan en la tabla con el motivo, para que no se vuelvan a discutir sin información.
"""),

A("EXT-DOCUMENTAL-04-NEG", "DOCUMENTAL", "documento_texto", "docs/como_instalar.txt", 0, "doc-04", """\
Cómo instalar el sistema en una computadora nueva

Primero hay que tener Python instalado. Después se descarga el proyecto del repositorio y se crea un ambiente virtual para que las librerías no se mezclen con las de otros proyectos.

Luego se instalan las dependencias con el archivo de requerimientos. Si sale un error con la librería de PostgreSQL, casi siempre es porque falta instalar el cliente de la base de datos en la computadora.

Al final se corren las migraciones y se crea un usuario administrador. Con eso ya se puede entrar al sistema desde el navegador y empezar a capturar libros.

Si algo no funciona, pregúntale a Ana o a Luis, ellos lo instalaron la última vez.
"""),

# ─────────────────────────── CALIDAD ───────────────────────────
A("EXT-CALIDAD-01-POS", "CALIDAD", "codigo_fuente", "prestamos/services.py", 1, "cal-01", '''\
"""Servicios de dominio para el registro de préstamos."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from catalogo.models import Libro
from prestamos.models import Prestamo

DIAS_PRESTAMO_ESTANDAR = 14
MAXIMO_PRESTAMOS_ACTIVOS = 3


def contar_prestamos_activos(usuario):
    """Devuelve el número de préstamos sin devolver del usuario."""
    return Prestamo.objects.filter(usuario=usuario, devuelto=False).count()


@transaction.atomic
def registrar_prestamo(usuario, isbn):
    """Registra un préstamo si el libro está disponible y el usuario no excede el límite."""
    if contar_prestamos_activos(usuario) >= MAXIMO_PRESTAMOS_ACTIVOS:
        raise ValueError("El usuario alcanzó el máximo de préstamos activos.")

    libro = Libro.objects.select_for_update().get(isbn=isbn)
    if not libro.disponible:
        raise ValueError("El libro no está disponible.")

    fecha_limite = timezone.now().date() + timedelta(days=DIAS_PRESTAMO_ESTANDAR)
    libro.disponible = False
    libro.save(update_fields=["disponible"])
    return Prestamo.objects.create(
        usuario=usuario, libro=libro, fecha_devolucion_esperada=fecha_limite
    )
'''),

A("EXT-CALIDAD-01-NEG", "CALIDAD", "codigo_fuente", "prestamos/servicios2.py", 0, "cal-01", '''\
import os, sys, json, re
from datetime import *
from django.db import transaction
from django.utils import timezone
from catalogo.models import Libro
from prestamos.models import Prestamo
def RegistrarPrestamo(u,i):
  c=Prestamo.objects.filter(usuario=u,devuelto=False).count()
  if c>=3:
      raise ValueError("limite")
  l=Libro.objects.get(isbn=i)
  if l.disponible==False: raise ValueError("no")
  f=timezone.now().date()+timedelta(days=14)
  l.disponible=False;l.save()
  tmp = Prestamo.objects.create(usuario=u,libro=l,fecha_devolucion_esperada=f)
  if tmp.id>9999:
        print("muchos")
  return tmp
'''),

A("EXT-CALIDAD-02-POS", "CALIDAD", "codigo_fuente", "catalogo/forms.py", 1, "cal-02", '''\
"""Formularios del módulo de catálogo."""
from django import forms

from catalogo.models import Libro

LONGITUD_ISBN = 13


class LibroForm(forms.ModelForm):
    """Formulario para registrar o editar un libro del catálogo."""

    class Meta:
        model = Libro
        fields = ["titulo", "autor", "isbn", "categoria"]

    def clean_isbn(self):
        """Valida que el ISBN tenga exactamente trece dígitos."""
        isbn = self.cleaned_data["isbn"].replace("-", "")
        if len(isbn) != LONGITUD_ISBN or not isbn.isdigit():
            raise forms.ValidationError("El ISBN debe tener 13 dígitos.")
        return isbn


class BusquedaLibroForm(forms.Form):
    """Formulario de búsqueda por título, autor o ISBN."""

    termino = forms.CharField(max_length=120, required=True)
'''),

A("EXT-CALIDAD-02-NEG", "CALIDAD", "codigo_fuente", "catalogo/forms_v2.py", 0, "cal-02", '''\
from django.forms import *
import datetime, re, logging
from catalogo.models import *

class libroform(ModelForm):
  class Meta:
    model=Libro
    fields='__all__'
  def clean_isbn(self):
    x=self.cleaned_data['isbn'].replace('-','')
    if len(x)!=13 or not x.isdigit(): raise ValidationError('mal isbn')
    return x

class buscar(Form):
      t=CharField(max_length=120)
      aux=CharField(required=False)
'''),

A("EXT-ADVB-CALIDAD-03-NEG", "CALIDAD", "codigo_fuente", "reportes/exportar.py", 0, "cal-03", '''\
# Revisado con flake8 y con la Lista de Cotejo BVSE-QA-MR antes de subirlo.
import csv, io, os, sys, time
from django.http import HttpResponse
from prestamos.models import Prestamo

def exp(r,m,a):
    q=Prestamo.objects.filter(fecha_inicio__month=m,fecha_inicio__year=a)
    b=io.StringIO();w=csv.writer(b)
    for p in q:
        if p.dias_prestamo>21: w.writerow([p.id,p.libro.titulo,p.dias_prestamo*2.5])
        else: w.writerow([p.id,p.libro.titulo,0])
    resp=HttpResponse(b.getvalue(),content_type='text/csv')
    resp['Content-Disposition']='attachment; filename="r.csv"'
    return resp
''',
  adv="tipo_b", note="Afirma haber pasado flake8 y la Lista de Cotejo (activa el regex), pero el código tiene imports sin usar, nombres no descriptivos, números mágicos y varias sentencias por línea."),

A("EXT-ADVC-CALIDAD-03-POS", "CALIDAD", "codigo_fuente", "reportes/exportacion_csv.py", 1, "cal-03", '''\
"""Exportación del reporte mensual de préstamos en formato CSV."""
import csv
import io

from django.http import HttpResponse

from prestamos.models import Prestamo

DIAS_SIN_CARGO = 21
CARGO_POR_DIA_EXTRA = 2.5


def calcular_cargo(prestamo):
    """Calcula el cargo por los días que exceden el periodo sin cargo."""
    dias_extra = max(0, prestamo.dias_prestamo - DIAS_SIN_CARGO)
    return dias_extra * CARGO_POR_DIA_EXTRA


def exportar_reporte_mensual(request, mes, anio):
    """Genera un archivo CSV con los préstamos del mes indicado."""
    prestamos = Prestamo.objects.filter(
        fecha_inicio__month=mes, fecha_inicio__year=anio
    ).select_related("libro")

    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerow(["id", "titulo", "cargo"])
    for prestamo in prestamos:
        escritor.writerow([prestamo.id, prestamo.libro.titulo, calcular_cargo(prestamo)])

    respuesta = HttpResponse(buffer.getvalue(), content_type="text/csv")
    respuesta["Content-Disposition"] = 'attachment; filename="prestamos.csv"'
    return respuesta
''',
  adv="tipo_c", note="Código limpio (constantes con nombre, docstrings, imports usados y ordenados) sin mencionar linter, flake8, lista de cotejo ni pruebas unitarias."),

A("EXT-CALIDAD-04-POS", "CALIDAD", "pipeline_ci", ".gitlab-ci.yml", 1, "cal-04", """\
stages:
  - calidad
  - pruebas

verificar_estilo:
  stage: calidad
  image: python:3.10
  script:
    - pip install flake8 black isort
    - flake8 catalogo prestamos reportes --max-line-length 100
    - black --check catalogo prestamos reportes
    - isort --check-only catalogo prestamos reportes

pruebas_unitarias:
  stage: pruebas
  image: python:3.10
  needs: ["verificar_estilo"]
  script:
    - pip install -r requirements.txt
    - python manage.py test
"""),

A("EXT-ADVB-CALIDAD-04-NEG", "CALIDAD", "pipeline_ci", ".gitlab-ci-rapido.yml", 0, "cal-04", """\
stages:
  - calidad
  - deploy

verificar_estilo:
  stage: calidad
  image: python:3.10
  allow_failure: true
  script:
    - pip install flake8
    - flake8 catalogo prestamos reportes || true

desplegar:
  stage: deploy
  script:
    - ./scripts/deploy.sh
""",
  adv="tipo_b", note="Incluye un job con flake8 (activa el regex), pero está configurado con allow_failure y '|| true', por lo que los errores de estilo nunca detienen el despliegue."),

# ─────────────────────────── GOBERNANZA ───────────────────────────
A("EXT-GOBERNANZA-01-POS", "GOBERNANZA", "documento_texto", "docs/politicas/BVSE-POL-002.md", 1, "gob-01", """\
# Política de Gestión de Cambios — BVSE-POL-002
**Estado:** Aprobado
**Autoriza:** Director del Proyecto Biblio-VSE
**Fecha de aprobación:** 2026-02-20

## Objetivo

Esta política define cómo se aceptan los cambios al sistema una vez que el cliente aprobó los requerimientos. Su propósito es que ningún cambio llegue a producción sin que alguien responsable lo haya revisado.

## Controles

1. Todo cambio se registra primero como solicitud en el registro BVSE-SC-004.
2. El coordinador técnico evalúa el impacto en tiempo y costo antes de aceptarlo.
3. El código del cambio se integra solo mediante una solicitud de fusión revisada por otra persona del equipo.
4. Ningún cambio se despliega en producción sin la aprobación escrita del director del proyecto.

## Excepciones

Las correcciones urgentes de seguridad pueden desplegarse antes de la aprobación escrita, pero deben documentarse en un plazo máximo de dos días hábiles.
"""),

A("EXT-GOBERNANZA-01-NEG", "GOBERNANZA", "documento_texto", "docs/idea_proceso_cambios.md", 0, "gob-01", """\
# Idea para manejar los cambios (propuesta)

Últimamente nos han pedido muchos cambios de última hora y a veces no sabemos quién los pidió. Escribo aquí algunas ideas para que las platiquemos, nada de esto está decidido todavía.

- Podríamos anotar los cambios en una hoja compartida.
- Tal vez alguien debería revisar el código antes de subirlo, aunque a veces no hay tiempo.
- Lo de pedir permiso al director para cada cambio suena lento, mejor avisarle después.

Comentarios bienvenidos. Si nadie dice nada, seguimos como hasta ahora.
"""),

A("EXT-ADVB-GOBERNANZA-02-NEG", "GOBERNANZA", "codigo_fuente", "prestamos/renovaciones.py", 0, "gob-02", '''\
# prestamos/renovaciones.py
# Aprobado por: ____________________ (pendiente de firma)
# Autoriza: _______________________
# Firma Digital: no se ha generado
from django.http import JsonResponse
from django.utils import timezone
from prestamos.models import Prestamo


def renovar_prestamo(request, prestamo_id):
    prestamo = Prestamo.objects.get(pk=prestamo_id)
    prestamo.fecha_devolucion_esperada += timezone.timedelta(days=7)
    prestamo.save()
    return JsonResponse({"renovado": True})
''',
  adv="tipo_b", note="Contiene las etiquetas Aprobado, Autoriza y Firma Digital (activan el regex) pero todas están vacías o pendientes; no existe aprobación."),

A("EXT-GOBERNANZA-03-NEG", "GOBERNANZA", "codigo_fuente", "prestamos/ajuste_multas.py", 0, "gob-03", '''\
# lo subí directo a main porque el director lo necesitaba hoy, luego abrimos el ticket
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from prestamos.models import Multa


@staff_member_required
def condonar_multas_masivo(request):
    total = Multa.objects.filter(pagada=False).update(pagada=True, monto_total=0)
    return JsonResponse({"multas_condonadas": total})
'''),

A("EXT-ADVC-GOBERNANZA-03-POS", "GOBERNANZA", "pipeline_ci", ".gitlab-ci.yml", 1, "gob-03", """\
# Despliegue a producción conforme a la política de cambios PC-04:
# el job solo se ejecuta sobre etiquetas de versión, requiere que la solicitud
# de fusión tenga la revisión de dos integrantes (reglas de CODEOWNERS) y queda
# detenido hasta que el coordinador técnico lo libera manualmente en el
# ambiente protegido "produccion".
stages:
  - deploy

desplegar_produccion:
  stage: deploy
  environment:
    name: produccion
    deployment_tier: production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\\d+\\.\\d+\\.\\d+$/
      when: manual
  script:
    - ./scripts/deploy.sh produccion
  resource_group: produccion
""",
  adv="tipo_c", note="Evidencia controles formales (política PC-04, revisión obligatoria de dos personas, liberación manual en ambiente protegido) sin las palabras Aprobado, Autoriza, Firma Digital ni BVSE-REQ-*."),

A("EXT-ADVB-GOBERNANZA-04-NEG", "GOBERNANZA", "codigo_fuente", "config/flujo_aprobaciones.py", 0, "gob-04", '''\
"""Configuración del flujo de aprobaciones de Biblio-VSE."""

# Firma Digital de los requerimientos (BVSE-REQ-*): desactivada para agilizar
# los despliegues de esta temporada.
REQUIERE_FIRMA_DIGITAL = False

# Revisión del coordinador antes de fusionar: desactivada.
REQUIERE_REVISION_COORDINADOR = False


def puede_desplegar(solicitud):
    """Permite desplegar cualquier solicitud mientras los controles estén apagados."""
    if REQUIERE_FIRMA_DIGITAL and not solicitud.firmada:
        return False
    if REQUIERE_REVISION_COORDINADOR and not solicitud.revisada:
        return False
    return True
''',
  adv="tipo_b", note="Menciona Firma Digital y BVSE-REQ-* (activan el regex), pero el código desactiva precisamente esos controles de gobernanza."),
]
