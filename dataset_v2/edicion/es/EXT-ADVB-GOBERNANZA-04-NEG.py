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
