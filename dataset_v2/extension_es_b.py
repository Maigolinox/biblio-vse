# Biblio-VSE v2 extension, part B: SEGURIDAD, TRAZABILIDAD, PRUEBAS.
# All secrets below are fabricated placeholders created for the benchmark.

from _schema import A

ARTIFACTS = [

# ─────────────────────────── SEGURIDAD ───────────────────────────
A("EXT-SEGURIDAD-01-POS", "SEGURIDAD", "codigo_fuente", "notificaciones/cliente_correo.py", 1, "seg-01", '''\
"""Cliente de correo para los avisos de vencimiento de préstamos."""
import os
import smtplib
from email.message import EmailMessage

SERVIDOR_SMTP = os.getenv("SMTP_HOST", "smtp.biblioteca.local")
PUERTO_SMTP = int(os.getenv("SMTP_PORT", "587"))
USUARIO_SMTP = os.getenv("SMTP_USER")
CLAVE_SMTP = os.getenv("SMTP_PASSWORD")


def enviar_aviso(destinatario, titulo_libro, fecha_limite):
    """Envía un aviso de vencimiento al usuario del préstamo."""
    mensaje = EmailMessage()
    mensaje["Subject"] = "Tu préstamo está por vencer"
    mensaje["To"] = destinatario
    mensaje.set_content(f"El libro '{titulo_libro}' debe devolverse el {fecha_limite}.")
    with smtplib.SMTP(SERVIDOR_SMTP, PUERTO_SMTP) as servidor:
        servidor.starttls()
        servidor.login(USUARIO_SMTP, CLAVE_SMTP)
        servidor.send_message(mensaje)
'''),

A("EXT-SEGURIDAD-01-NEG", "SEGURIDAD", "codigo_fuente", "notificaciones/cliente_correo.py", 0, "seg-01", '''\
"""Cliente de correo para los avisos de vencimiento de préstamos."""
import smtplib
from email.message import EmailMessage

SERVIDOR_SMTP = "smtp.biblioteca.local"
PUERTO_SMTP = 587
USUARIO_SMTP = "avisos@biblioteca.local"
CLAVE_SMTP = "Avisos#Biblio2026"


def enviar_aviso(destinatario, titulo_libro, fecha_limite):
    """Envía un aviso de vencimiento al usuario del préstamo."""
    mensaje = EmailMessage()
    mensaje["Subject"] = "Tu préstamo está por vencer"
    mensaje["To"] = destinatario
    mensaje.set_content(f"El libro '{titulo_libro}' debe devolverse el {fecha_limite}.")
    with smtplib.SMTP(SERVIDOR_SMTP, PUERTO_SMTP) as servidor:
        servidor.starttls()
        servidor.login(USUARIO_SMTP, CLAVE_SMTP)
        servidor.send_message(mensaje)
'''),

A("EXT-ADVC-SEGURIDAD-02-POS", "SEGURIDAD", "pipeline_ci", ".gitlab-ci.yml", 1, "seg-02", """\
stages:
  - build
  - deploy

construir_imagen:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"

desplegar:
  stage: deploy
  script:
    - ssh -i "$DEPLOY_SSH_KEY_FILE" deploy@app01 "./actualizar.sh $CI_COMMIT_SHORT_SHA"
  # DEPLOY_SSH_KEY_FILE y CI_REGISTRY_PASSWORD son variables protegidas y
  # enmascaradas definidas en la configuración del proyecto de GitLab.
""",
  adv="tipo_c", note="Todas las credenciales provienen de variables protegidas y enmascaradas de GitLab CI; no hay os.environ/getenv en el archivo, por lo que el regex predice violación."),

A("EXT-SEGURIDAD-02-NEG", "SEGURIDAD", "pipeline_ci", ".gitlab-ci.yml", 0, "seg-02", """\
stages:
  - build
  - deploy

construir_imagen:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u biblio_admin -p "Registro.Biblio.2026" registry.biblioteca.local
    - docker build -t registry.biblioteca.local/biblio:$CI_COMMIT_SHORT_SHA .
    - docker push registry.biblioteca.local/biblio:$CI_COMMIT_SHORT_SHA

desplegar:
  stage: deploy
  script:
    - sshpass -p "deploy2026" ssh deploy@app01 "./actualizar.sh $CI_COMMIT_SHORT_SHA"
"""),

A("EXT-ADVB-SEGURIDAD-03-NEG", "SEGURIDAD", "codigo_fuente", "reportes/almacenamiento.py", 0, "seg-03", '''\
"""Carga de reportes mensuales al almacenamiento de objetos."""
import os

import boto3

CLAVE_ACCESO = os.environ.get("AWS_ACCESS_KEY_ID", "AKIAQ3EXAMPLE7BIBLIO2")
CLAVE_SECRETA = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", "q9Xr2vL8mZt4Kp1Nw6Ys3Bc7Hd0Jf5Ge8Ua2Io4E"
)
CUBETA = os.environ.get("REPORTES_BUCKET", "biblio-reportes")


def subir_reporte(ruta_local, nombre):
    """Sube un reporte generado a la cubeta de reportes."""
    cliente = boto3.client(
        "s3", aws_access_key_id=CLAVE_ACCESO, aws_secret_access_key=CLAVE_SECRETA
    )
    cliente.upload_file(ruta_local, CUBETA, f"mensuales/{nombre}")
''',
  adv="tipo_b", note="Usa os.environ.get (activa el regex), pero los valores por defecto contienen una clave de acceso y una clave secreta reales en texto plano."),

A("EXT-SEGURIDAD-03-POS", "SEGURIDAD", "codigo_fuente", "config/base_datos.py", 1, "seg-03", '''\
"""Lectura de credenciales de base de datos desde archivos de secretos montados."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def leer_secreto(variable):
    """Lee el secreto desde el archivo indicado por la variable de entorno."""
    ruta = os.environ.get(variable)
    if not ruta:
        raise ImproperlyConfigured(f"Falta la variable {variable}.")
    return Path(ruta).read_text(encoding="utf-8").strip()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "biblio"),
        "USER": leer_secreto("DB_USER_FILE"),
        "PASSWORD": leer_secreto("DB_PASSWORD_FILE"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
'''),

A("EXT-ADVC-SEGURIDAD-04-POS", "SEGURIDAD", "documento_texto", "docs/operacion/despliegue_servidor.md", 1, "seg-04", """\
# Guía de despliegue en el servidor de la biblioteca

## Antes de empezar

Para desplegar necesitas acceso al servidor de aplicación y permiso de lectura en la bóveda de secretos del proyecto. Pide ambos accesos al responsable de infraestructura; no se comparten por correo ni por mensaje.

## Pasos

1. Entra al servidor con tu propia llave personal, no con cuentas compartidas.
2. Descarga la nueva versión desde el repositorio con la etiqueta indicada en la solicitud de cambio.
3. Las contraseñas de la base de datos y del correo se inyectan desde la bóveda al iniciar el servicio. No las copies en archivos de configuración ni en esta guía.
4. Reinicia el servicio y revisa que la página de inicio responda.

## Si algo falla

Revisa el registro del servicio. Si el error menciona credenciales, avisa al responsable de infraestructura para que las rote desde la bóveda.
""",
  adv="tipo_c", note="Documento operativo sin ningún secreto en texto plano y que prescribe el uso de una bóveda; no contiene os.environ/getenv."),

# ─────────────────────────── TRAZABILIDAD ───────────────────────────
A("EXT-TRAZABILIDAD-01-POS", "TRAZABILIDAD", "documento_texto", "docs/matriz_trazabilidad.md", 1, "traz-01", """\
# Matriz de trazabilidad — iteración 3

La siguiente tabla relaciona cada requerimiento con el código que lo implementa y con la prueba que lo verifica. Se actualiza al cierre de cada iteración.

| Requerimiento | Descripción | Implementación | Prueba |
|---|---|---|---|
| RF_05 | Registrar préstamo | prestamos/services.py | prestamos/tests.py::test_registrar_prestamo |
| RF_07 | Registrar devolución | devoluciones/views.py | devoluciones/tests.py::test_devolucion_a_tiempo |
| RF_08 | Calcular multa por retraso | multas/calculo.py | multas/tests.py::test_multa_tres_dias |
| US_04 | Consultar multas pendientes | multas/views.py | multas/tests.py::test_listado_pendientes |

Los requerimientos RF_06 y US_05 quedaron fuera de esta iteración por acuerdo con el cliente.
"""),

A("EXT-TRAZABILIDAD-01-NEG", "TRAZABILIDAD", "codigo_fuente", "devoluciones/views.py", 0, "traz-01", '''\
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from prestamos.models import Prestamo


def registrar_devolucion(request, prestamo_id):
    """Marca el préstamo como devuelto y libera el libro."""
    prestamo = get_object_or_404(Prestamo, pk=prestamo_id)
    prestamo.devuelto = True
    prestamo.fecha_devolucion_real = timezone.now().date()
    prestamo.save(update_fields=["devuelto", "fecha_devolucion_real"])

    libro = prestamo.libro
    libro.disponible = True
    libro.save(update_fields=["disponible"])

    dias_retraso = (prestamo.fecha_devolucion_real - prestamo.fecha_devolucion_esperada).days
    return JsonResponse({"devuelto": True, "dias_retraso": max(0, dias_retraso)})
'''),

A("EXT-ADVB-TRAZABILIDAD-02-NEG", "TRAZABILIDAD", "codigo_fuente", "reservas/views.py", 0, "traz-02", '''\
from django.http import JsonResponse
from reservas.models import Reserva


def cancelar_reserva(request, reserva_id):
    """
    ID Requerimiento: pendiente de asignar
    Caso de Prueba Asociado: por definir cuando exista el requerimiento
    """
    reserva = Reserva.objects.get(pk=reserva_id)
    reserva.activa = False
    reserva.save(update_fields=["activa"])
    return JsonResponse({"cancelada": True})
''',
  adv="tipo_b", note="Tiene las etiquetas 'ID Requerimiento' y 'Caso de Prueba Asociado' (activan el regex), pero ambos valores están pendientes: no referencia ningún requerimiento real."),

A("EXT-ADVC-TRAZABILIDAD-02-POS", "TRAZABILIDAD", "codigo_fuente", "reservas/servicios.py", 1, "traz-02", '''\
from django.utils import timezone
from reservas.models import Reserva

VIGENCIA_RESERVA_DIAS = 3


def expirar_reservas_vencidas():
    """
    Implementa REQ-FUN-014 (expiración automática de reservas no reclamadas).
    Deriva de la historia HISTORIA-031 del tablero del cliente.
    """
    limite = timezone.now() - timezone.timedelta(days=VIGENCIA_RESERVA_DIAS)
    return Reserva.objects.filter(activa=True, creada__lt=limite).update(activa=False)
''',
  adv="tipo_c", note="Trazabilidad explícita con el esquema REQ-FUN-014 / HISTORIA-031, que el regex (RF_/US_/ID Requerimiento) no reconoce."),

A("EXT-TRAZABILIDAD-03-NEG", "TRAZABILIDAD", "documento_texto", "docs/notas_version_2.1.md", 0, "traz-03", """\
# Notas de la versión 2.1

## Novedades

- Ahora se pueden renovar los préstamos desde la página del usuario.
- La pantalla de multas muestra el total pendiente en la parte superior.
- Se agregó la búsqueda por nombre de autor en el catálogo.

## Correcciones

- Ya no se duplica el préstamo cuando se presiona dos veces el botón "Prestar".
- El reporte mensual respeta los días feriados.

## Cambios internos

- Se actualizó Django y se limpiaron consultas lentas en el listado de préstamos.
"""),

A("EXT-ADVB-TRAZABILIDAD-04-NEG", "TRAZABILIDAD", "documento_texto", "docs/plantillas/plantilla_trazabilidad.md", 0, "traz-04", """\
# Plantilla de trazabilidad (no llenar aquí)

Copie esta plantilla en la carpeta de la iteración y sustituya los ejemplos por los identificadores reales del proyecto.

| Requerimiento | Implementación | Prueba |
|---|---|---|
| RF_00 (ejemplo, reemplazar) | ruta/al/modulo.py | ruta/a/la/prueba.py |
| US_00 (ejemplo, reemplazar) | ruta/al/modulo.py | ruta/a/la/prueba.py |

Instrucciones: cada fila debe apuntar a un requerimiento aprobado. Las filas de ejemplo se deben borrar antes de entregar el documento.
""",
  adv="tipo_b", note="Contiene RF_00 y US_00 (activan el regex), pero son marcadores de ejemplo de una plantilla vacía; no hay trazabilidad a requerimientos reales."),

# ─────────────────────────── PRUEBAS ───────────────────────────
A("EXT-PRUEBAS-01-POS", "PRUEBAS", "codigo_fuente", "devoluciones/tests.py", 1, "pru-01", '''\
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from catalogo.models import Libro
from prestamos.models import Prestamo


class DevolucionTests(TestCase):
    def test_devolucion_con_retraso(self):
        """
        Caso de Prueba: TC-DEV-002
        Requerimiento: RF_07 (registrar devolución)
        Pasos:
        1. Crear un préstamo vencido hace tres días.
        2. Enviar POST a /devoluciones/<id>/.
        Resultado Esperado: HTTP 200, préstamo devuelto y dias_retraso = 3.
        """
        usuario = User.objects.create(username="lector")
        libro = Libro.objects.create(titulo="Pedro Páramo", isbn="9786071600000")
        prestamo = Prestamo.objects.create(
            usuario=usuario, libro=libro,
            fecha_devolucion_esperada=date.today() - timedelta(days=3),
        )
        respuesta = self.client.post(f"/devoluciones/{prestamo.id}/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["dias_retraso"], 3)
        prestamo.refresh_from_db()
        self.assertTrue(prestamo.devuelto)
'''),

A("EXT-PRUEBAS-01-NEG", "PRUEBAS", "codigo_fuente", "devoluciones/tests.py", 0, "pru-01", '''\
from unittest import skip

from django.test import TestCase


class DevolucionTests(TestCase):
    @skip("arreglar después")
    def test_devolucion(self):
        pass

    @skip("falla en la computadora de Luis")
    def test_devolucion_tarde(self):
        pass
'''),

A("EXT-PRUEBAS-02-POS", "PRUEBAS", "documento_texto", "docs/pruebas/protocolo_multas.md", 1, "pru-02", """\
# Protocolo de pruebas — módulo de multas

| Caso de Prueba: | TC-MUL-001 |
|---|---|
| Requerimiento | RF_08 — Calcular multa por retraso |
| Entorno: | Servidor de integración, base de datos de prueba |

**Pasos:**
1. Registrar un préstamo con fecha límite 2026-03-01.
2. Registrar la devolución el 2026-03-04.
3. Consultar la multa generada para el préstamo.

**Resultado Esperado:** la multa es de 3 días por la tarifa diaria vigente y queda en estado pendiente.

| Caso de Prueba: | TC-MUL-002 |
|---|---|
| Requerimiento | RF_08 — Calcular multa por retraso |
| Entorno: | Servidor de integración, base de datos de prueba |

**Pasos:**
1. Registrar un préstamo con fecha límite 2026-03-01.
2. Registrar la devolución el 2026-02-28.

**Resultado Esperado:** no se genera ninguna multa para el préstamo.
"""),

A("EXT-PRUEBAS-02-NEG", "PRUEBAS", "documento_texto", "docs/pruebas/como_nos_fue.txt", 0, "pru-02", """\
Resumen de pruebas de esta semana

Probé el inicio de sesión con mi usuario y funciona bien. También hice un préstamo y una devolución y no marcó errores.

Lo de las multas no lo alcancé a probar porque la base de datos de pruebas estaba caída el jueves. Luis dice que a él sí le calculó bien, así que supongo que está bien.

La próxima semana intento probar los reportes.
"""),

A("EXT-ADVC-PRUEBAS-03-POS", "PRUEBAS", "codigo_fuente", "multas/test_calculo.py", 1, "pru-03", '''\
import pytest

from multas.calculo import calcular_multa

TARIFA_DIARIA = 5.0


@pytest.mark.parametrize(
    "dias_atraso, monto_correcto",
    [(0, 0.0), (1, 5.0), (3, 15.0)],
)
def test_tp_mul_004_monto_por_dias_de_atraso(dias_atraso, monto_correcto):
    """
    Escenario TP-MUL-004 — cubre la historia HU-12 (multas por devolución tardía).
    Dado un préstamo devuelto con `dias_atraso` días de atraso
    y una tarifa diaria de 5.0,
    cuando se calcula la multa,
    entonces el monto debe ser igual a `monto_correcto`.
    """
    assert calcular_multa(dias_atraso, TARIFA_DIARIA) == monto_correcto


def test_tp_mul_005_atraso_negativo_no_genera_multa():
    """
    Escenario TP-MUL-005 — cubre HU-12.
    Dado un libro devuelto antes de la fecha límite, cuando se calcula la multa,
    entonces el monto debe ser cero.
    """
    assert calcular_multa(-2, TARIFA_DIARIA) == 0.0
''',
  adv="tipo_c", note="Casos con identificador (TP-MUL-004/005), pasos Dado/cuando/entonces, resultado verificado con asserts reales y vínculo a HU-12, sin las palabras Caso de Prueba:, Pasos:, Entorno: ni Resultado Esperado."),

A("EXT-ADVB-PRUEBAS-03-NEG", "PRUEBAS", "documento_texto", "docs/pruebas/plantilla_caso.md", 0, "pru-03", """\
# Caso de prueba (plantilla)

Caso de Prueba: TC-___
Requerimiento: ______
Entorno: ______

Pasos:
1.
2.
3.

Resultado Esperado:

Resultado obtenido:

Observaciones: llenar esta plantilla por cada caso antes de la revisión de la iteración.
""",
  adv="tipo_b", note="Contiene todas las etiquetas del regex (Caso de Prueba:, Entorno:, Pasos:, Resultado Esperado) pero es una plantilla vacía sin ningún caso de prueba real."),

A("EXT-PRUEBAS-04-POS", "PRUEBAS", "codigo_fuente", "reservas/tests.py", 1, "pru-04", '''\
from django.contrib.auth.models import User
from django.test import TestCase

from catalogo.models import Libro
from reservas.models import Reserva


class ReservaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create(username="lectora")
        self.libro = Libro.objects.create(titulo="Rayuela", isbn="9788437604572")

    def test_reserva_libro_prestado(self):
        """
        Caso de Prueba: TC-RES-001
        Requerimiento: BVSE-REQ-002 (reservas anticipadas)
        Pasos:
        1. Marcar el libro como no disponible.
        2. Enviar POST a /reservas/ con el ISBN del libro.
        Resultado Esperado: HTTP 201 y una reserva activa para el usuario.
        """
        self.libro.disponible = False
        self.libro.save()
        self.client.force_login(self.usuario)
        respuesta = self.client.post("/reservas/", {"isbn": self.libro.isbn})
        self.assertEqual(respuesta.status_code, 201)
        self.assertTrue(
            Reserva.objects.filter(usuario=self.usuario, libro=self.libro, activa=True).exists()
        )
'''),
]
