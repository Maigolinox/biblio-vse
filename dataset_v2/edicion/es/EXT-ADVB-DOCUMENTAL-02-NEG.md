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
