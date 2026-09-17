# Guía de despliegue en el servidor de la biblioteca

## Antes de empezar

Para desplegar necesitas acceso al servidor de aplicación y permiso de lectura en la bóveda de secretos del proyecto. Pide ambos accesos al responsable de infraestructura; no se comparten por correo ni por mensaje.

## Pasos

1. Entra al servidor con tu propia llave personal, no con cuentas compartidas.
2. Descarga la nueva versión desde el repositorio con la etiqueta indicada en la solicitud de cambio.
3. Las contraseñas de la base de datos y del correo se inyectan desde la bóveda al iniciar el servicio. No las copies en archivos de configuración ni en esta guía.
4. Reinicia el servicio y revisa que la página de inicio responda.

## Si algo falla

Revisa el registro del servicio. Si el error menciona credenciales, avisa al responsable de infraestructura para que las rote desde la bóveda.
