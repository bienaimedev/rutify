"""
Formateo de RUTs en diferentes estilos, incluyendo normalización y enmascaramiento.
"""

from __future__ import annotations

from rutify._core import RutStyle
from rutify.rut import Rut


def format_rut(rut: str, style: RutStyle) -> str:
    """
    Formatea un RUT según el estilo especificado.

    Args:
        rut: El RUT a formatear, que puede estar en cualquier formato válido.
        style: El estilo de formato a aplicar al RUT.

    Returns:
        El RUT formateado según el estilo especificado.

    Raises:
        ValueError: Si el RUT no es válido o si el estilo de formato no es reconocido.
    """
    return Rut.parse(rut).format(style)


def normalize(rut: str) -> str:
    """
    Normaliza un RUT a un formato estándar con puntos y guión (ejemplo: "12.345.678-5").

    Args:
        rut: El RUT a normalizar, que puede estar en cualquier formato válido.
    """
    return Rut.parse(rut).format(RutStyle.DOTS)


def mask(rut: str) -> str:
    """
    Enmascara un RUT, ocultando todos los dígitos
    excepto los últimos 4 caracteres (ejemplo: "XX.XXX.678-5").

    Args:
        rut: El RUT a enmascarar, que puede estar
        en cualquier formato válido.
    """
    parsed = Rut.parse(rut)
    num_str = f"{parsed.number:,}".replace(",", ".")
    return f"XX.XXX.{num_str[-3:]}-{parsed.dv}"
