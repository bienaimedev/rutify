"""
Core de computación de RUT, incluyendo el cálculo 
del dígito verificador y el parseo de RUT sin formato.
"""

from __future__ import annotations

from enum import Enum

_SERIES = [2, 3, 4, 5, 6, 7]


def compute_dv(number: int) -> str:
    """
    Calcula el dígito verificador para un número de RUT dado.

    Utiliza el algoritmo de módulo 11, donde los dígitos
    del número se multiplican por una secuencia de 
    factores (2, 3, 4, 5, 6, 7)
    que se repite. La suma de estos productos se divide por 11,
    y el resto se utiliza para determinar el dígito verificador.

    Args:
        number: El número de RUT para el cual se desea calcular 
        el dígito verificador.

    Returns:
        El dígito verificador correspondiente al número de RUT dado, 
        que puede ser un dígito (0-9) o 'K'.

    Raises:
        ValueError: Si el número de RUT es negativo.
    """
    if number < 0:
        raise ValueError("el número de RUT no puede ser negativo")
    total = 0
    for i, digit in enumerate(reversed(str(number))):
        factor = _SERIES[i % len(_SERIES)]
        total += int(digit) * factor
    remainder = total % 11
    if remainder == 0:
        return "0"
    elif remainder == 1:
        return "K"
    else:
        return str(11 - remainder)


def _split_raw(rut: str) -> tuple[int, str]:
    """
    Parsea el RUT sin formato, devolviendo el número 
    y el dígito verificador por separado.

    Formatos aceptados: ``12345678-9``, ``123456789`` 
    o ``12.345.678-9``, etc.

    Args:
        rut: El RUT sin formato.

    Returns:
        A ``(número, dv)`` tupla dónde *dv* está en mayúscula.

    Raises:
        ValueError: Si el RUT no es válido.
    """
    cleaned = rut.strip().replace(".", "").replace(" ", "")
    if "-" in cleaned:
        parts = cleaned.split("-")
        if len(parts) != 2:
            raise ValueError(f"formato de RUT inválido: {rut!r}")
        num_str, dv = parts
    elif len(cleaned) >= 2:
        num_str, dv = cleaned[:-1], cleaned[-1]
    else:
        raise ValueError(f"formato de RUT inválido: {rut!r}")

    if not num_str.isdigit():
        raise ValueError(f"número de RUT inválido: {num_str!r}")
    if not (dv.isdigit() or dv.upper() == "K"):
        raise ValueError(f"dígito verificador de RUT inválido: {dv!r}")
    return int(num_str), dv.upper()


class RutStyle(str, Enum):
    DOTS = "dots"
    DASH = "dash"
    PLAIN = "plain"
    DOTS_NO_DASH = "dots_no_dash"
