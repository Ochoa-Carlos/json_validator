import re
from typing import Union

from constants import CONDENSEDGAS_REGEX, petroleo_caracteres
from custom_exceptions import RegexError, ValorMinMaxError


class CondensedGasValidator:

    def __init__(self, gas_node: Union[list, dict]):
        self.gas_natural  = gas_node

    def validate_gasnatural(self) -> None:
        self._validate_condensado()
        self._validate_fraccion_molar()
        self._validate_poder_calorifico()

    def _validate_condensado(self) -> None:
        compo_gas = self.gas_natural.get("ComposGasNaturalOCondensados")

        if compo_gas is None:
            raise KeyError(
                f"""Error: 'ComposGasNaturalOCondensados' debe expresarse si se manifiesta caracter {petroleo_caracteres} y Producto 'PR09' o 'PR10'."""
            )
        if not re.match(CONDENSEDGAS_REGEX, compo_gas):
            raise RegexError(
                f"Error: 'ComposGasNaturalOCondensados {compo_gas}' no cumple con el patron {CONDENSEDGAS_REGEX}"
            )

# TODO EVALUAR CORRECTAMENTE COMO SE RECIBEN LAS FRACCIONES MOLARES
    def _validate_fraccion_molar(self) -> None:
        molar_val = self.gas_natural.get("FraccionMolar")

        if molar_val is None:
            raise KeyError(
                "Error: 'FraccionMolar' por cada componente expresado en 'ComposGasNaturalOCondensados'."
            )
        if not 0 <= molar_val <= 0.999:
            raise ValorMinMaxError(
                "Error: 'FraccionMolar' no está en el rango min 0 o max 0.999"
            )
        # TODO VALIDAR SUMA MLAR DE TODOS LOS COMPONENTES = 1

    def _validate_poder_calorifico(self) -> None:
        power_val = self.gas_natural.get("PoderCalorifico")

        if power_val is None:
            raise KeyError(
                "Error: 'PoderCalorifico' por cada componente expresado en 'ComposGasNaturalOCondensados'."
            )
        if not 0.001 <= power_val <= 150000:
            raise ValorMinMaxError(
                "Error: 'PoderCalorifico' no está en el rango min 0.001 o max 150000."
            )
