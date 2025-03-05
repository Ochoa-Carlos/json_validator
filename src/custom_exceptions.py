

class BaseError(Exception):
    """Base class for custom exception"""
    def __init__(self, message):
        super().__init__(message)

class RegexError(BaseError):
    """Custom Regex Error."""

class CaracterError(BaseError):
    """Custom Contratista Error."""

class CaracterContratistaError(BaseError):
    """Custom Contratista Error."""

class CaracterAsignatarioError(BaseError):
    """Custom Asignatario Error."""

class CaracterPermisionarioError(BaseError):
    """Custom Permisionario Error."""

class CaracterUsuarioError(BaseError):
    """Custom Usuario Error."""

class LongitudError(BaseError):
    """Custom length error."""

class ValorMinMaxError(BaseError):
    """Custom value range error."""

class RequiredError(BaseError):
    """Custom length error."""

class ClaveError(BaseError):
    """Custom clave sub producto error."""

class ClaveSubProductoError(BaseError):
    """Custom clave sub producto error."""

class ClaveProductoError(BaseError):
    """Custom clave sub producto error."""

class RecepcionesError(BaseError):
    """Custom reception error."""

class ControlExistenciasError(BaseError):
    """Custom reception error."""

class EntregasError(BaseError):
    """Custom reception error."""

class BitacoraMensualError(BaseError):
    """Custom reception error."""

class TipadoError(BaseError):
    """Custom tipado error."""

class ValorError(BaseError):
    """Custom Valor error."""
