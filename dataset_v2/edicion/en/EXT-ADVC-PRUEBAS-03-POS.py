import pytest

from fines.calculation import calculate_fine

DAILY_RATE = 5.0


@pytest.mark.parametrize(
    "days_overdue, correct_amount",
    [(0, 0.0), (1, 5.0), (3, 15.0)],
)
def test_tp_mul_004_amount_per_day_overdue(days_overdue, correct_amount):
    """
    Scenario TP-MUL-004 — covers story HU-12 (fines for late returns).
    Given a loan returned `days_overdue` days after its due date
    and a daily rate of 5.0,
    when the fine is calculated,
    then the amount must equal `correct_amount`.
    """
    assert calculate_fine(days_overdue, DAILY_RATE) == correct_amount


def test_tp_mul_005_negative_delay_generates_no_fine():
    """
    Scenario TP-MUL-005 — covers HU-12.
    Given a book returned before its due date, when the fine is calculated,
    then the amount must be zero.
    """
    assert calculate_fine(-2, DAILY_RATE) == 0.0
