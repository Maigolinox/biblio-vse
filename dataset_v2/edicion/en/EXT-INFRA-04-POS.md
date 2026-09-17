# Biblio-VSE network architecture

The system is published only inside the library network. There is no rule that exposes the services to the internet.

## Allowed hosts

| Service | Name | Address |
|---|---|---|
| Web application | prestamos.biblioteca.local | 10.20.0.15 |
| API | api.biblioteca.local | 10.20.0.16 |
| Database | db.biblioteca.local | 10.20.1.5 |

## Firewall rules

| Rule | Source | Port | Action |
|---|---|---|---|
| 1 | 10.20.0.0/16 | 443 | Allow |
| 2 | 10.20.0.15, 10.20.0.16 | 5432 | Allow |
| 3 | Any other source | All | Deny |
