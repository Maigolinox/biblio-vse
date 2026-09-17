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
