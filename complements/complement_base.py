import re 
from complements.enumerators import ComplementType, CfdiType
from dict_types import complement_transport
from dict_type_validator import DictionaryTypeValidator
from custom_exceptions import LongitudError, RegexError, ValorMinMaxError
from complements.constants import TRANSPORT_PERM_REGEX, RFC_PERSONA_MORAL_REGEX, FOLIO_DICTAMEN_REGEX, DATE_REGEX, FOLIO_CERTIFIED_REGEX, RFC_REGEX, PERMISSION_PROOVE_REGEX, CFDI_REGEX, UTC_FORMAT_REGEX, MEASURE_UNIT
from decorators import exception_wrapper


# TODO los valores son Almacenamiento, CDLR, Comercializacion, Distribucion
class ComplementBuilder:
    """Base class for complement types according type."""
    def __init__(self, complement_type: str, complement_dict: list):
        self._comp_index = 0
        self.complement = complement_dict
        self.complement_type = complement_type
        self.current_complement = complement_dict[self._comp_index]
        self.comp_len = len(complement_dict)
        self.exc_func = set()
        self._errors = {}

# TODO implementar validar extranjero
    def validate_complemento(self) -> None:
        if self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_transporte()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_aclaracion()
            # self._validate_extranjero()

            self._update_index()
            self.validate_complemento()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement, dict_type=complement_transport)

    @exception_wrapper
    def _validate_tipo_complemento(self) -> None:
        comp_type = self.current_complement.get("TipoComplemento")

        if comp_type not in [en.value for en in ComplementType]:
            raise TypeError(f"Error: TipoComplemento {comp_type} no válido.")

    @exception_wrapper
    def _validate_transporte(self) -> None:
        if (transportation := self.current_complement.get("Transporte")) is None:
            return
        transp_permission = transportation.get("PermisoTransporte")
        vehicle_key = transportation.get("ClaveVehiculo")
        trans_fee = transportation.get("TarifaDeTransporte")
        trans_cap_fee = transportation.get("CargoPorCapacidadTransporte")
        trans_use_fee = transportation.get("CargoPorUsoTrans")
        trans_volum_charge = transportation.get("CargoVolumetricoTransporte")

        if transp_permission is None:
            raise KeyError("Error: clave 'PermisoTransporte' no encontrada.")
        if trans_fee is None:
            raise KeyError("Error: clave 'TarifaDeTransporte' no encontrada.")

        if not re.match(TRANSPORT_PERM_REGEX, transp_permission):
            raise RegexError(f"Error: valor 'PermisoTransporte' no cumple con el patron {TRANSPORT_PERM_REGEX}")
        if 6 <= len(vehicle_key) <= 12:
            raise LongitudError("Error: 'ClaveVehiculo' no cumple con la longitud min 6 o max 12.")
        if 0 <= trans_fee <= 1000000000000:
            raise ValorMinMaxError(
                "Error: valor 'TarifaDeTransporte' no se encuentra en el rango min 0 o max 1000000000000."
                )
        if trans_cap_fee and 0 <= trans_cap_fee <= 1000000000000:
            raise ValorMinMaxError(
                "Error: valor 'CargoPorCapacidadTransporte' no se encuentra en el rango min 0 o max 1000000000000."
                )
        if trans_use_fee and 0 <= trans_use_fee <= 1000000000000:
            raise ValorMinMaxError(
                "Error: valor 'CargoPorUsoTrans' no se encuentra en el rango min 0 o max 1000000000000."
                )
        if trans_volum_charge and 0 <= trans_volum_charge <= 1000000000000:
            raise ValorMinMaxError(
                "Error: valor 'CargoVolumetricoTransporte' no se encuentra en el rango min 0 o max 1000000000000."
                )

