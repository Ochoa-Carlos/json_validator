"""This module handles product validations."""
import re
from typing import Optional, Union, List

from src.condensed_gas_validator import CondensedGasValidator
from src.constants import (SUBPRODUCTO_REGEX, petroleo_caracteres,
                           products_keys, subproducts_keys)
from src.custom_exceptions import (CaracterError, ClaveError,
                                   ClaveProductoError, ClaveSubProductoError,
                                   LongitudError, ProductoError, RegexError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import product_dict
from src.enumerators import ProductEnum, SiNoEnum, SubProductEnum
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

    def validate_products(self) -> None:
        """Validate product JSON body."""
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
            self._additionals_validations()

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
            self.catch_error(err_type=ClaveError, err_message="Error: 'Clave producto' requerida no encontrada.")

    @exception_wrapper
    def _validate_clave_sub_producto(self) -> None:
        product_key = self.current_product.get("ClaveProducto")
        subproduct_key = self.current_product.get("ClaveSubProducto")

        if product_key in [ProductEnum.PR03.value, ProductEnum.PR07.value, ProductEnum.PR08.value,
                           ProductEnum.PR09.value, ProductEnum.PR11.value, ProductEnum.PR13.value,
                           ProductEnum.PR15.value, ProductEnum.PR16.value, ProductEnum.PR17.value,
                           ProductEnum.PR18.value, ProductEnum.PR19.value] and subproduct_key is None:
            self.catch_error(
                err_type=ClaveSubProductoError,
                err_message=f"Error: Elemento 'ClaveSubProducto' requerido para ClaveProducto: {product_key}",
                )
        if subproduct_key and not re.match(SUBPRODUCTO_REGEX, subproduct_key):
            self._regex_error(
                    key="ClaveSubProducto", value=subproduct_key, pattern=SUBPRODUCTO_REGEX,
                    source="ClaveSubProducto"
                    )

    @exception_wrapper
    def _validate_octanaje_gasolina(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if octanaje_gas := self.current_product.get("ComposOctanajeGasolina"):
            if  product_key != ProductEnum.PR07.value:
                self._product_key_error(
                    product_key=ProductEnum.PR07.value, subproduct_key="ComposOctanajeGasolina",
                    source="ComposOctanajeGasolina"
                    )
            if not 87 <= octanaje_gas <= 130:
                self._min_max_value_error(
                    key="ComposOctanajeGasolina", value=octanaje_gas, min_val=87, max_val=130,
                    source="ComposOctanajeGasolina"
                    )

    @exception_wrapper
    def _validate_combustible_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if nofossil_fuel := self.current_product.get("GasolinaConCombustibleNoFosil"):
            if product_key != ProductEnum.PR07.value:
                self._product_key_error(
                    product_key=ProductEnum.PR07.value, subproduct_key="GasolinaConCombustibleNoFosil",
                    source="ComposDeCombustibleNoFosilEnGasolina"
                    )
            if nofossil_fuel not in [SiNoEnum.SI.value, SiNoEnum.NO.value]:
                self._value_error(
                    key="GasolinaConCombustibleNoFosil", value=nofossil_fuel,
                    source="ComposDeCombustibleNoFosilEnGasolina"
                    )

    @exception_wrapper
    def _validate_combustible_nofosil_engasolina(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if nofossil_ingas_fuel := self.current_product.get("ComposDeCombustibleNoFosilEnGasolina"):
            if product_key != ProductEnum.PR07.value:
                self._product_key_error(
                    product_key=ProductEnum.PR07.value, subproduct_key="ComposDeCombustibleNoFosilEnGasolina",
                    source="ComposDeCombustibleNoFosilEnGasolina"
                    )
            if not 1 <= nofossil_ingas_fuel <= 99:
                self._min_max_value_error(
                    key="ComposDeCombustibleNoFosilEnGasolina", value=nofossil_ingas_fuel,
                    min_val=1, max_val=99,
                    source="ComposDeCombustibleNoFosilEnGasolina"
                    )

    @exception_wrapper
    def _validate_diesel_combustible_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if diesel_nofossil_fuel := self.current_product.get("DieselConCombustibleNoFosil"):
            if product_key != "PR03":
                self._product_key_error(
                    product_key=ProductEnum.PR03.value, subproduct_key="DieseConCombustibleNoFosil",
                    source="DieselConCombustibleNoFosil"
                    )
            if diesel_nofossil_fuel not in [SiNoEnum.SI.value, SiNoEnum.NO.value]:
                self._value_error(
                    key="DieselConCombustibleNoFosil", value=diesel_nofossil_fuel,
                    source="DieselConCombustibleNoFosil"
                    )

    @exception_wrapper
    def _validate_combustible_nofosil_endiesel(self) -> None:
        nofossil_fuel = self.current_product.get("DieselConCombustibleNoFosil")

        if nofossil_fuel == SiNoEnum.SI.value:
            if nofossil_fuel_diesel := self.current_product.get("ComposDeCombustibleNoFosilEnDiesel"):
                if not 1 <= nofossil_fuel_diesel <= 99:
                    self._min_max_value_error(
                        key="DieselConCombustibleNoFosil", value=nofossil_fuel_diesel,
                        min_val=1, max_val=99,
                        source="DieselConCombustibleNoFosil"
                        )

    @exception_wrapper
    def _validate_combustible_turbosina_nofosil(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if turbosine_nofossil_fuel := self.current_product.get("TurbosinaConCombustibleNoFosil"):
            if product_key != ProductEnum.PR11.value:
                self._product_key_error(
                    product_key=ProductEnum.PR11.value, subproduct_key="TurbosinaConCombustibleNoFosil",
                    source="TurbosinaConCombustibleNoFosil"
                    )
            if turbosine_nofossil_fuel not in [SiNoEnum.SI.value, SiNoEnum.NO.value]:
                self._value_error(
                    key="TurbosinaConCombustibleNoFosil", value=turbosine_nofossil_fuel,
                    source="TurbosinaConCombustibleNoFosil"
                    )

    @exception_wrapper
    def _validate_combustible_nofosil_enturbosina(self) -> None:
        if turbosine_nofossil_fuel := self.current_product.get("TurbosinaConCombustibleNoFosil"):
            if turbosine_nofossil_fuel == SiNoEnum.SI.value:
                nofossil_fuel_turobssine = self.current_product.get("ComposDeCombustibleNoFosilEnTurbosina")
                if not 1 <= nofossil_fuel_turobssine <= 99:
                    self._min_max_value_error(
                        key="ComposDeCombustibleNoFosilEnTurbosina", value=nofossil_fuel_turobssine,
                        min_val=1, max_val=99,
                        source="TurbosinaConCombustibleNoFosil"
                        )

    def _validate_compos_propano_gaslp(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if propane_gaslp := self.current_product.get("ComposDePropanoEnGasLP"):
            if product_key != ProductEnum.PR12.value:
                self._product_key_error(
                    product_key=ProductEnum.PR12.value, subproduct_key="ComposDePropanoEnGasLP",
                    source="ComposDePropanoEnGasLP"
                    )
            if not 0.01 <= propane_gaslp <= 99.99:
                self._min_max_value_error(
                    key="ComposDePropanoEnGasLP", value=propane_gaslp, min_val=0.01, max_val=99.99,
                    source="ComposDePropanoEnGasLP"
                    )

    @exception_wrapper
    def _validate_compos_butano_gaslp(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if propane_gaslp := self.current_product.get("ComposDeButanoEnGasLP"):
            if product_key != ProductEnum.PR12.value:
                self._product_key_error(
                    product_key=ProductEnum.PR12.value, subproduct_key="ComposDeButanoEnGasLP",
                    source="ComposDeButanoEnGasLP"
                    )
            if not 0.01 <= propane_gaslp <= 99.99:
                self._min_max_value_error(
                    key="ComposDeButanoEnGasLP", value=propane_gaslp, min_val=0.01, max_val=99.99,
                    source="ComposDeButanoEnGasLP"
                    )

    @exception_wrapper
    def _validate_densidad_petroleo(self) -> None:
        if oil_density := self.current_product.get("DensidadDePetroleo"):
            if self.caracter not in petroleo_caracteres:
                self.catch_error(
                    err_type=CaracterError,
                    err_message=f"Error: 'DensidadDePetroleo' solo pertenece a los caracteres {petroleo_caracteres}"
                    )
            if not 0.1 <= oil_density <= 80:
                self._min_max_value_error(
                    key="DensidadDePetroleo", value=oil_density, min_val=0.1, max_val=80,
                    )

    @exception_wrapper
    def _validate_compos_azufre_petroleo(self) -> None:
        product_key = self.current_product.get("ClaveProducto")

        if sulfur_compos := self.current_product.get("ComposDeAzufreEnPetroleo"):
            if product_key != "PR08":
                self._product_key_error(
                    product_key=ProductEnum.PR08.value, subproduct_key="ComposDeAzufreEnPetroleo",
                    )
            if self.caracter not in petroleo_caracteres:
                self.catch_error(
                    err_type=CaracterError,
                    err_message=f"Error:ComposDeAzufreEnPetroleo solo pertenece a los caracteres {petroleo_caracteres}"
                    )
            if not 0.1 <= sulfur_compos <= 10:
                self._min_max_value_error(
                    key="ComposDeAzufreEnPetroleo", value=sulfur_compos, min_val=0.1, max_val=10,
                    )

    @exception_wrapper
    def _validate_otros(self) -> None:
        product_key = self.current_product.get("ClaveProducto")
        subproduct_key = self.current_product.get("ClaveSubProducto")

        if product_key == "PR15" and subproduct_key == "SP20":
            others = self.current_product.get("Otros")
            if not 1 <= len(others) <= 30:
                self._longitud_error(
                    key="Otros", value=others, min_long=1, max_long=30,
                    )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message="Error: 'Otros' no cumple con la longitud min 1 o max 30.")

    @exception_wrapper
    def _validate_marca_comercial(self) -> None:
        if brand := self.current_product.get("MarcaComercial"):
            if not 2 <= len(brand) <= 200:
                self._longitud_error(
                    key="MarcaComercial", value=brand, min_long=2, max_long=200,
                    )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message="Error: 'MarcaComercial' no cumple con la longitud min 2 o max 200.")

    @exception_wrapper
    def _validate_marcaje(self) -> None:
        if marking := self.current_product.get("Marcaje"):
            if not 2 <= len(marking) <= 40:
                self._longitud_error(
                    key="Marcaje", value=marking, min_long=2, max_long=40,
                    )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message="Error: 'Marcaje' no cumple con la longitud min 2 o max 40.")

    @exception_wrapper
    def _validate_concentracion_sustancia_marcaje(self) -> None:
        if marking := self.current_product.get("Marcaje"):
            concentration = self.current_product.get("ConcentracionSustanciaMarcaje")
            if not concentration:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: 'ConcentracionSustanciaMarcaje' debe expresarse si se manifiesta 'Marcaje'."
                    )
            if not 1 <= concentration <= 1000:
                self._min_max_value_error(
                    key="ConcentracionSustanciaMarcaje", value=concentration, min_val=1, max_val=1000,
                    )
                # self.catch_error(
                #     err_type=ValorMinMaxError,
                #     err_message="Error: 'ConcentracionSustanciaMarcaje' no está en el rango min 1 o max 1000.")

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
                for err in report_errors:
                    if source := err.get("source"):
                        err["source"] = f"Producto[{self.products.index(self.current_product)}].{source}"
                self._product_errors_list.extend(report_errors)

    # @exception_wrapper
    def _validate_gasnatural_ocondensados(self) -> None:
        if self.caracter not in petroleo_caracteres or self.current_product.get(
            "ClaveProducto"
        ) not in [ProductEnum.PR09.value, ProductEnum.PR10.value]:
            return
        if (natural_gas := self.current_product.get("GasNaturalOCondensados")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message=f"Error: 'GasNaturalOCondensados' debe expresarse si se manifiesta caracter {petroleo_caracteres} y Producto 'PR09' o 'PR10'."
                )
        if not 2 <= len(natural_gas) <= 10:
            self._longitud_error(
                key="InstalacionAlmacenGasNatural", value=natural_gas, min_long=2, max_long=10,
                )

        gas_node = self.current_product.get("GasNaturalOCondensados")
        condensed_obj = CondensedGasValidator(gas_node=gas_node)
        condensed_obj.validate_gasnatural()

        if report_errors := condensed_obj.errors:
            self._errors = self._errors | report_errors

    def _additionals_validations(self) -> None:
        """Extra validations according product and subproduct"""
        product_key = self.current_product.get("ClaveProducto")
        subp_key = self.current_product.get("ClaveSubProducto")

        if product_key == ProductEnum.PR07.value and subp_key not in {
            SubProductEnum.SP16.value, SubProductEnum.SP17.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto"
                    f"deben ser {SubProductEnum.SP16.value} ó {SubProductEnum.SP17.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto
            # deben ser {SubProductEnum.SP16.value} ó {SubProductEnum.SP17.value}.")
        if product_key == ProductEnum.PR03.value and subp_key not in {
            SubProductEnum.SP18.value, SubProductEnum.SP19.value,
            SubProductEnum.SP22.value, SubProductEnum.SP23.value,
            SubProductEnum.SP24.value, SubProductEnum.SP25.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto"
                    f"deben ser {SubProductEnum.SP18.value}, {SubProductEnum.SP19.value}, {SubProductEnum.SP22.value}"
                    f", {SubProductEnum.SP23.value}, {SubProductEnum.SP24.value}, {SubProductEnum.SP25.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto deben ser
            # {SubProductEnum.SP18.value}, {SubProductEnum.SP19.value}, {SubProductEnum.SP22.value},
            # {SubProductEnum.SP23.value}, {SubProductEnum.SP24.value}, {SubProductEnum.SP25.value}.")
        if product_key == ProductEnum.PR07.value:
            nofosil_gas = self.current_product.get("GasolinaConCombustibleNoFosil")
            comp_oct_gas = self.current_product.get("ComposOctanajeGasolina")
            if comp_oct_gas is None:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        f"debe existir el elemento 'ComposOctanajeGasolina'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # debe existir el elemento 'ComposOctanajeGasolina'.")
            if nofosil_gas is None:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        f"debe existir el elemento 'GasolinaConCombustibleNoFosil'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # debe existir el elemento 'GasolinaConCombustibleNoFosil'.")
            if nofosil_gas and nofosil_gas == SiNoEnum.SI.value and self.current_product.get("ComposDeCombustibleNoFosilEnGasolina") is None:
                self._product_error(
                    custom_message=(
                        "Error: Error: para valor 'Sí' en clave 'GasolinaConCombustibleNoFosil'"
                        "debe existir elemento 'ComposDeCombustibleNoFosilEnGasolina'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message="Error: para valor 'Sí' en clave 'GasolinaConCombustibleNoFosil'"
                #     "debe existir elemento 'ComposDeCombustibleNoFosilEnGasolina'.")
        if product_key == ProductEnum.PR03.value:
            nofosil_diesel = self.current_product.get("DieselConCombustibleNoFosil")
            if nofosil_diesel is None:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        "debe existir el elemento 'DieselConCombustibleNoFosil'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # debe existir el elemento 'DieselConCombustibleNoFosil'.")
            if nofosil_diesel == SiNoEnum.SI.value and self.current_product.get("ComposDeCombustibleNoFosilEnDiesel") is None:
                self._product_error(
                    custom_message=(
                        "Error: para valor 'Sí' en clave 'DieselConCombustibleNoFosil'"
                        "debe existir elemento 'ComposDeCombustibleNoFosilEnDiesel'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message="Error: para valor 'Sí' en clave 'DieselConCombustibleNoFosil'
                # debe existir elemento 'ComposDeCombustibleNoFosilEnDiesel'.")
        if product_key == ProductEnum.PR11.value:
            nofosil_turbosine = self.current_product.get("TurbosinaConCombustibleNoFosil")
            if nofosil_turbosine is None:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        "debe existir el elemento 'TurbosinaConCombustibleNoFosil'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # debe existir el elemento 'TurbosinaConCombustibleNoFosil'.")
            if nofosil_turbosine == SiNoEnum.SI.value and self.current_product.get("ComposDeCombustibleNoFosilEnTurbosina") is None:
                self._product_error(
                    custom_message=(
                        "Error: para valor 'Sí' en clave 'TurbosinaConCombustibleNoFosil'"
                        "debe existir elemento 'ComposDeCombustibleNoFosilEnTurbosina'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message="Error: para valor 'Sí' en clave 'TurbosinaConCombustibleNoFosil'
                # debe existir elemento 'ComposDeCombustibleNoFosilEnTurbosina'.")
        if product_key == ProductEnum.PR15.value and subp_key not in {
            SubProductEnum.SP20.value, SubProductEnum.SP21.value,
            SubProductEnum.SP36.value, SubProductEnum.SP39.value,
            SubProductEnum.SP40.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto deben ser"
                    f"{SubProductEnum.SP20.value}, {SubProductEnum.SP21.value}, {SubProductEnum.SP36.value}"
                    f", {SubProductEnum.SP39.value}, {SubProductEnum.SP40.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto deben ser
            # {SubProductEnum.SP20.value}, {SubProductEnum.SP21.value},
            # {SubProductEnum.SP36.value}, {SubProductEnum.SP39.value}, {SubProductEnum.SP40.value}.")
        if product_key == ProductEnum.PR08.value:
            pr08_subp = {
                SubProductEnum.SP1.value, SubProductEnum.SP2.value,
                SubProductEnum.SP3.value, SubProductEnum.SP4.value,
                SubProductEnum.SP5.value, SubProductEnum.SP6.value,
                SubProductEnum.SP7.value, SubProductEnum.SP8.value,
                SubProductEnum.SP9.value, SubProductEnum.SP10.value,
                SubProductEnum.SP11.value, SubProductEnum.SP12.value,
                SubProductEnum.SP13.value, SubProductEnum.SP14.value,
                SubProductEnum.SP15.value
                }
            if subp_key not in pr08_subp:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        f"los valores en ClaveSubProducto deben ser {pr08_subp}."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # los valores en ClaveSubProducto deben ser {pr08_subp}.")
            if (self.current_product.get("DensidadDePetroleo")
                or self.current_product.get("ComposDeAzufreEnPetroleo")) is None:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        f"deben existir los elementos 'DensidadDePetroleo' y 'ComposDeAzufreEnPetroleo'."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # deben existir los elementos 'DensidadDePetroleo' y 'ComposDeAzufreEnPetroleo'.")
        if product_key == ProductEnum.PR09.value:
            pr09_subp = {
                SubProductEnum.SP27.value, SubProductEnum.SP28.value,
                SubProductEnum.SP29.value, SubProductEnum.SP37.value,
                SubProductEnum.SP38.value, SubProductEnum.SP41.value,
                SubProductEnum.SP42.value, SubProductEnum.SP43.value,
                SubProductEnum.SP44.value, SubProductEnum.SP17.value,
                }
            if subp_key not in pr09_subp:
                self._product_error(
                    custom_message=(
                        f"Error: para ClaveProducto {product_key}"
                        f"los valores en ClaveSubProducto deben ser {pr09_subp}."
                    )
                )
                # self.catch_error(
                #     err_type=ProductoError,
                #     err_message=f"Error: para ClaveProducto {product_key}
                # los valores en ClaveSubProducto deben ser {pr09_subp}.")
        if product_key in {
            ProductEnum.PR09.value,
            ProductEnum.PR10.value} and self.caracter in petroleo_caracteres and self.current_product.get("GasNaturalOCondensados") is None:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {ProductEnum.PR09.value, ProductEnum.PR10.value}"
                    "debe existir el elemento 'GasNaturalOCondensados'."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {ProductEnum.PR09.value,
            # ProductEnum.PR10.value} debe existir el elemento 'GasNaturalOCondensados'.")
        if product_key in {
            ProductEnum.PR10.value,
            ProductEnum.PR14.value} and subp_key:
            self._product_error(
                custom_message=(
                    f"Error: ClaveProducto {ProductEnum.PR10.value, ProductEnum.PR14.value}"
                    "no cuenta con ClaveSubProducto."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: ClaveProducto {ProductEnum.PR10.value,
            # ProductEnum.PR14.value} no cuenta con ClaveSubProducto.")
        if product_key == ProductEnum.PR11.value and subp_key not in {
            SubProductEnum.SP34.value, SubProductEnum.SP35.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    f" ClaveSubProducto deben ser {SubProductEnum.SP34.value}, {SubProductEnum.SP35.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en
            # ClaveSubProducto deben ser {SubProductEnum.SP34.value}, {SubProductEnum.SP35.value}.")
        if product_key == ProductEnum.PR12.value and (
            self.current_product.get("ComposDePropanoEnGasLP") or
            self.current_product.get("ComposDeButanoEnGasLP")
        ) is None:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    "deben existir los elementos 'ComposDePropanoEnGasLP' y 'ComposDeButanoEnGasLP'."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key}
            # deben existir los elementos 'ComposDePropanoEnGasLP' y 'ComposDeButanoEnGasLP'.")
        if product_key == ProductEnum.PR13.value and subp_key not in {
            SubProductEnum.SP30.value, SubProductEnum.SP31.value,
            SubProductEnum.SP32.value, SubProductEnum.SP33.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto deben ser"
                    f" {SubProductEnum.SP30.value}, {SubProductEnum.SP31.value}"
                    f", {SubProductEnum.SP32.value}, {SubProductEnum.SP33.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto
            # deben ser {SubProductEnum.SP30.value}, {SubProductEnum.SP31.value},
            # {SubProductEnum.SP32.value}, {SubProductEnum.SP33.value}.")
        if product_key == ProductEnum.PR16.value and subp_key not in {
            SubProductEnum.SP48.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    f"ClaveSubProducto debe ser {SubProductEnum.SP48.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key}
            # el valore en ClaveSubProducto debe ser {SubProductEnum.SP48.value}.")
        if product_key == ProductEnum.PR17.value and subp_key not in {
            SubProductEnum.SP45.value, SubProductEnum.SP46.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    f"ClaveSubProducto deben ser {SubProductEnum.SP45.value}, {SubProductEnum.SP46.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key} los valores en ClaveSubProducto
            # deben ser {SubProductEnum.SP45.value}, {SubProductEnum.SP46.value}.")
        if product_key == ProductEnum.PR18.value and subp_key not in {
            SubProductEnum.SP26.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    f"ClaveSubProducto debe ser {SubProductEnum.SP26.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key}
            # el valore en ClaveSubProducto debe ser {SubProductEnum.SP26.value}.")
        if product_key == ProductEnum.PR19.value and subp_key not in {
            SubProductEnum.SP42.value}:
            self._product_error(
                custom_message=(
                    f"Error: para ClaveProducto {product_key} los valores en"
                    f"ClaveSubProducto debe ser {SubProductEnum.SP42.value}."
                )
            )
            # self.catch_error(
            #     err_type=ProductoError,
            #     err_message=f"Error: para ClaveProducto {product_key}
            # el valore en ClaveSubProducto debe ser {SubProductEnum.SP42.value}.")

    def _current_product(self) -> dict:
        return self.products[self._gen_index]

    def _next_product(self) -> bool:
        return self._gen_index < self.products_len

    def _update_index(self) -> None:
        self._gen_index += 1
        if self._next_product():
            self.current_product = self.products[self._gen_index]

    def catch_error(self, err_type: BaseException, err_message: str, source: Optional[str] = None) -> None:
        """Store given error in class error list.
        :param err_type: Class from BaseException inherit.\n
        :param err_message: Message of the given error.\n
        :param source: Source reference of the error\n
        :return: None."""
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message,
            # "source": source,
            "source": f"Producto[{self.products.index(self.current_product)}].{source}"
            }

    def _product_key_error(
            self,
            product_key: Union[ProductEnum, List[str], str],
            subproduct_key: Union[str, List[str]],
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param product_key: ClaveProducto element.\n
        :param subproduct_key: ClaveSubProducto element.\n
        :param value: value that unmatch range.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ClaveProductoError,
            err_message=f"Error: clave {subproduct_key} solo debe expresarse en ClaveProducto {product_key}.",
            source=source
        )

    def _product_error(
            self,
            custom_message: str,
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param product_key: ClaveProducto element.\n
        :param subproduct_key: ClaveSubProducto element.\n
        :param value: value that unmatch range.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ProductoError,
            err_message=custom_message,
            source=source
        )

    def _min_max_value_error(
            self,
            key: str,
            value: Union[int, float, str],
            min_val: Union[int, float, str],
            max_val: Union[int, float, str],
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that unmatch range.\n
        :param min_val: minimium value.\n
        :param max_val: maximum value.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ValorMinMaxError,
            err_message=f"Error: clave {key} con valor {value} no tiene el valor min {min_val} ó max {max_val}.",
            source=source
        )

    def _longitud_error(
            self,
            key: str,
            value: Union[int, float],
            min_long: Union[int, float],
            max_long: Union[int, float],
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that unmatch lenght.\n
        :param min_long: minimium lenght.\n
        :param max_long: maximum lenght.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=LongitudError,
            err_message=f"Error: clave {key} con valor {value} no tiene una longitud min {min_long} ó max {max_long}.",
            source=source
        )

    def _value_error(
            self,
            key: str,
            value: Union[int, float],
            source: Optional[str] = None,
        ) -> None:
        """Store ValorError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that is invalid.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ValorError,
            err_message=f"Error: valor '{value}' en clave {key} no válido.",
            source=source
        )

    def _regex_error(
            self,
            key: str,
            value: Union[int, float],
            pattern: str,
            source: Optional[str] = None,
        ) -> None:
        """Store RegexError in self.errors.\n
        :param key: Dict Key element.\n
        :param value: value that unmatch regex.\n
        :param patter: Reggex pattern.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=RegexError,
            err_message=f"Error: clave {key} con valor {value} no cumple con el patrón {pattern}",
            source=source
        )


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
