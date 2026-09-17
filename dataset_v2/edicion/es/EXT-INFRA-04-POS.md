# Arquitectura de red de Biblio-VSE

El sistema se publica únicamente dentro de la red de la biblioteca. No existe ninguna regla que exponga los servicios a internet.

## Hosts permitidos

| Servicio | Nombre | Dirección |
|---|---|---|
| Aplicación web | prestamos.biblioteca.local | 10.20.0.15 |
| API | api.biblioteca.local | 10.20.0.16 |
| Base de datos | db.biblioteca.local | 10.20.1.5 |

## Reglas del firewall

| Regla | Origen | Puerto | Acción |
|---|---|---|---|
| 1 | 10.20.0.0/16 | 443 | Permitir |
| 2 | 10.20.0.15, 10.20.0.16 | 5432 | Permitir |
| 3 | Cualquier otro origen | Todos | Denegar |
