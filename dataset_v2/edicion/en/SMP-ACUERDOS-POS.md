# System Design Meeting Minutes — BVSE-ACTA-002
**Code:** BVSE-ACTA-002
**Version:** V1.0.0
**Effective Date:** 2026-03-10
**Status:** Approved

## General Meeting Information

- **Meeting Date:** 2026-03-10
- **Location:** Biblio-VSE project meeting room
- **Coordination Owner:** Project Coordinator

## Project Participants

| Name | Role | Attendance |
|---|---|---|
| Ana García | Lead Developer | Present |
| Luis Martínez | Database Owner | Present |
| María Torres | Quality Owner | Present |
| Pedro Ramírez | Infrastructure Owner | Present |

## Formalized Agreements

**Agreement 01:** The team will migrate the function-based views to Django's Class-Based Views pattern.
The goal is to improve the maintainability and extensibility of the module.
The pattern separates business logic from the presentation layer.
- **Responsible:** Ana García, Lead Developer
- **Implementation Date:** 2026-03-20
- **Status:** In Progress

**Agreement 02:** Luis Martínez will add optimization indexes to the loans and users tables.
This improvement will reduce the response time of system queries.
The indexes will be applied to the date and record status columns.
- **Responsible:** Luis Martínez, Database Owner
- **Implementation Date:** 2026-03-17
- **Status:** Pending

**Agreement 03:** María Torres will validate the authentication module before deployment.
The coverage will include the login and user session management flows.
The result will be documented in the system quality report.
- **Responsible:** María Torres, Quality Owner
- **Validation Date:** 2026-03-15
- **Status:** In Progress

## Approval of the Minutes

**Authorized by:** Biblio-VSE System Project Director
**Document Status:** Approved
