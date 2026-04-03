"""
Excepciones para el módulo rutify.
"""

from __future__ import annotations


class RutifyError(Exception):
    """
    Excepción base para errores relacionados con RUT en el módulo rutify.
    """


class InvalidRutError(RutifyError):
    """Excepción lanzada cuando un RUT no puede ser parseado o tiene un DV inválido.

    Attributes:
        rut: El RUT original que falló la validación.
    """

    def __init__(self, rut: str, reason: str = "") -> None:
        self.rut = rut
        detail = f": {reason}" if reason else ""
        super().__init__(f"Rut inválido {rut!r}{detail}")


class InvalidRutNumberError(RutifyError):
    """Excepción lanzada cuando un valor numérico de RUT está fuera del rango válido."""
