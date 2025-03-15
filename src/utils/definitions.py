"""SAT definitions"""

class CantidadMonetaria(float):
    """CantidadMonetaria definition."""
    min_val = 0
    max_val = 1_000_000_000_000.0
    max_decimals = 3
    def __new__(cls, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError(".")

        if not cls.min_val <= value <= cls.max_val:
            raise ValueError(f" está fuera del rango permitido {cls.min_val}-{cls.max_val}.")

        if "." in str(value) and len(str(value).split(".")[-1]) > cls.max_decimals:
            raise ValueError(" tiene más de 3 decimales.")

        return super().__new__(cls, value)

class ValorNumerico(float):
    """ValorNumerico definition."""
    min_val = 0
    max_val = 1_000_000_000_00.0
    max_decimals = 3
    def __new__(cls, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError(".")

        if not cls.min_val <= value <= cls.max_val:
            raise ValueError(f" está fuera del rango permitido {cls.min_val}-{cls.max_val}.")

        if "." in str(value) and len(str(value).split(".")[-1]) > cls.max_decimals:
            raise ValueError(" tiene más de 3 decimales.")

        return super().__new__(cls, value)

class PositiveNegativeNumber(float):
    """Number definition."""
    min_val = -1_000_000_000_00.0
    max_val = 1_000_000_000_00.0
    max_decimals = 3
    def __new__(cls, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError(".")

        if not cls.min_val <= value <= cls.max_val:
            raise ValueError(f" está fuera del rango permitido {cls.min_val}-{cls.max_val}.")

        if "." in str(value) and len(str(value).split(".")[-1]) > 3:
            raise ValueError(" tiene más de 3 decimales.")

        return super().__new__(cls, value)

class PositiveNumber(float):
    """Number definition."""
    min_val = 0
    max_val = 1_000_000_000_00.0
    max_decimals = 3
    def __new__(cls, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError(".")

        if not cls.min_val <= value <= cls.max_val:
            raise ValueError(f" está fuera del rango permitido {cls.min_val}-{cls.max_val}.")

        if "." in str(value) and len(str(value).split(".")[-1]) > 3:
            raise ValueError(" tiene más de 3 decimales.")

        return super().__new__(cls, value)
