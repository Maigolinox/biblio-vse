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
