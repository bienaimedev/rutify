"""
Tests unitarios para rutify.
"""

import pytest

from rutify import (
    InvalidRutError,
    InvalidRutNumberError,
    Rut,
    RutifyError,
    RutStyle,
    format_rut,
    generate,
    generate_many,
    is_valid,
    is_valid_number,
    mask,
    normalize,
    validate_many,
)
from rutify._core import _split_raw, compute_dv


class TestComputeDv:
    """Tests para la función compute_dv."""

    def test_compute_dv_basic(self):
        """
        Verifica el cálculo correcto del dígito verificador 
        para números comunes.
        """
        assert compute_dv(12345678) == "5"
        assert compute_dv(11111111) == "1"

    def test_compute_dv_returns_k(self):
        """
        Verifica que el dígito verificador retorne 'K' 
        cuando corresponde.
        """
        assert compute_dv(1000005) == "K"

    def test_compute_dv_returns_zero(self):
        """Verifica que el dígito verificador retorne '0' cuando corresponde."""
        assert compute_dv(22222222) == "2"
        assert compute_dv(1000013) == "0"

    def test_compute_dv_negative_raises(self):
        """Verifica que se lance ValueError con números negativos."""
        with pytest.raises(ValueError, match="negativo"):
            compute_dv(-1)

    def test_compute_dv_known_values(self):
        """Verifica el cálculo con valores reales conocidos."""
        assert compute_dv(11111111) == "1"
        assert compute_dv(1000005) == "K"


class TestSplitRaw:
    """Tests para la función _split_raw."""

    def test_split_with_hyphen(self):
        """Verifica el parseo de RUT con formato de guión."""
        assert _split_raw("12345678-5") == (12345678, "5")

    def test_split_with_dots_and_hyphen(self):
        """Verifica el parseo de RUT con formato completo (puntos y guión)."""
        assert _split_raw("12.345.678-5") == (12345678, "5")

    def test_split_plain_format(self):
        """Verifica el parseo de RUT en formato plano sin separadores."""
        assert _split_raw("123456785") == (12345678, "5")

    def test_split_with_k_lowercase(self):
        """Verifica que 'k' minúscula se convierta a mayúscula."""
        assert _split_raw("1000005-k") == (1000005, "K")

    def test_split_with_k_uppercase(self):
        """Verifica el parseo correcto de 'K' mayúscula."""
        assert _split_raw("1000005-K") == (1000005, "K")

    def test_split_with_spaces(self):
        """Verifica que los espacios al inicio y final sean ignorados."""
        assert _split_raw("  12.345.678-5  ") == (12345678, "5")

    def test_split_invalid_format_multiple_hyphens(self):
        """Verifica que se rechacen formatos con múltiples guiones."""
        with pytest.raises(ValueError, match="formato de RUT inválido"):
            _split_raw("12-345-678-5")

    def test_split_invalid_number(self):
        """Verifica que se rechacen números con caracteres no numéricos."""
        with pytest.raises(ValueError, match="número de RUT inválido"):
            _split_raw("abc12345-5")

    def test_split_invalid_dv(self):
        """Verifica que se rechacen dígitos verificadores inválidos."""
        with pytest.raises(ValueError, match="dígito verificador de RUT inválido"):
            _split_raw("12345678-X")

    def test_split_too_short(self):
        """Verifica que se rechacen RUTs demasiado cortos."""
        with pytest.raises(ValueError, match="formato de RUT inválido"):
            _split_raw("1")


class TestRutInit:
    """Tests para el constructor de Rut."""

    def test_init_with_number_only(self):
        """
        Verifica la creación de RUT solo con número 
        (DV se calcula automáticamente)."""
        rut = Rut(12345678)
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_init_with_correct_dv(self):
        """Verifica la creación de RUT con número y DV correcto."""
        rut = Rut(12345678, "5")
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_init_with_incorrect_dv(self):
        """Verifica que se lance error con DV incorrecto."""
        with pytest.raises(ValueError, match="Dígito verificador incorrecto"):
            Rut(12345678, "9")

    def test_init_with_k_lowercase(self):
        """Verifica que 'k' minúscula se normalice a mayúscula."""
        rut = Rut(1000005, "k")
        assert rut.dv == "K"

    def test_init_number_too_small(self):
        """Verifica que se rechacen números menores al mínimo permitido."""
        with pytest.raises(ValueError, match="debe estar entre"):
            Rut(999999)

    def test_init_number_too_large(self):
        """Verifica que se rechacen números mayores al máximo permitido."""
        with pytest.raises(ValueError, match="debe estar entre"):
            Rut(100000000)

    def test_init_min_valid_number(self):
        """Verifica que se acepte el número mínimo válido."""
        rut = Rut(1000000)
        assert rut.number == 1000000

    def test_init_max_valid_number(self):
        """Verifica que se acepte el número máximo válido."""
        rut = Rut(99999999)
        assert rut.number == 99999999


