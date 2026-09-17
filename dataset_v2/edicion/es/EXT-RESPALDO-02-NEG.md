# Cómo actualizar el sistema a una nueva versión

1. Avisar al personal de la biblioteca que el sistema estará detenido unos minutos.
2. Entrar al servidor y descargar la nueva versión del repositorio.
3. Instalar las dependencias nuevas, si las hay.
4. Aplicar las migraciones de la base de datos directamente sobre producción.
5. Reiniciar el servicio y revisar que la página de préstamos cargue.

Si algo sale mal después de migrar, se puede intentar regresar a la versión anterior del código. Los datos que ya se hayan modificado tendrán que corregirse a mano.
