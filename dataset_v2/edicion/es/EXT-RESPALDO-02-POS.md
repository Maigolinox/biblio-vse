# Procedimiento de respaldo y recuperación de la base de datos

## Tipo y periodicidad

- Respaldo completo: cada domingo a las 02:00 con pg_dump en formato personalizado.
- Respaldo incremental: todos los días a las 02:00 mediante el archivado continuo de los registros WAL.

## Ubicación

Los archivos se guardan en la cubeta biblio-respaldos, en una región distinta a la del servidor de producción. Se conservan cuatro respaldos completos y los incrementales de los últimos 28 días.

## Recuperación

1. Detener el servicio de la aplicación.
2. Descargar el último respaldo completo y los archivos WAL posteriores.
3. Ejecutar pg_restore sobre una base de datos vacía y aplicar los WAL hasta la hora deseada.
4. Verificar el número de préstamos del día anterior y reiniciar el servicio.

## Prueba de recuperación

El primer lunes de cada mes el responsable de infraestructura restaura el respaldo en el servidor de pruebas y anota el resultado en la bitácora de operación.