class TestRutParse:
    """Tests para el método parse de Rut."""

    def test_parse_with_dots_and_hyphen(self):
        """Verifica el parseo de RUT con formato completo."""
        rut = Rut.parse("12.345.678-5")
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_parse_with_hyphen_only(self):
        """Verifica el parseo de RUT con solo guión."""
        rut = Rut.parse("12345678-5")
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_parse_plain_format(self):
        """Verifica el parseo de RUT en formato plano."""
        rut = Rut.parse("123456785")
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_parse_strict_mode_valid(self):
        """Verifica que el modo estricto acepte formato correcto."""
        rut = Rut.parse("12.345.678-5", strict=True)
        assert rut.number == 12345678

    def test_parse_strict_mode_invalid_no_dots(self):
        """Verifica que el modo estricto rechace formato sin puntos."""
        with pytest.raises(InvalidRutError):
            Rut.parse("12345678-5", strict=True)

    def test_parse_strict_mode_invalid_plain(self):
        """Verifica que el modo estricto rechace formato plano."""
        with pytest.raises(InvalidRutError):
            Rut.parse("123456785", strict=True)

    def test_parse_invalid_rut(self):
        """Verifica que se rechace RUT con DV incorrecto."""
        with pytest.raises(InvalidRutError):
            Rut.parse("12.345.678-9")

    def test_parse_invalid_format(self):
        """Verifica que se rechace formato completamente inválido."""
        with pytest.raises(InvalidRutError):
            Rut.parse("invalid")


class TestRutFromNumber:
    """Tests para el método from_number de Rut."""

    def test_from_number(self):
        """Verifica la creación de RUT desde número."""
        rut = Rut.from_number(12345678)
        assert rut.number == 12345678
        assert rut.dv == "5"

    def test_from_number_with_k(self):
        """Verifica que from_number calcule correctamente DV 'K'."""
        rut = Rut.from_number(1000005)
        assert rut.dv == "K"


class TestRutFormat:
    """Tests para el método format de Rut."""

    def test_format_dots(self):
        """Verifica formato con puntos y guión."""
        rut = Rut(12345678)
        assert rut.format(RutStyle.DOTS) == "12.345.678-5"

    def test_format_dash(self):
        """Verifica formato con solo guión."""
        rut = Rut(12345678)
        assert rut.format(RutStyle.DASH) == "12345678-5"

    def test_format_plain(self):
        """Verifica formato plano sin separadores."""
        rut = Rut(12345678)
        assert rut.format(RutStyle.PLAIN) == "123456785"

    def test_format_dots_no_dash(self):
        """Verifica formato con puntos pero sin guión."""
        rut = Rut(12345678)
        assert rut.format(RutStyle.DOTS_NO_DASH) == "12.345.6785"

    def test_format_with_k(self):
        """Verifica formato correcto cuando DV es 'K'."""
        rut = Rut(1000005)
        assert rut.format(RutStyle.DOTS) == "1.000.005-K"

    def test_format_default(self):
        """Verifica que el formato por defecto sea DOTS."""
        rut = Rut(12345678)
        assert rut.format() == "12.345.678-5"


class TestRutImmutability:
    """Tests para verificar la inmutabilidad de Rut."""

    def test_cannot_set_attribute(self):
        """Verifica que no se puedan modificar atributos de RUT."""
        rut = Rut(12345678)
        with pytest.raises(AttributeError, match="inmutables"):
            rut.number = 99999999


class TestRutStringRepresentation:
    """Tests para __str__ y __repr__ de Rut."""

    def test_str(self):
        """Verifica la representación string de RUT."""
        rut = Rut(12345678)
        assert str(rut) == "12.345.678-5"

    def test_repr(self):
        """Verifica la representación oficial de RUT."""
        rut = Rut(12345678)
        assert repr(rut) == "RUT(number=12345678, dv='5')"


class TestRutEquality:
    """Tests para comparaciones de igualdad de Rut."""

    def test_equal_ruts(self):
        """Verifica que RUTs con el mismo número sean iguales."""
        rut1 = Rut(12345678)
        rut2 = Rut.parse("12.345.678-5")
        assert rut1 == rut2

    def test_different_ruts(self):
        """Verifica que RUTs con diferente número no sean iguales."""
        rut1 = Rut(12345678)
        rut2 = Rut(11111111)
        assert rut1 != rut2

    def test_hash_equal_ruts(self):
        """Verifica que RUTs iguales tengan el mismo hash."""
        rut1 = Rut(12345678)
        rut2 = Rut.parse("12.345.678-5")
        assert hash(rut1) == hash(rut2)

    def test_can_use_in_set(self):
        """Verifica que RUTs puedan usarse en sets correctamente."""
        ruts = {Rut(12345678), Rut.parse("12.345.678-5"), Rut(11111111)}
        assert len(ruts) == 2


