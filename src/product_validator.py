import re

from src.condensed_gas_validator import CondensedGasValidator
from src.constants import (SUBPRODUCTO_REGEX, petroleo_caracteres, products_keys,
                       subproducts_keys)
from src.custom_exceptions import (CaracterError, ClaveProductoError,
                               ClaveSubProductoError, LongitudError,
                               RegexError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import product_dict
from src.monthly_volume_report import MonthlyVolumeReportValidator


class ProductValidator:
    """Product validator class."""

    def __init__(self, products: list, caracter: str):
        self._gen_index = 0
        self.caracter = caracter
        self.products = products
        self.products_len = len(products)
        self.current_product = self.products[self._gen_index]
        self._errors = {}
        self._product_errors = {}
        self._product_errors_list = []
        self._executed_functions = set()

# TODO DESCOMENTAR VALIDATE GASNATURAL Y AJUSTAR
    def validate_products(self) -> None:
        if self._next_product():
            self._validate_producto_tipado()
            self._validate_clave_producto()
            self._validate_clave_sub_producto()
            self._validate_octanaje_gasolina()
            self._validate_combustible_nofosil()
            self._validate_combustible_nofosil_engasolina()
            self._validate_diesel_combustible_nofosil()
            self._validate_combustible_nofosil_endiesel()
            self._validate_combustible_turbosina_nofosil()
            self._validate_combustible_nofosil_enturbosina()
            self._validate_compos_propano_gaslp()
            self._validate_compos_butano_gaslp()
            self._validate_densidad_petroleo()
            self._validate_compos_azufre_petroleo()
            self._validate_otros()
            self._validate_marca_comercial()
            self._validate_marcaje()
            self._validate_concentracion_sustancia_marcaje()
            self._validate_monthly_report()
            self._validate_gasnatural_ocondensados()

            self._update_index()
            self.validate_products()
        else:
            print("Ya no hay productos por validar ==================================")

    @exception_wrapper
    def _validate_producto_tipado(self) -> None:
        prod = self.current_product

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=prod, dict_type=product_dict):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)

    @exception_wrapper
    def _validate_clave_producto(self) -> None:
        prod = self.current_product

        if prod.get("ClaveProducto") not in products_keys:
            self.catch_error(err_type=KeyError, err_message="Error: 'Clave producto' requerida no encontrada.")
            # raise RequiredError("Error: 'Clave producto' requerida no encontrada.")

    @exception_wrapper
    def _validate_clave_sub_producto(self) -> None:
        product_key = self.current_product.get("ClaveProducto")
        subproduct_key = self.current_product.get("ClaveSubProducto")

        if product_key not in subproducts_keys:
            self.catch_error(err_type=ClaveSubProductoError, err_message=f"Error: 'ClaveSubProducto {subproduct_key}' debe pertenecer a los productos {subproducts_keys}.")
            # raise ClaveSubProductoError(
            #     f"Error: 'ClaveSubProducto {subproduct_key}' debe pertenecer a los productos {subproducts_keys}."
            #     )
        if not re.match(SUBPRODUCTO_REGEX, subproduct_key):
            self.catch_error(err_type=RegexError, err_message=f"Error: 'ClaveSubProducto {subproduct_key}' no cumple con el patron {SUBPRODUCTO_REGEX}")
            # raise RegexError(
            #     f"Error: 'ClaveSubProducto {subproduct_key}' no cumple con el patron {SUBPRODUCTO_REGEX}"
            #     )

