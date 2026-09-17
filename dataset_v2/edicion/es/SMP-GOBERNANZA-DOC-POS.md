# Especificación de Requerimientos del Sistema — BVSE-REQ-002
**Código:** BVSE-REQ-002
**Versión:** V1.0.0
**Fecha de Vigencia:** 2026-03-12
**Estado:** Aprobado
**Firma Digital (Hash SHA-256):** 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
**Autoriza:** Director de Biblioteca — Sistema Biblio-VSE
**Responsable de Revisión:** Coordinador Técnico del Proyecto

## Descripción del Requerimiento del Sistema

El requerimiento funcional BVSE-REQ-002 especifica el proceso de implementación del módulo de gestión de reservas del sistema de biblioteca. El proceso de reserva del sistema permite a los usuarios registrados del sistema realizar la reserva anticipada de libros disponibles en el catálogo del sistema de biblioteca antes de su préstamo formal en el sistema.

El sistema de reservas debe implementar el proceso de validación de disponibilidad del libro en el catálogo del sistema antes de registrar la reserva del usuario en el sistema de base de datos. El proceso de validación del sistema debe verificar que el usuario registrado no tenga préstamos vencidos ni multas pendientes de pago en el sistema de administración de la biblioteca antes de autorizar la reserva del sistema.

## Criterios de Aceptación del Sistema

El proceso de implementación del módulo de reservas del sistema debe satisfacer los siguientes criterios de aceptación establecidos por el responsable técnico del proyecto del sistema:

1. El sistema debe procesar la solicitud de reserva del usuario registrado en un tiempo de respuesta máximo de dos segundos de procesamiento del sistema de biblioteca.
2. El proceso de notificación del sistema debe enviar una confirmación de reserva al correo electrónico registrado del usuario dentro de los cinco minutos posteriores al registro de la reserva en el sistema.
3. El sistema de reservas debe cancelar automáticamente las reservas del usuario registrado que no sean reclamadas dentro del período de vigencia de la reserva establecido en la configuración del sistema de biblioteca.

## Implementación del Requerimiento del Sistema

La implementación del módulo de gestión de reservas del sistema sigue las especificaciones de gobernanza del proceso y los controles de aprobación definidos en el presente documento de requerimientos del sistema de biblioteca.
