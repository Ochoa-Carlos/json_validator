import re
from typing import Union

from src.constants import CONDENSEDGAS_REGEX, petroleo_caracteres
from src.custom_exceptions import RegexError, ValorMinMaxError, ClaveError
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import gas_dict


# TODO VALIDAR EL TIPADO Y AJUSTAR LA MANERA DE REGRESAR LOS ERRORES
class CondensedGasValidator:
    """Validate gas condensado class."""

    def __init__(self, gas_node: Union[list, dict]):
        self.gas_natural  = gas_node
        self._errors = {}
        self._executed_functions = set()

    def validate_gasnatural(self) -> None:
        """Validate gas natural o condensado."""
        self._validate_condensado_tipos()
        self._validate_condensado()
        self._validate_fraccion_molar()
        self._validate_poder_calorifico()

    @exception_wrapper
    def _validate_condensado_tipos(self) -> None:
        DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.gas_natural, dict_type=gas_dict)

    @exception_wrapper
    def _validate_condensado(self) -> None:
        compo_gas = self.gas_natural.get("ComposGasNaturalOCondensados")

        if compo_gas is None:
            self.catch_error(
                err_type=ClaveError,
                err_message=f"""Error: 'ComposGasNaturalOCondensados' debe expresarse si se manifiesta caracter {petroleo_caracteres} y Producto 'PR09' o 'PR10'."""
                )
        if compo_gas and not re.match(CONDENSEDGAS_REGEX, compo_gas):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: 'ComposGasNaturalOCondensados {compo_gas}' no cumple con el patron {CONDENSEDGAS_REGEX}"
                )

# TODO EVALUAR CORRECTAMENTE COMO SE RECIBEN LAS FRACCIONES MOLARES
    @exception_wrapper
    def _validate_fraccion_molar(self) -> None:
        molar_val = self.gas_natural.get("FraccionMolar")

        if molar_val is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: 'FraccionMolar' por cada componente expresado en 'ComposGasNaturalOCondensados'."
                )
        if molar_val and not 0 <= molar_val <= 0.999:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message="Error: 'FraccionMolar' no está en el rango min 0 o max 0.999"
                )
        # TODO VALIDAR SUMA MLAR DE LOS COMPONENTES = 1

    @exception_wrapper
    def _validate_poder_calorifico(self) -> None:
        power_val = self.gas_natural.get("PoderCalorifico")

        if power_val is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: 'PoderCalorifico' por cada componente expresado en 'ComposGasNaturalOCondensados'."
                )
        if power_val and not 0.001 <= power_val <= 150000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message="Error: 'PoderCalorifico' no está en el rango min 0.001 o max 150000."
                )

    def catch_error(self, err_type: str | Exception, err_message: str) -> dict:
        """Catch error from validations."""
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message
            }

    @property
    def errors(self) -> dict:
        """Get errors from condensed gas validator obj."""
        return self._errors

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in condensed gas validator obj."""
        self._errors[errors["type_error"]] = errors["error"]

    @property
    def exc_funcs(self) -> dict:
        """Get excecuted function in condensed gas validator class."""
        return self._executed_functions

    @exc_funcs.setter
    def exc_funcs(self, executed_function: str) -> None:
        """set excecuted function in condensed gas validator class."""
        self._executed_functions.add(executed_function)
