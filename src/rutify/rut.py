"""
Clase RUT que representa un RUT chileno, 
compuesto por un número y un dígito verificador (DV).
"""

from __future__ import annotations

import re

from rutify.exceptions import InvalidRutError

from ._core import RutStyle, _split_raw, compute_dv

_MIN_NUMBER = 1_000_000
_MAX_NUMBER = 99_999_999



# Regular expression para validar el formato del RUT en 
# modo estricto (con guión y sin puntos).
STRICT_RE = re.compile(
    r"^\d{1,2}(\.\d{3}){0,2}-[\dKk]$"
    )


class Rut:
    """
    Clase que representa un RUT chileno, compuesto por un número 
    y un dígito verificador (DV).

    El RUT es un identificador único utilizado en Chile para personas 
    naturales y jurídicas.
    El número del RUT debe estar entre 1.000.000 y 99.999.999,
    y el dígito verificador se calcula a partir del número utilizando 
    un algoritmo específico.

    Uso básico:
        >>> from rutify import Rut
        >>> rut = Rut.parse("12.345.678-5")
        >>> print(rut)  # Salida: 12.345.678-5
        >>> print(rut.number)  # Salida: 12345678
        >>> print(rut.dv)  # Salida: '5'
        >>> print(rut.format(RutStyle.PLAIN))  # Salida: '123456785'

    """

    __slots__ = ("_number", "_dv")
    _number: int
    _dv: str

    def __init__(self, number: int, dv: str | None = None) -> None:
        """
        Crea una instancia de RUT a partir de un número y 
        un dígito verificador opcional.

        Args:
            number: El número del RUT, que debe estar entre 1.000.000
                    y 99.999.999.
            dv: El dígito verificador del RUT, que puede ser un 
            dígito (0-9) o 'K'.
            Si se proporciona, se validará contra el número.
            Si no se proporciona, se calculará automáticamente.
        Raises:
            ValueError: Si el número del RUT está fuera del 
            rango permitido o si el dígito verificador proporcionado 
            no coincide con el número.

        """
        if not (_MIN_NUMBER <= number <= _MAX_NUMBER):
            raise ValueError(
                f"El número del RUT debe estar entre {_MIN_NUMBER} y {_MAX_NUMBER}."
            )
        computed = compute_dv(number)
        if dv is not None:
            given = dv.upper()
            if given != computed:
                raise ValueError(
                    f"Dígito verificador incorrecto: se esperaba "
                    f"'{computed}' pero se recibió '{given}'."
                )
        object.__setattr__(self, "_number", number)
        object.__setattr__(self, "_dv", computed)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Los atributos de RUT son inmutables.")

    @classmethod
    def parse(cls, rut: str, *, strict: bool = False) -> Rut:
        """
        Parsea un RUT a partir de una cadena de texto, 
        validando su formato y dígito verificador.

        Args:
            rut: La cadena de texto que representa el RUT.
            strict: Si es True, se aplicará una validación 
            estricta del formato.

        Returns:
            Una instancia de RUT válida.

        Raises:
            InvalidRutError: Si el RUT no es válido.

        """
        try:
            if strict and not STRICT_RE.match(rut):
                raise InvalidRutError(
                    rut, "no cumple con el formato estricto " \
                    "dd.ddd.ddd-dv"
                )
            number, dv = _split_raw(rut)
            return cls(number, dv)
        except (InvalidRutError, ValueError) as e:
            raise InvalidRutError(rut, str(e)) from e

    @classmethod
    def from_number(cls, number: int) -> Rut:
        """
        Crea una instancia de RUT a partir de un número, 
        calculando automáticamente el dígito verificador.
        """
        return cls(number)

    @property
    def number(self) -> int:
        """
        Devuelve el número del RUT.
        """
        return self._number

    @property
    def dv(self) -> str:
        """
        Devuelve el dígito verificador del RUT.
        """
        return self._dv

    def format(self, style: RutStyle = RutStyle.DOTS) -> str:
        """
        Devuelve una representación formateada del RUT según 
        el estilo especificado.

        Args:
            style: El estilo de formato a utilizar, que 
              puede ser uno de los siguientes:
                - RutStyle.DOTS: Formato con puntos y guión 
                (ejemplo: "12.345.678-5").
                - RutStyle.DASH: Formato sin puntos pero 
                con guión (ejemplo: "12345678-5").
                - RutStyle.PLAIN: Formato sin puntos ni 
                guión (ejemplo: "123456785").
                - RutStyle.DOTS_NO_DASH: Formato con puntos 
                pero sin guión (ejemplo: "12.345.6785").

        """
        num_str = f"{self.number:,}".replace(",", ".")
        match style:
            case RutStyle.DOTS:
                return f"{num_str}-{self.dv}"
            case RutStyle.DASH:
                return f"{self.number}-{self.dv}"
            case RutStyle.PLAIN:
                return f"{self.number}{self.dv}"
            case RutStyle.DOTS_NO_DASH:
                return f"{num_str}{self.dv}"
            case _:
                valids = ", ".join(f"{s.value!r}" for s in RutStyle)
                raise ValueError(
                    f"estilo de formato desconocido: {style!r} \n"
                    f"(válidos: {valids})"
                )

    def __str__(self) -> str:
        """
        Devuelve una representación legible del RUT, 
        utilizando el formato con puntos y guión por defecto.
        """
        return self.format(RutStyle.DOTS)

    def __repr__(self) -> str:
        """
        Devuelve una representación oficial del RUT, 
        mostrando el número y el dígito verificador por separado.
        """
        return f"RUT(number={self.number}, dv={self.dv!r})"

    def __eq__(self, other: object) -> bool:
        """
        Compara dos instancias de RUT para determinar si son iguales.

        Args:
            other: La otra instancia de RUT a comparar.

        Returns:
            True si los RUT son iguales, False en caso contrario.

        """
        if isinstance(other, Rut):
            return self.number == other.number
        return NotImplemented

    def __hash__(self) -> int:
        """Devuelve un valor hash para la instancia de RUT, 
        basado en su número."""
        return hash(self.number)

    def __lt__(self, other: Rut) -> bool:
        """
        Compara dos instancias de RUT para determinar su orden.

        Args:
            other: La otra instancia de RUT a comparar.

        Returns:
            True si el RUT actual es menor que el RUT proporcionado,
              False en caso contrario.
        """
        if isinstance(other, Rut):
            return self.number < other.number
        return NotImplemented

    def __le__(self, other: Rut) -> bool:
        """
        Compara dos instancias de RUT para determinar su orden.

        Args:
            other: La otra instancia de RUT a comparar.

        Returns:
            True si el RUT actual es menor o igual que el RUT proporcionado,
              False en caso contrario.
        """
        if isinstance(other, Rut):
            return self.number <= other.number
        return NotImplemented

    def __gt__(self, other: Rut) -> bool:
        """
        Compara dos instancias de RUT para determinar su orden.

        Args:
            other: La otra instancia de RUT a comparar.

        Returns:
            True si el RUT actual es mayor que el RUT proporcionado,
              False en caso contrario.
        """

        if isinstance(other, Rut):
            return self.number > other.number
        return NotImplemented

    def __ge__(self, other: Rut) -> bool:
        """
        Compara dos instancias de RUT para determinar su orden.

        Args:
            other: La otra instancia de RUT a comparar.

        Returns:
            True si el RUT actual es mayor o igual que el RUT proporcionado,
              False en caso contrario.
        """
        if isinstance(other, Rut):
            return self.number >= other.number
        return NotImplemented
