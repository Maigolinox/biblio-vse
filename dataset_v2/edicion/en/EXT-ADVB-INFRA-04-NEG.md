# Network policy of the application server

The institutional policy states that the system must only operate in authorized environments of the private network (biblioteca.local domain).

## Current firewall configuration

| Rule | Source | Port | Action |
|---|---|---|---|
| 1 | 0.0.0.0/0 | 443 | Allow |
| 2 | 0.0.0.0/0 | 22 | Allow |
| 3 | 0.0.0.0/0 | 5432 | Allow |

Note: the rules were opened to any source during the server migration and have not been restricted yet.
