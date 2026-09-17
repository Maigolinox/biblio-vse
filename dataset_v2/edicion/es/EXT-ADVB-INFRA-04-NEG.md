# Política de red del servidor de aplicación

La política institucional indica que el sistema solo debe operar en entornos autorizados de la red interna (dominio biblioteca.local).

## Configuración vigente del firewall

| Regla | Origen | Puerto | Acción |
|---|---|---|---|
| 1 | 0.0.0.0/0 | 443 | Permitir |
| 2 | 0.0.0.0/0 | 22 | Permitir |
| 3 | 0.0.0.0/0 | 5432 | Permitir |

Nota: las reglas se abrieron a cualquier origen durante la migración de servidor y todavía no se han restringido.
