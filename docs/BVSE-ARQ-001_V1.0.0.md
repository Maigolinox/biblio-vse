# Documento de Arquitectura del Sistema
**Código:** BVSE-ARQ-001
**Versión:** V1.0.0
**Fecha de Vigencia:** 2026-03-16

## 1. Patrón Arquitectónico del Sistema

El sistema Biblio-VSE implementa el patrón arquitectónico MVT (Modelo-Vista-Template) proporcionado por el framework de desarrollo web Django. Este patrón arquitectónico garantiza la separación de responsabilidades entre la lógica de negocio del sistema, la capa de presentación de datos del sistema y el módulo de acceso a la base de datos del sistema. La implementación del patrón arquitectónico MVT en el sistema permite que cada componente del sistema pueda ser desarrollado, verificado y mantenido de forma independiente sin afectar el funcionamiento de los demás componentes del sistema de biblioteca.

## 2. Componentes del Sistema

El sistema está compuesto por los siguientes módulos principales de implementación: el módulo de autenticación y autorización de usuarios del sistema, el módulo de gestión del catálogo de libros disponibles en el sistema, el módulo de administración de préstamos y devoluciones del sistema, y el módulo de generación de reportes del sistema de biblioteca.

El módulo de autenticación del sistema implementa el proceso de verificación de credenciales de usuario mediante el sistema de autenticación integrado del framework Django. El proceso de autorización del sistema determina los permisos de acceso de cada usuario en función del rol asignado en el sistema de administración de la biblioteca.

## 3. Base de Datos del Sistema

El sistema utiliza PostgreSQL como sistema gestor de base de datos para el almacenamiento persistente de la información del sistema de biblioteca. La estructura de la base de datos del sistema incluye las entidades principales de implementación: Usuario, Libro, Préstamo, Devolución y Multa. Las relaciones entre las entidades del sistema garantizan la integridad referencial de los datos almacenados en el sistema de administración de la biblioteca.

## 4. Proceso de Despliegue del Sistema

El proceso de despliegue del sistema se realiza mediante la plataforma de integración y despliegue continuo GitLab CI/CD. Cada nueva versión del sistema pasa por un proceso de validación automatizada antes de ser desplegada al entorno de producción del sistema. El proceso de despliegue del sistema incluye la ejecución de pruebas unitarias del sistema, la verificación de cobertura de código y la validación de la configuración del sistema de biblioteca.
