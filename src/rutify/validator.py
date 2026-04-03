"""
Módulo de validación para RUT chilenos.
"""

from __future__ import annotations

from rutify._core import _split_raw, compute_dv
from rutify.rut import _MAX_NUMBER, _MIN_NUMBER


def is_valid(rut: str) -> bool:
    """
    Valida un RUT chileno.

    Args:
        rut (str): RUT a validar.

    Returns:
        bool: True si el RUT es válido, False en caso contrario.
    """
    try:
        number, dv = _split_raw(rut)
    except (ValueError, AttributeError):
        return False
    if not (_MIN_NUMBER <= number <= _MAX_NUMBER):
        return False
    return compute_dv(number) == dv.upper()


def is_valid_number(number: int) -> bool:
    """
    Valida un número de RUT, sin considerar el dígito verificador.

    Args:
        number (int): Número de RUT a validar.
    Returns:
        bool: True si el número de RUT es válido, False en caso contrario.
    """
    if not isinstance(number, int):
        return False
    return _MIN_NUMBER <= number <= _MAX_NUMBER


def validate_many(ruts: list[str]) -> list[bool]:
    """
    Valida una lista de RUTs, devolviendo una lista de booleanos
    que indican la validez de cada RUT.

    Args:
        ruts: Lista de RUTs a validar.
    Returns:
        Lista de booleanos donde cada elemento es True si el RUT
        correspondiente es válido, o False en caso contrario.
    """
    return [is_valid(rut) for rut in ruts]
