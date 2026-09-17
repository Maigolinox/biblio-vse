## Lista de Cotejo de Calidad del Sistema — BVSE-QA-MR

### Verificación de Estilo y Formato del Código del Sistema

- [ ] El código del sistema pasa el proceso de verificación con la herramienta de análisis estático flake8 sin errores ni advertencias de estilo de código.
- [ ] El código del sistema cumple con las convenciones de nomenclatura del proyecto: variables del sistema en snake_case, clases del sistema en PascalCase, constantes del sistema en MAYÚSCULAS_CON_GUIÓN_BAJO.
- [ ] El código del sistema no contiene identificadores mágicos (magic numbers) sin documentar en ninguna función ni clase del módulo de implementación del sistema.
- [ ] El código del sistema tiene indentación correcta de cuatro espacios por nivel de anidamiento en todas las funciones y clases del módulo del sistema de biblioteca.
- [ ] Los imports del módulo del sistema están organizados según las convenciones de estilo establecidas en la guía del proyecto: primero la biblioteca estándar del sistema, luego dependencias externas del sistema, y finalmente módulos del propio sistema de biblioteca.

### Verificación de Documentación del Sistema

- [ ] El código del sistema incluye docstrings en todas las funciones y clases públicas del módulo de implementación de acuerdo con el estándar de documentación del proyecto del sistema.
- [ ] El código del sistema incluye referencias explícitas a los identificadores de requerimientos del sistema (RF_XX o US_XX) en los comentarios de las funciones que implementan lógica de negocio del sistema.
- [ ] Se incluyeron pruebas unitarias del sistema con una cobertura mínima del 80% para todas las funciones y clases del módulo del sistema de biblioteca.
- [ ] Los mensajes de commit del proceso de integración del sistema siguen el formato convencional establecido en la guía de contribución del proyecto del sistema.

### Verificación de Seguridad del Sistema

- [ ] El código del sistema no contiene credenciales, tokens de autenticación ni contraseñas del sistema en texto plano (hardcoded) en ninguna parte del módulo de implementación.
- [ ] El código del sistema utiliza variables de entorno del sistema operativo para la gestión de toda configuración sensible del sistema de biblioteca.
- [ ] El proceso de validación de entradas del sistema incluye verificación de tipos, longitudes y formatos esperados para todos los parámetros de entrada del sistema.
