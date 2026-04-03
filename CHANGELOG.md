# Changelog

Todos los cambios importantes del proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-02

Primera versión pública de rutify, una biblioteca Python para trabajar con RUT chilenos.

### Agregado

- Funciones de validación: `is_valid()`, `is_valid_number()` y `validate_many()`
- Funciones de formateo: `format_rut()`, `normalize()` y `mask()` con soporte para múltiples estilos
- Funciones de generación: `generate()` y `generate_many()` para crear RUTs válidos aleatorios
- Clase `Rut` inmutable con métodos de validación, formateo y comparación
- Enumeración `RutStyle` para estilos de formato consistentes
- Excepciones personalizadas: `InvalidRutError`, `InvalidRutNumberError` e `InvalidRutDVError`
- Soporte completo de tipado estático con marcador `py.typed`
- Suite de pruebas con 91 tests unitarios

### Notas técnicas

- Sin dependencias en tiempo de ejecución
- Compatible con Python 3.10+
- Código completamente tipado y validado con mypy
- Integración continua en múltiples versiones de Python

[0.1.0]: https://github.com/bienaimedev/rutify/releases/tag/v0.1.0