class TestRutComparison:
    """Tests para comparaciones de orden de Rut."""

    def test_less_than(self):
        """Verifica la comparación menor que."""
        rut1 = Rut(10000000)
        rut2 = Rut(20000000)
        assert rut1 < rut2

    def test_less_or_equal(self):
        """Verifica la comparación menor o igual."""
        rut1 = Rut(10000000)
        rut2 = Rut(10000000)
        rut3 = Rut(20000000)
        assert rut1 <= rut2
        assert rut1 <= rut3

    def test_sorting(self):
        """Verifica que los RUTs puedan ordenarse correctamente."""
        ruts = [Rut(20000000), Rut(10000000), Rut(15000000)]
        sorted_ruts = sorted(ruts)
        assert sorted_ruts[0].number == 10000000
        assert sorted_ruts[1].number == 15000000
        assert sorted_ruts[2].number == 20000000


class TestIsValid:
    """Tests para la función is_valid."""

    def test_valid_rut_with_dots(self):
        """Verifica validación de RUT con formato completo."""
        assert is_valid("12.345.678-5") is True

    def test_valid_rut_with_hyphen(self):
        """Verifica validación de RUT con solo guión."""
        assert is_valid("12345678-5") is True

    def test_valid_rut_plain(self):
        """Verifica validación de RUT en formato plano."""
        assert is_valid("123456785") is True

    def test_valid_rut_with_k(self):
        """Verifica validación de RUT con DV 'K'."""
        assert is_valid("1.000.005-K") is True
        assert is_valid("1000005k") is True

    def test_invalid_dv(self):
        """Verifica que RUT con DV incorrecto sea inválido."""
        assert is_valid("12.345.678-9") is False

    def test_invalid_format(self):
        """Verifica que formato inválido retorne False."""
        assert is_valid("invalid") is False

    def test_number_too_small(self):
        """Verifica que número menor al mínimo sea inválido."""
        assert is_valid("999999-0") is False

    def test_number_too_large(self):
        """Verifica que número mayor al máximo sea inválido."""
        assert is_valid("100000000-0") is False

    def test_empty_string_returns_false(self):
        """Verifica que string vacío retorne False."""
        assert is_valid("") is False


class TestIsValidNumber:
    """Tests para la función is_valid_number."""

    def test_valid_number(self):
        """Verifica validación de número válido."""
        assert is_valid_number(12345678) is True

    def test_min_valid_number(self):
        """Verifica validación del número mínimo permitido."""
        assert is_valid_number(1000000) is True

    def test_max_valid_number(self):
        """Verifica validación del número máximo permitido."""
        assert is_valid_number(99999999) is True

    def test_number_too_small(self):
        """Verifica que número menor al mínimo sea inválido."""
        assert is_valid_number(999999) is False

    def test_number_too_large(self):
        """Verifica que número mayor al máximo sea inválido."""
        assert is_valid_number(100000000) is False

    def test_not_an_integer(self):
        """Verifica que tipos no enteros sean inválidos."""
        assert is_valid_number("12345678") is False
        assert is_valid_number(12345678.5) is False


class TestValidateMany:
    """Tests para la función validate_many."""

    def test_validate_many_all_valid(self):
        """Verifica validación múltiple con todos válidos."""
        ruts = ["12.345.678-5", "11.111.111-1", "1000005-K"]
        result = validate_many(ruts)
        assert result == [True, True, True]

    def test_validate_many_mixed(self):
        """Verifica validación múltiple con RUTs válidos e inválidos."""
        ruts = ["12.345.678-5", "12.345.678-9", "1000005-K"]
        result = validate_many(ruts)
        assert result == [True, False, True]

    def test_validate_many_all_invalid(self):
        """Verifica validación múltiple con todos inválidos."""
        ruts = ["invalid", "12.345.678-9", "999-0"]
        result = validate_many(ruts)
        assert result == [False, False, False]

    def test_validate_many_empty_list(self):
        """Verifica que lista vacía retorne lista vacía."""
        result = validate_many([])
        assert result == []


class TestFormatRut:
    """Tests para la función format_rut."""

    def test_format_rut_dots(self):
        """Verifica formateo con estilo DOTS."""
        assert format_rut("123456785", RutStyle.DOTS) == "12.345.678-5"

    def test_format_rut_dash(self):
        """Verifica formateo con estilo DASH."""
        assert format_rut("12.345.678-5", RutStyle.DASH) == "12345678-5"

    def test_format_rut_plain(self):
        """Verifica formateo con estilo PLAIN."""
        assert format_rut("12.345.678-5", RutStyle.PLAIN) == "123456785"