# TODO FORMAN PARTE DEL PRODUCTO PR07
    @exception_wrapper
    def _validate_octanaje_gasolina(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if octanaje_gas := self.current_product.get("ComposOctanajeGasolina"):
            if  product_key != "PR07":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'ComposOctanajeGasolina' solo pertenece a ClaveProducto 'PR07'.")
                # raise ClaveProductoError(
                #     "Error: 'ComposOctanajeGasolina' solo pertenece a ClaveProducto 'PR07'."
                # )
            if not 87 <= octanaje_gas <= 130:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposOctanajeGasolina' no está en el rango min 87 o max 130.")
                # raise ValorMinMaxError(
                #     "Error: 'ComposOctanajeGasolina' no está en el rango min 87 o max 130."
                # )

    @exception_wrapper
    def _validate_combustible_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if nofossil_fuel := self.current_product.get("GasolinaConCombustibleNoFosil"):
            if product_key != "PR07":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'GasolinaConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR07'")
                # raise ClaveProductoError(
                #     "Error: 'GasolinaConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR07'"
                # )
            if nofossil_fuel not in ["Sí", "No"]:
                self.catch_error(err_type=ValueError, err_message="Valor GasolinaConCombustibleNoFosil inválido.")
                # raise ValueError("Valor CombustibleNoFosil inválido.")

    @exception_wrapper
    def _validate_combustible_nofosil_engasolina(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if nofossil_ingas_fuel := self.current_product.get("ComposDeCombustibleNoFosilEnGasolina"):
            if product_key != "PR07":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'ComposDeCombustibleNoFosilEnGasolina' solo pertenece a ClaveProducto 'PR07'")
                # raise ClaveProductoError(
                #     "Error: 'ComposDeCombustibleNoFosilEnGasolina' solo pertenece a ClaveProducto 'PR07'"
                #     )
            if not 1 <= nofossil_ingas_fuel <= 99:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposDeCombustibleNoFosilEnGasolina' no está en el rango min 1 o max 99.")
                # raise ValorMinMaxError(
                #     "Error: 'ComposDeCombustibleNoFosilEnGasolina' no está en el rango min 1 o max 99."
                #     )

# TODO FORMAN PARTE DEL PRODUCTO PRR03
    @exception_wrapper
    def _validate_diesel_combustible_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if diesel_nofossil_fuel := self.current_product.get("DieselConCombustibleNoFosil"):
            if product_key != "PR03":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'DieseConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR03'")
                # raise ClaveProductoError(
                #     "Error: 'DieseConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR03'"
                #     )
            if diesel_nofossil_fuel not in ["Sí", "No"]:
                self.catch_error(err_type=ValueError, err_message="DieseConCombustibleNoFosil inválido.")
                # raise ValueError("DieseConCombustibleNoFosil inválido.")

    @exception_wrapper
    def _validate_combustible_nofosil_endiesel(self) -> None:
        nofossil_fuel = self.current_product.get("DieselConCombustibleNoFosil")

        if nofossil_fuel == "Sí":
            if nofossil_fuel_diesel := self.current_product.get("ComposDeCombustibleNoFosilEnDiesel"):
                if not 1 <= nofossil_fuel_diesel <= 99:
                    self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'DieselConCombustibleNoFosil' no está en el rango min 1 o max 99.")
                    # raise ValorMinMaxError(
                    #     "Error: 'DieselConCombustibleNoFosil' no está en el rango min 1 o max 99."
                    #     )

# TODO FORMAN PARTE DEL PRODUCTO PR11
    @exception_wrapper
    def _validate_combustible_turbosina_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if turbosine_nofossil_fuel := self.current_product.get("TurbosinaConCombustibleNoFosil"):
            if product_key != "PR11":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'TurbosinaConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR11'")
                # raise ClaveProductoError(
                #     "Error: 'TurbosinaConCombustibleNoFosil' solo pertenece a ClaveProducto 'PR11'"
                #     )
            if turbosine_nofossil_fuel not in ["Sí", "No"]:
                self.catch_error(err_type=ValueError, err_message="TurbosinaConCombustibleNoFosil inválido.")
                # raise ValueError("TurbosinaConCombustibleNoFosil inválido.")

    @exception_wrapper
    def _validate_combustible_nofosil_enturbosina(self) -> None:
        if turbosine_nofossil_fuel := self.current_product.get("TurbosinaConCombustibleNoFosil"):
            if turbosine_nofossil_fuel == "Sí":
                nofossil_fuel_turobssine = self.current_product.get("ComposDeCombustibleNoFosilEnTurbosina")
                if not 1 <= nofossil_fuel_turobssine <= 99:
                    self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposDeCombustibleNoFosilEnTurbosina' no está en el rango min 1 o max 99.")
                    # raise ValorMinMaxError(
                    #     "Error: 'ComposDeCombustibleNoFosilEnTurbosina' no está en el rango min 1 o max 99."
                    #     )

# TODO FORMAN PARTE DE EL PRODUCTO PR12
    def _validate_compos_propano_gaslp(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if propane_gaslp := self.current_product.get("ComposDePropanoEnGasLP"):
            if product_key != "PR12":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'ComposDePropanoEnGasLP' solo pertenece a ClaveProducto 'PR12'")
                # raise ClaveProductoError(
                #     "Error: 'ComposDePropanoEnGasLP' solo pertenece a ClaveProducto 'PR12'"
                # )
            if not 0.01 <= propane_gaslp <= 99.99:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposDePropanoEnGasLP' no está en el rango min 0.01 o max 99.99.")
                # raise ValorMinMaxError(
                #     "Error: 'ComposDePropanoEnGasLP' no está en el rango min 0.01 o max 99.99."
                # )

    @exception_wrapper
    def _validate_compos_butano_gaslp(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if propane_gaslp := self.current_product.get("ComposDeButanoEnGasLP"):
            if product_key != "PR12":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'ComposDeButanoEnGasLP' solo pertenece a ClaveProducto 'PR12'")
                # raise ClaveProductoError(
                #     "Error: 'ComposDeButanoEnGasLP' solo pertenece a ClaveProducto 'PR12'"
                # )
            if not 0.01 <= propane_gaslp <= 99.99:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposDeButanoEnGasLP' no está en el rango min 0.01 o max 99.99.")
                # raise ValorMinMaxError(
                #     "Error: 'ComposDeButanoEnGasLP' no está en el rango min 0.01 o max 99.99."
                # )

# TODO pertenece al productoo PR08 Y CARACTER CONTRATISTA O PERMISIONARIO
    @exception_wrapper
    def _validate_densidad_petroleo(self) -> None:
        if oil_density := self.current_product.get("DensidadDePetroleo"):
            if self.caracter not in petroleo_caracteres:
                self.catch_error(err_type=CaracterError, err_message=f"Error: 'DensidadDePetroleo' solo pertenece a los caracteres {petroleo_caracteres}")
                # raise CaracterError(
                #     f"Error: 'DensidadDePetroleo' solo pertenece a los caracteres {petroleo_caracteres}"
                # )
            if not 0.1 <= oil_density <= 80:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'DensidadDePetroleo' no está en el rango min 0.1 o max 80.")
                # raise ValorMinMaxError(
                #     "Error: 'DensidadDePetroleo' no está en el rango min 0.1 o max 80."
                # )

    @exception_wrapper
    def _validate_compos_azufre_petroleo(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if sulfur_compos := self.current_product.get("ComposDeAzufreEnPetroleo"):
            if product_key != "PR08":
                self.catch_error(err_type=ClaveProductoError, err_message="Error: 'ComposDeAzufreEnPetroleo' solo pertenece a ClaveProducto 'PR08'.")
                # raise ClaveProductoError(
                #     "Error: 'ComposDeAzufreEnPetroleo' solo pertenece a ClaveProducto 'PR08'."
                # )
            if self.caracter not in petroleo_caracteres:
                self.catch_error(err_type=CaracterError, err_message=f"Error: 'ComposDeAzufreEnPetroleo' solo pertenece a los caracteres {petroleo_caracteres}")
                # raise CaracterError(
                #     f"Error: 'ComposDeAzufreEnPetroleo' solo pertenece a los caracteres {petroleo_caracteres}"
                # )
            if not 0.1 <= sulfur_compos <= 10:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ComposDeAzufreEnPetroleo' no está en el rango min 0.1 o max 10.")
                # raise ValorMinMaxError(
                #     "Error: 'ComposDeAzufreEnPetroleo' no está en el rango min 0.1 o max 10."
                # )

# TODO TERMINAN VALIDACIONES POR PRODUCTO
    @exception_wrapper
    def _validate_otros(self) -> None:
        product_key = self.current_product.get("ClaveProducto")
        subproduct_key = self.current_product.get("ClaveSubProducto")

        if product_key == "PR15" and subproduct_key == "SP20":
            others = self.current_product.get("Otros")
            if not 1 <= len(others) <= 30:
                self.catch_error(err_type=LongitudError, err_message="Error: 'Otros' no cumple con la longitud min 1 o max 30.")
                # raise LongitudError(
                #     "Error: 'Otros' no cumple con la longitud min 1 o max 30."
                #     )

    @exception_wrapper
    def _validate_marca_comercial(self) -> None:
        if brand := self.current_product.get("MarcaComercial"):
            if not 2 <= len(brand) <= 200:
                self.catch_error(err_type=LongitudError, err_message="Error: 'MarcaComercial' no cumple con la longitud min 2 o max 200.")
                # raise LongitudError(
                #     "Error: 'MarcaComercial' no cumple con la longitud min 2 o max 200."
                # )

    @exception_wrapper
    def _validate_marcaje(self) -> None:
        if marking := self.current_product.get("Marcaje"):
            if not 2 <= len(marking) <= 40:
                self.catch_error(err_type=LongitudError, err_message="Error: 'Marcaje' no cumple con la longitud min 2 o max 40.")
                # raise LongitudError(
                #     "Error: 'Marcaje' no cumple con la longitud min 2 o max 40."
                # )

    @exception_wrapper
    def _validate_concentracion_sustancia_marcaje(self) -> None:
        if marking := self.current_product.get("Marcaje"):
            concentration = self.current_product.get("ConcentracionSustanciaMarcaje")
            if not concentration:
                self.catch_error(err_type=KeyError, err_message="Error: 'ConcentracionSustanciaMarcaje' debe expresarse si se manifiesta 'Marcaje'.")
                # raise KeyError(
                #     "Error: 'ConcentracionSustanciaMarcaje' debe expresarse si se manifiesta 'Marcaje'."
                # )
            if not 1 <= concentration <= 1000:
                self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ConcentracionSustanciaMarcaje' no está en el rango min 1 o max 1000.")
                # raise ValorMinMaxError(
                #     "Error: 'ConcentracionSustanciaMarcaje' no está en el rango min 1 o max 1000."
                # )


    # @exception_wrapper
    def _validate_monthly_report(self) -> None:
        if month_report := self.current_product.get("ReporteDeVolumenMensual"):

            product_key = self.current_product.get("ClaveProducto")
            month_report_obj = MonthlyVolumeReportValidator(
                monthly_volume_report=month_report,
                product_key=product_key,
                caracter=self.caracter)
            month_report_obj.validate_report()

            if report_errors := month_report_obj.errors:
                # self._errors = self._errors | report_errors
                # self._product_errors[self.current_product.get("ClaveProducto")].extend(report_errors)
                self._product_errors_list.extend(report_errors)

    # @exception_wrapper
    def _validate_gasnatural_ocondensados(self) -> None:
        if self.caracter in petroleo_caracteres and self.current_product.get("ClaveProducto") in ["PR09", "PR10"]:
            if (natural_gas := self.current_product.get("GasNaturalOCondensados")) is None:
                self.catch_error(
                    err_type=KeyError,
                    err_message=f"Error: 'GasNaturalOCondensados' debe expresarse si se manifiesta caracter {petroleo_caracteres} y Producto 'PR09' o 'PR10'."
                    )
                # raise KeyError(
                #     f"""Error: 'GasNaturalOCondensados' debe expresarse si se manifiesta caracter {petroleo_caracteres} y Producto 'PR09' o 'PR10'."""
                # )
            if not 2 <= len(natural_gas) <= 10:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: 'InstalacionAlmacenGasNatural' no cumple con los elementos min 2 o max 10."
                    )
                # raise LongitudError(
                #     "Error: 'InstalacionAlmacenGasNatural' no cumple con los elementos min 2 o max 10."
                #     )

            gas_node = self.current_product.get("GasNaturalOCondensados")
            condensed_obj = CondensedGasValidator(gas_node=gas_node)
            condensed_obj.validate_gasnatural()

            if report_errors := condensed_obj.errors:
                self._errors = self._errors | report_errors

    def _current_product(self) -> dict:
        return self.products[self._gen_index]

    def _next_product(self) -> bool:
        return self._gen_index < self.products_len

    def _update_index(self) -> None:
        self._gen_index += 1
        if self._next_product():
            self.current_product = self.products[self._gen_index]

    def catch_error(self, err_type: str | Exception, err_message: str) -> dict:
        """Catch error from validations."""
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message
            }

    @property
    def errors(self) -> dict:
        """Get errors from product validation obj."""
        return self._product_errors_list

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in product validation obj."""
        key = self.current_product.get("ClaveProducto")

        if key not in self._product_errors:
            self._product_errors[key] = []
        self._product_errors_list.append(errors)
        self._product_errors[key].append(errors)
        self._errors[errors["type_error"]] = errors["error"]

    @property
    def exc_funcs(self) -> dict:
        """Get excecuted function in product validation class."""
        return self._executed_functions

    @exc_funcs.setter
    def exc_funcs(self, executed_function: str) -> None:
        """set excecuted function in product validation class."""
        self._executed_functions.add(executed_function)