# TODO preguntar reglas para aquellos que deben llevar dictamen dentro de su tipo de complemento
    @exception_wrapper
    def _validate_dictamen(self) -> None:
        if (dictamen := self.current_complement.get("Dictamen")) is None:
            return

        dictamen_rfc = dictamen.get("RfcDictamen")
        dictamen_lote = dictamen.get("LoteDictamen")
        dictamen_folio = dictamen.get("NumeroFolioDictamen")
        dictamen_date = dictamen.get("FechaEmisionDictamen")
        dictamen_result = dictamen.get("ResultadoDictamen")

        if dictamen_rfc is None:
            raise KeyError("Error: clave 'RfcDictamen no encontrada.")
        if dictamen_lote is None:
            raise KeyError("Error: clave 'LoteDictamen' no encontrada.")
        if dictamen_folio is None:
            raise KeyError("Error: clave 'NumeroFolioDictamen' no encontrada.")
        if dictamen_date is None:
            raise KeyError("Error: clave 'FechaEmisionDictamen' no encontrada.")
        if dictamen_result is None:
            raise KeyError("Error: clave 'ResultadoDictamen' no encontrada.")

        if not re.match(RFC_PERSONA_MORAL_REGEX, dictamen_rfc):
            raise RegexError(
                f"Error: clave 'RfcDictamen' con valor '{dictamen_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}'"
                )
        if not 1 <= len(dictamen_lote) <= 50:
            raise LongitudError(
                f"Error: clave 'LoteDictamen' con valor '{dictamen_lote}' no se encuentra en el rango min 1 o max 50."
            )
        if not re.match(FOLIO_DICTAMEN_REGEX, dictamen_folio):
            raise RegexError(
                f"Error: clave 'NumeroFolioDictamen' con valor {dictamen_folio} no cumple con el regex {FOLIO_DICTAMEN_REGEX}",
            )
        if not re.match(DATE_REGEX, dictamen_date):
            raise RegexError(
                f"Error: clave 'FechaEmisionDictamen' con valor {dictamen_date} no cumple con el regex {UTC_FORMAT_REGEX}"
            )
        if not 10 <= len(dictamen_result) <= 300:
            raise LongitudError(
                f"Error: clave 'ResultadoDictamen' con valor {dictamen_result} no se encuentra en el rango min 10 o max 300."
            )

    @exception_wrapper
    def _validate_certificado(self) -> None:
        if (certified := self.current_complement.get("Certificado")) is None:
            return

        certified_rfc = certified.get("RfcCertificado")
        certified_folio = certified.get("NumeroFolioCertificado")
        certified_date = certified.get("FechaEmisionCertificado")
        certified_result = certified.get("ResultadoCertificado")

        if certified_rfc is None:
            raise KeyError("Error: clave 'RfcCertificado' no encontrada.")
        if certified_folio is None:
            raise KeyError("Error: clave 'NumeroFolioCertificado' no encontrada.")
        if certified_date is None:
            raise KeyError("Error: clave 'FechaEmisionCertificado' no encontrada.")
        if certified_result is None:
            raise KeyError("Error: clave 'ResultadoCertificado' no encontrada.")

        if not re.match(RFC_PERSONA_MORAL_REGEX, certified_rfc):
            raise RegexError(
                f"Error: clave 'RfcCertificado' con valor {certified_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}"
                )
        if not re.match(FOLIO_CERTIFIED_REGEX, certified_folio):
            raise RegexError(
                f"Error: clave 'NumeroFolioCertificado' con valor {certified_folio} no cumple con el regex {FOLIO_CERTIFIED_REGEX}"
                )
        if not re.match(DATE_REGEX, certified_date):
            raise RegexError(
                f"Error: clave 'FechaEmisionCertificado' con valor {certified_date} no cumple con el regex {DATE_REGEX}"
            )
        if not 10 <= len(certified_result) <= 300:
            raise LongitudError(
                f"Error: clave 'ResultadoCertificado' con valor {certified_result} no se encuentra en el rango min 10 o max 300."
            )

    @exception_wrapper
    def _validate_nacional(self) -> None:
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            supplier_permission = national_item.get("PermisoProveedor")
            cfdis = national_item.get("CFDIs")

            if custom_client_rfc is None:
                raise KeyError("Error: clave 'RfcClienteOProveedor' no encontrada.")
            if custom_client_name is None:
                raise KeyError("Error: clave 'NombreClienteOProveedor' no encontrada.")

            if not re.match(RFC_REGEX, custom_client_rfc):
                raise RegexError(
                    f"Error: clave 'RfcClienteOProveedor' con valor {custom_client_rfc} no cumple con el regex {RFC_REGEX}"
                    )
            if not 10 <= len(custom_client_name) <= 150:
                raise LongitudError(
                    f"Error: clave 'NombreClienteOProveedor' con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300."
                    )
            if supplier_permission and not re.match(PERMISSION_PROOVE_REGEX, supplier_permission):
                raise RegexError(
                    f"Error: clave 'PermisoProveedor' con valor {supplier_permission} no cumple con el regex {PERMISSION_PROOVE_REGEX}"
                )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi: dict) -> None:
        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        purchase_price = cfdi.get("PrecioCompra")
        consideration = cfdi.get("Contraprestacion")
        alm_fee = cfdi.get("CargoPorCapacidadAlmac")
        alm_cap_fee = cfdi.get("CargoPorCapacidadAlmac")
        alm_use_fee = cfdi.get("CargoPorUsoAlmac")
        alm_volum_fee = cfdi.get("CargoVolumetricoAlmac")
        discount = cfdi.get("Descuento")
        transaction_date = cfdi.get("FechaYHoraTransaccion")
        documented_volum = cfdi.get("VolumenDocumentado")
        num_value = documented_volum.get("ValorNumerico")
        measure_unit = documented_volum.get("UnidadDeMedida")

        if cfdi_val is None:
            raise KeyError("Error: clave 'Cfdi' no se encuentra.")
        if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            raise KeyError(f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válido.")
        if transaction_date is None:
            raise KeyError("Error: clave 'FechaYHoraTransaccion' no se encuentra.")
        if documented_volum is None:
            raise KeyError("Error: clave 'VolumenDocumentado' no se encuentra.")
        if num_value is None:
            raise KeyError("Error: clave 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'.")
        if measure_unit is None:
            raise KeyError("Error: clave 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'.")

        if not re.match(CFDI_REGEX, cfdi_val):
            raise RegexError(f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}")
        if purchase_price and not 1 <= purchase_price <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'PrecioCompra' con valor '{purchase_price}' no tiene el valor min 0 o max 1000000000000."
            )
        if consideration and not 1 <= consideration <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'Contraprestacion' con valor '{consideration}' no tiene el valor min 0 o max 1000000000000."
            )
        if alm_fee and not 1 <= alm_fee <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'Contraprestacion' con valor '{alm_fee}' no tiene el valor min 0 o max 1000000000000."
            )
        if alm_cap_fee and not 1 <= alm_cap_fee <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'CargoPorCapacidadALmac' con valor '{alm_cap_fee}' no tiene el valor min 0 o max 1000000000000."
            )
        if alm_use_fee and not 1 <= alm_use_fee <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'CargoPorUsoAlmac' con valor '{alm_use_fee}' no tiene el valor min 0 o max 1000000000000."
            )
        if alm_volum_fee and not 1 <= alm_volum_fee <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'CargoVolumetricoAlmac' con valor '{alm_volum_fee}' no tiene el valor min 0 o max 1000000000000."
            )
        if discount and not 1 <= discount <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'Descuento' con valor '{discount}' no tiene el valor min 0 o max 1000000000000."
            )
        if not re.match(UTC_FORMAT_REGEX, transaction_date):
            raise RegexError(
                f"Error: clave 'FechaYHoraTransaccion' con valor {transaction_date} no cumple con el regex {UTC_FORMAT_REGEX}"
            )
        if not 0 <= num_value <= 100000000000:
            raise ValorMinMaxError(
                f"Error: clave 'ValorNumerico' con valor {num_value} no tiene el valor min 0 o max 100000000000."
                )
        if not re.match(MEASURE_UNIT, measure_unit):
            raise RegexError(
                f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                )

    @exception_wrapper
    def _validate_extranjero(self) -> None:
        raise NotImplementedError("No se ha implementado validar extranjero")

    @exception_wrapper
    def _validate_aclaracion(self) -> None:
        if (clarif := self.current_complement.get("Aclaracion")) is None:
            return
        if not 10 <= len(clarif) <= 600:
            raise LongitudError("Error: valor 'Aclaracion' no cumple con la longitud min 10 o max 600.")

    def _current_complement(self) -> dict:
        return self.current_complement[self._comp_index]

    def _next_complement(self) -> bool:
        return self._comp_index < self.comp_len

    def _update_index(self) -> None:
        self._comp_index += 1
        if self._next_complement():
            self.current_complement = self.complement[self._comp_index]

    @property
    def errors(self) -> dict:
        """Get errors from product validation obj."""
        return self._errors

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in product validation obj."""
        self._errors[errors["func_error"]] = errors["error"]
