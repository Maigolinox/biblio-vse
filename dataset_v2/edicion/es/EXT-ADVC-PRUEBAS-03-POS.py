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
