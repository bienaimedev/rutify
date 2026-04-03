"""
Módulo para generar RUTs chilenos aleatorios.
"""

import random
import secrets

from rutify.rut import _MAX_NUMBER, _MIN_NUMBER, Rut


def generate(*, secure: bool = False) -> "Rut":
    """
    Genera un RUT aleatorio válido.

    Args:
        secure: Si es True, se utilizará el módulo secrets
        para generar un número aleatorio criptográficamente seguro.
        Si es False, se utilizará el módulo random,
        que es más rápido pero menos seguro.
    """
    number = (
        secrets.randbelow(_MAX_NUMBER - _MIN_NUMBER + 1) + _MIN_NUMBER
        if secure
        else random.randint(_MIN_NUMBER, _MAX_NUMBER)
    )
    return Rut.from_number(number)


def generate_many(
    count: int, *, unique: bool = True, secure: bool = False
) -> list["Rut"]:
    """
    Genera una lista de RUTs aleatorios válidos.

    Args:
        count: La cantidad de RUTs a generar.
        unique: Si es True, se garantiza que todos los RUTs generados
        sean únicos.
        secure: Si es True, se utilizará el módulo secrets
        para generar números aleatorios criptográficamente seguros.
        Si es False, se utilizará el módulo random,
        que es más rápido pero menos seguro.

    Returns:
        Una lista de instancias de RUT generados aleatoriamente.
    """
    if count < 1:
        raise ValueError("La cantidad debe ser un entero positivo")

    if not unique:
        return [generate(secure=secure) for _ in range(count)]

    seen: set[int] = set()
    result: list[int] = []
    while len(result) < count:
        rut = generate(secure=secure)
        if rut.number not in seen:
            seen.add(rut.number)
            result.append(rut.number)
    return [Rut.from_number(num) for num in result]
