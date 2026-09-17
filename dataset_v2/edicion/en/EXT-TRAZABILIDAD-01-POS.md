# Traceability matrix — iteration 3

The following table links each requirement with the code that implements it and the test that verifies it. It is updated at the end of each iteration.

| Requirement | Description | Implementation | Test |
|---|---|---|---|
| RF_05 | Register loan | loans/services.py | loans/tests.py::test_register_loan |
| RF_07 | Register return | returns/views.py | returns/tests.py::test_on_time_return |
| RF_08 | Calculate late fine | fines/calculation.py | fines/tests.py::test_three_day_fine |
| US_04 | Look up pending fines | fines/views.py | fines/tests.py::test_pending_list |

Requirements RF_06 and US_05 were left out of this iteration by agreement with the client.
