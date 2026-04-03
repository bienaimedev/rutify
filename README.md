# Rutify

Librería Python para trabajar con RUT chilenos. Permite validar, formatear y generar RUTs de forma simple y eficiente.

## Instalación

```bash
pip install rutify
```

## Características

- Validación de RUTs completa
- Formateo en múltiples estilos
- Generación de RUTs aleatorios
- Sin dependencias externas
- Completamente tipado
- Soporte para Python 3.10+

## Uso

### Validación

```python
from rutify import is_valid, is_valid_number

# Validar RUT completo
is_valid("12.345.678-5")  # True
is_valid("12345678-5")    # True
is_valid("12.345.678-0")  # False

# Validar solo el número
is_valid_number(12345678)  # True
is_valid_number(999)       # False

# Validar múltiples RUTs
from rutify import validate_many
validate_many(["12.345.678-5", "98.765.432-1"])
# [True, True]
```

### Formateo

```python
from rutify import format_rut, normalize, mask, Rut, RutStyle

# Diferentes estilos de formato
rut = Rut.parse("12345678-5")

rut.format(RutStyle.DOTS)   # "12.345.678-5"
rut.format(RutStyle.HYPHEN)  # "12345678-5"
rut.format(RutStyle.PLAIN)   # "123456785"

# Normalizar a formato estándar
normalize("123456785")  # "12.345.678-5"

# Enmascarar RUT (ocultar dígitos)
mask("12.345.678-5")  # "XX.XXX.678-5"
```

### Generación

```python
from rutify import generate, generate_many

# Generar un RUT aleatorio
rut = generate()
print(rut)  # 15.234.567-8

# Generar múltiples RUTs
ruts = generate_many(5, unique=True)

# Generación segura (criptográficamente)
rut = generate(secure=True)
```

### Clase Rut

```python
from rutify import Rut

# Crear desde string
rut = Rut.parse("12.345.678-5")

# Crear desde número (calcula el DV automáticamente)
rut = Rut.from_number(12345678)

# Acceder a componentes
print(rut.number)  # 12345678
print(rut.dv)      # "5"

# Formatear
print(rut.format(RutStyle.DOTS))  # "12.345.678-5"

# Modo estricto (valida formato exacto)
Rut.parse("12.345.678-5", strict=True)  # OK
Rut.parse("12345678-5", strict=True)    # InvalidRutError
```

## API

### Validación

- `is_valid(rut: str) -> bool`: Valida un RUT completo
- `is_valid_number(number: int) -> bool`: Valida solo el número del RUT
- `validate_many(ruts: list[str]) -> list[bool]`: Valida múltiples RUTs

### Formateo

- `format_rut(rut: str, style: RutStyle) -> str`: Formatea según estilo
- `normalize(rut: str) -> str`: Normaliza a formato estándar con puntos
- `mask(rut: str) -> str`: Enmascara el RUT

### Generación

- `generate(*, secure: bool = False) -> Rut`: Genera un RUT aleatorio
- `generate_many(count: int, *, unique: bool = True, secure: bool = False) -> list[Rut]`: Genera múltiples RUTs

### Clase Rut

- `Rut.parse(rut: str, *, strict: bool = False) -> Rut`: Parsea desde string
- `Rut.from_number(number: int) -> Rut`: Crea desde número
- `rut.number`: Obtiene el número
- `rut.dv`: Obtiene el dígito verificador
- `rut.format(style: RutStyle) -> str`: Formatea el RUT

### Estilos disponibles

- `RutStyle.DOTS`: Con puntos y guión (12.345.678-5)
- `RutStyle.HYPHEN`: Sin puntos, con guión (12345678-5)
- `RutStyle.PLAIN`: Sin formato (123456785)

### Excepciones

- `RutifyError`: Excepción base
- `InvalidRutError`: RUT inválido
- `InvalidRutNumberError`: Número de RUT inválido

## Rangos válidos

Los RUTs válidos deben tener un número entre 1.000.000 y 99.999.999.

## Licencia

MIT
