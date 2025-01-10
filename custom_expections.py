

class BaseError(Exception):
    """Base class for custom exception"""
    def __init__(self, message):
        super().__init__(message)

class RegexError(BaseError):
    """Custom Regex Error."""

class CaracterContratistaError(BaseError):
    """Custom Contratista Error."""

class CaracterAsignatarioError(BaseError):
    """Custom Asignatario Error."""

class CaracterPermisionarioError(BaseError):
    """Custom Permisionario Error."""

class CaracterUsuarioError(BaseError):
    """Custom Usuario Error."""
