# Matriz de trazabilidad — iteración 3

La siguiente tabla relaciona cada requerimiento con el código que lo implementa y con la prueba que lo verifica. Se actualiza al cierre de cada iteración.

| Requerimiento | Descripción | Implementación | Prueba |
|---|---|---|---|
| RF_05 | Registrar préstamo | prestamos/services.py | prestamos/tests.py::test_registrar_prestamo |
| RF_07 | Registrar devolución | devoluciones/views.py | devoluciones/tests.py::test_devolucion_a_tiempo |
| RF_08 | Calcular multa por retraso | multas/calculo.py | multas/tests.py::test_multa_tres_dias |
| US_04 | Consultar multas pendientes | multas/views.py | multas/tests.py::test_listado_pendientes |

Los requerimientos RF_06 y US_05 quedaron fuera de esta iteración por acuerdo con el cliente.