class TestNormalize:
    """Tests para la función normalize."""

    def test_normalize_plain(self):
        """Verifica normalización de formato plano."""
        assert normalize("123456785") == "12.345.678-5"

    def test_normalize_with_hyphen(self):
        """Verifica normalización de formato con guión."""
        assert normalize("12345678-5") == "12.345.678-5"

    def test_normalize_already_normalized(self):
        """Verifica que RUT ya normalizado permanezca igual."""
        assert normalize("12.345.678-5") == "12.345.678-5"


class TestMask:
    """Tests para la función mask."""

    def test_mask_rut(self):
        """Verifica enmascaramiento de RUT."""
        assert mask("12.345.678-5") == "XX.XXX.678-5"

    def test_mask_plain_format(self):
        """Verifica enmascaramiento de formato plano."""
        assert mask("123456785") == "XX.XXX.678-5"

    def test_mask_with_k(self):
        """Verifica enmascaramiento de RUT con DV 'K'."""
        assert mask("1.000.005-K") == "XX.XXX.005-K"


class TestGenerate:
    """Tests para la función generate."""

    def test_generate_returns_valid_rut(self):
        """Verifica que generate retorne un RUT válido."""
        rut = generate()
        assert isinstance(rut, Rut)
        assert 1000000 <= rut.number <= 99999999

    def test_generate_secure(self):
        """Verifica generación segura de RUT."""
        rut = generate(secure=True)
        assert isinstance(rut, Rut)
        assert 1000000 <= rut.number <= 99999999

    def test_generate_different_values(self):
        """Verifica que generate produzca valores diferentes."""
        ruts = [generate() for _ in range(10)]
        numbers = [rut.number for rut in ruts]
        assert len(set(numbers)) > 1


class TestGenerateMany:
    """Tests para la función generate_many."""

    def test_generate_many_count(self):
        """Verifica que generate_many retorne la cantidad correcta."""
        ruts = generate_many(5)
        assert len(ruts) == 5
        assert all(isinstance(rut, Rut) for rut in ruts)

    def test_generate_many_unique(self):
        """Verifica que generate_many con unique=True no genere duplicados."""
        ruts = generate_many(10, unique=True)
        numbers = [rut.number for rut in ruts]
        assert len(numbers) == len(set(numbers))

    def test_generate_many_not_unique(self):
        """Verifica que generate_many con unique=False permita duplicados."""
        ruts = generate_many(5, unique=False)
        assert len(ruts) == 5

    def test_generate_many_secure(self):
        """Verifica generación múltiple segura."""
        ruts = generate_many(5, secure=True)
        assert len(ruts) == 5

    def test_generate_many_invalid_count(self):
        """Verifica que cantidades inválidas lancen ValueError."""
        with pytest.raises(ValueError, match="cantidad debe ser un entero positivo"):
            generate_many(0)

        with pytest.raises(ValueError, match="cantidad debe ser un entero positivo"):
            generate_many(-1)


class TestExceptions:
    """Tests para las excepciones."""

    def test_rutify_error_base(self):
        """Verifica que RutifyError sea una excepción base válida."""
        exc = RutifyError("Error base")
        assert isinstance(exc, Exception)

    def test_invalid_rut_error(self):
        """Verifica que InvalidRutError almacene el RUT y mensaje correctamente."""
        exc = InvalidRutError("12.345.678-9", "DV incorrecto")
        assert exc.rut == "12.345.678-9"
        assert "12.345.678-9" in str(exc)
        assert "DV incorrecto" in str(exc)

    def test_invalid_rut_error_without_reason(self):
        """Verifica InvalidRutError sin razón específica."""
        exc = InvalidRutError("invalid")
        assert exc.rut == "invalid"
        assert "invalid" in str(exc)

    def test_invalid_rut_number_error(self):
        """Verifica que InvalidRutNumberError herede de RutifyError."""
        exc = InvalidRutNumberError("Número fuera de rango")
        assert isinstance(exc, RutifyError)


class TestRutStyle:
    """Tests para el enum RutStyle."""

    def test_rutstyle_values(self):
        """Verifica los valores del enum RutStyle."""
        assert RutStyle.DOTS == "dots"
        assert RutStyle.DASH == "dash"
        assert RutStyle.PLAIN == "plain"
        assert RutStyle.DOTS_NO_DASH == "dots_no_dash"

    def test_rutstyle_members(self):
        """Verifica que RutStyle tenga exactamente 4 miembros."""
        assert len(RutStyle) == 4
