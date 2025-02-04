import re

from complements.constants import (ADUANAL_PEDIMENTO, CFDI_REGEX, DATE_REGEX,
                                   FOLIO_CERTIFIED_REGEX, FOLIO_DICTAMEN_REGEX,
                                   IMPORT_PERMISSION_REGEX, INTERN_SPOT_REGEX,
                                   MEASURE_UNIT, PERMISSION_PROOVE_REGEX,
                                   RFC_PERSONA_MORAL_REGEX, RFC_REGEX,
                                   TRANSPORT_PERM_REGEX, UTC_FORMAT_REGEX)
from complements.enumerators import (AduanaEntrance, CfdiType, ComplementType,
                                     CountryCode, IncotermCode)
from custom_exceptions import LongitudError, RegexError, ValorMinMaxError
from decorators import exception_wrapper
from dict_type_validator import DictionaryTypeValidator
from dict_types import (compl_foreign_pedimentos, complement,
                        complement_certified, complement_cfdis,
                        complement_dictamen, complement_foreign,
                        complement_national, complement_transport)


# TODO IMPORTANTISIMO< HICE LA BASE BAASADO EN EL COMPLEMENTO ALMACENAMIENTO
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
        self._errors_list = []

    def validate_complemento(self) -> None:
        if self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_transporte()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self.__validate_national_cfdi()
            self._validate_aclaracion()
            self._validate_extranjero()
            self.__validate_extranjero_pedimentos()

            self._update_index()
            self.validate_complemento()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement, dict_type=complement):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)

    @exception_wrapper
    def _validate_tipo_complemento(self) -> None:
        comp_type = self.current_complement.get("TipoComplemento")

        if comp_type not in [en.value for en in ComplementType]:
            self.catch_error(err_type=TypeError, err_message=f"Error: TipoComplemento {comp_type} no válido.")
            # raise TypeError(f"Error: TipoComplemento {comp_type} no válido.")

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

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transportation,
                                                               dict_type=complement_transport):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
        if transp_permission is None:
            self.catch_error(err_type=KeyError, err_message="Error: clave 'PermisoTransporte' no encontrada.")
            # raise KeyError("Error: clave 'PermisoTransporte' no encontrada.")
        if trans_fee is None:
            self.catch_error(KeyError, "Error: clave 'TarifaDeTransporte' no encontrada.")
            # raise KeyError("Error: clave 'TarifaDeTransporte' no encontrada.")

        if not re.match(TRANSPORT_PERM_REGEX, transp_permission):
            self.catch_error(RegexError, f"Error: valor 'PermisoTransporte' no cumple con el patron {TRANSPORT_PERM_REGEX}")
            # raise RegexError(f"Error: valor 'PermisoTransporte' no cumple con el patron {TRANSPORT_PERM_REGEX}")
        if 6 <= len(vehicle_key) <= 12:
            self.catch_error(LongitudError, "Error: 'ClaveVehiculo' no cumple con la longitud min 6 o max 12.")
            # raise LongitudError("Error: 'ClaveVehiculo' no cumple con la longitud min 6 o max 12.")
        if 0 <= trans_fee <= 1000000000000:
            self.catch_error(ValorMinMaxError, "Error: valor 'TarifaDeTransporte' no se encuentra en el rango min 0 o max 1000000000000.")
            # raise ValorMinMaxError(
            #     "Error: valor 'TarifaDeTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_cap_fee and 0 <= trans_cap_fee <= 1000000000000:
            self.catch_error(ValorMinMaxError, "Error: valor 'CargoPorCapacidadTransporte' no se encuentra en el rango min 0 o max 1000000000000.")
            # raise ValorMinMaxError(
            #     "Error: valor 'CargoPorCapacidadTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_use_fee and 0 <= trans_use_fee <= 1000000000000:
            self.catch_error(ValorMinMaxError, "Error: valor 'CargoPorUsoTrans' no se encuentra en el rango min 0 o max 1000000000000.")
            # raise ValorMinMaxError(
            #     "Error: valor 'CargoPorUsoTrans' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_volum_charge and 0 <= trans_volum_charge <= 1000000000000:
            self.catch_error(ValorMinMaxError, "Error: valor 'CargoVolumetricoTransporte' no se encuentra en el rango min 0 o max 1000000000000.")
            # raise ValorMinMaxError(
            #     "Error: valor 'CargoVolumetricoTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )

# TODO preguntar reglas para aquellos que deben llevar dictamen dentro de su tipo de complemento
    @exception_wrapper
    def _validate_dictamen(self) -> None:
        if (dictamen := self.current_complement.get("Dictamen")) is None:
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=dictamen,
                                                               dict_type=complement_dictamen):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
        dictamen_rfc = dictamen.get("RfcDictamen")
        dictamen_lote = dictamen.get("LoteDictamen")
        dictamen_folio = dictamen.get("NumeroFolioDictamen")
        dictamen_date = dictamen.get("FechaEmisionDictamen")
        dictamen_result = dictamen.get("ResultadoDictamen")

        if dictamen_rfc is None:
            self.catch_error(KeyError, "Error: clave 'RfcDictamen no encontrada.")
            # raise KeyError("Error: clave 'RfcDictamen no encontrada.")
        if dictamen_lote is None:
            self.catch_error(KeyError, "Error: clave 'LoteDictamen' no encontrada.")
            # raise KeyError("Error: clave 'LoteDictamen' no encontrada.")
        if dictamen_folio is None:
            self.catch_error(KeyError, "Error: clave 'NumeroFolioDictamen' no encontrada.")
            # raise KeyError("Error: clave 'NumeroFolioDictamen' no encontrada.")
        if dictamen_date is None:
            self.catch_error(KeyError, "Error: clave 'FechaEmisionDictamen' no encontrada.")
            # raise KeyError("Error: clave 'FechaEmisionDictamen' no encontrada.")
        if dictamen_result is None:
            self.catch_error(KeyError, "Error: clave 'ResultadoDictamen' no encontrada.")
            # raise KeyError("Error: clave 'ResultadoDictamen' no encontrada.")

        if not re.match(RFC_PERSONA_MORAL_REGEX, dictamen_rfc):
            self.catch_error(RegexError, f"Error: clave 'RfcDictamen' con valor '{dictamen_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}'")
            # raise RegexError(
            #     f"Error: clave 'RfcDictamen' con valor '{dictamen_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}'"
            #     )
        if not 1 <= len(dictamen_lote) <= 50:
            self.catch_error(LongitudError, f"Error: clave 'LoteDictamen' con valor '{dictamen_lote}' no se encuentra en el rango min 1 o max 50.")
            # raise LongitudError(
            #     f"Error: clave 'LoteDictamen' con valor '{dictamen_lote}' no se encuentra en el rango min 1 o max 50."
            # )
        if not re.match(FOLIO_DICTAMEN_REGEX, dictamen_folio):
            self.catch_error(RegexError, f"Error: clave 'NumeroFolioDictamen' con valor {dictamen_folio} no cumple con el regex {FOLIO_DICTAMEN_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'NumeroFolioDictamen' con valor {dictamen_folio} no cumple con el regex {FOLIO_DICTAMEN_REGEX}",
            # )
        if not re.match(DATE_REGEX, dictamen_date):
            self.catch_error(RegexError, f"Error: clave 'FechaEmisionDictamen' con valor {dictamen_date} no cumple con el regex {UTC_FORMAT_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'FechaEmisionDictamen' con valor {dictamen_date} no cumple con el regex {UTC_FORMAT_REGEX}"
            # )
        if not 10 <= len(dictamen_result) <= 300:
            self.catch_error(LongitudError, f"Error: clave 'ResultadoDictamen' con valor {dictamen_result} no se encuentra en el rango min 10 o max 300.")
            # raise LongitudError(
            #     f"Error: clave 'ResultadoDictamen' con valor {dictamen_result} no se encuentra en el rango min 10 o max 300."
            # )

    @exception_wrapper
    def _validate_certificado(self) -> None:
        if (certified := self.current_complement.get("Certificado")) is None:
            return

        certified_rfc = certified.get("RfcCertificado")
        certified_folio = certified.get("NumeroFolioCertificado")
        certified_date = certified.get("FechaEmisionCertificado")
        certified_result = certified.get("ResultadoCertificado")

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=certified,
                                                               dict_type=complement_certified):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
        if certified_rfc is None:
            self.catch_error(KeyError, "Error: clave 'RfcCertificado' no encontrada.")
            # raise KeyError("Error: clave 'RfcCertificado' no encontrada.")
        if certified_folio is None:
            self.catch_error(KeyError, "Error: clave 'NumeroFolioCertificado' no encontrada.")
            # raise KeyError("Error: clave 'NumeroFolioCertificado' no encontrada.")
        if certified_date is None:
            self.catch_error(KeyError, "Error: clave 'FechaEmisionCertificado' no encontrada.")
            # raise KeyError("Error: clave 'FechaEmisionCertificado' no encontrada.")
        if certified_result is None:
            self.catch_error(KeyError, "Error: clave 'ResultadoCertificado' no encontrada.")
            # raise KeyError("Error: clave 'ResultadoCertificado' no encontrada.")

        if not re.match(RFC_PERSONA_MORAL_REGEX, certified_rfc):
            self.catch_error(RegexError, f"Error: clave 'RfcCertificado' con valor {certified_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'RfcCertificado' con valor {certified_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}"
            #     )
        if not re.match(FOLIO_CERTIFIED_REGEX, certified_folio):
            self.catch_error(RegexError, f"Error: clave 'NumeroFolioCertificado' con valor {certified_folio} no cumple con el regex {FOLIO_CERTIFIED_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'NumeroFolioCertificado' con valor {certified_folio} no cumple con el regex {FOLIO_CERTIFIED_REGEX}"
            #     )
        if not re.match(DATE_REGEX, certified_date):
            self.catch_error(RegexError, f"Error: clave 'FechaEmisionCertificado' con valor {certified_date} no cumple con el regex {DATE_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'FechaEmisionCertificado' con valor {certified_date} no cumple con el regex {DATE_REGEX}"
            # )
        if not 10 <= len(certified_result) <= 300:
            self.catch_error(LongitudError, f"Error: clave 'ResultadoCertificado' con valor {certified_result} no se encuentra en el rango min 10 o max 300.")
            # raise LongitudError(
            #     f"Error: clave 'ResultadoCertificado' con valor {certified_result} no se encuentra en el rango min 10 o max 300."
            # )

    @exception_wrapper
    def _validate_nacional(self) -> None:
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            supplier_permission = national_item.get("PermisoProveedor")
            # cfdis = national_item.get("CFDIs")

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                dict_type=complement_national):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
            if custom_client_rfc is None:
                self.catch_error(KeyError, "Error: clave 'RfcClienteOProveedor' no encontrada.")
                # raise KeyError("Error: clave 'RfcClienteOProveedor' no encontrada.")
            if custom_client_name is None:
                self.catch_error(KeyError, "Error: clave 'NombreClienteOProveedor' no encontrada.")
                # raise KeyError("Error: clave 'NombreClienteOProveedor' no encontrada.")

            if not re.match(RFC_REGEX, custom_client_rfc):
                self.catch_error(RegexError, f"Error: clave 'RfcClienteOProveedor' con valor {custom_client_rfc} no cumple con el regex {RFC_REGEX}")
                # raise RegexError(
                #     f"Error: clave 'RfcClienteOProveedor' con valor {custom_client_rfc} no cumple con el regex {RFC_REGEX}"
                #     )
            if not 10 <= len(custom_client_name) <= 150:
                self.catch_error(LongitudError, f"Error: clave 'NombreClienteOProveedor' con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300.")
                # raise LongitudError(
                #     f"Error: clave 'NombreClienteOProveedor' con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300."
                #     )
            if supplier_permission and not re.match(PERMISSION_PROOVE_REGEX, supplier_permission):
                self.catch_error(RegexError, f"Error: clave 'PermisoProveedor' con valor {supplier_permission} no cumple con el regex {PERMISSION_PROOVE_REGEX}")
                # raise RegexError(
                #     f"Error: clave 'PermisoProveedor' con valor {supplier_permission} no cumple con el regex {PERMISSION_PROOVE_REGEX}"
                # )

            # if cfdis:
            #     print("HAY CFDI")
            #     print("HAY CFDI")
            #     print("HAY CFDI")
            #     print("HAY CFDI")
            #     print("HAY CFDI")
            #     print(cfdis)
            #     for cfdi in cfdis:
            #         self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_national_cfdi(self) -> None:
        if (national := self.current_complement.get("Nacional")) is None:
            return
        for national_item in national:
            if cfdis := national_item.get("CFDIs"):
                for cfdi in cfdis:
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

                    if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi,
                                                                        dict_type=complement_cfdis):
                        type_err = err.get("type_err")
                        err_message = err.get("err_message")
                        self.catch_error(err_type=type_err, err_message=err_message)
                    if documented_volum:
                        num_value = documented_volum.get("ValorNumerico")
                        measure_unit = documented_volum.get("UnidadDeMedida")
                        if num_value is None:
                            self.catch_error(KeyError, "Error: clave 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'.")
                        if measure_unit is None:
                            self.catch_error(KeyError, "Error: clave 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'.")
                    if cfdi_val is None:
                        self.catch_error(KeyError, "Error: clave 'Cfdi' no se encuentra.")
                        # raise KeyError("Error: clave 'Cfdi' no se encuentra.")
                    if cfdi_type is None:
                        self.catch_error(KeyError, "Error: clave 'TipoCfdi' no se encuentra.")
                        # raise KeyError("Error: clave 'TipoCfdi' no se encuentra.")
                    if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
                        self.catch_error(KeyError, f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válido.")
                        # raise KeyError(f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válido.")
                    if transaction_date is None:
                        self.catch_error(KeyError, "Error: clave 'FechaYHoraTransaccion' no se encuentra.")
                        # raise KeyError("Error: clave 'FechaYHoraTransaccion' no se encuentra.")
                    if documented_volum is None:
                        self.catch_error(KeyError, "Error: clave 'VolumenDocumentado' no se encuentra.")
                        # raise KeyError("Error: clave 'VolumenDocumentado' no se encuentra.")
                    if not re.match(CFDI_REGEX, cfdi_val):
                        self.catch_error(RegexError, f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}")
                        # raise RegexError(f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}")
                    if purchase_price and not 1 <= purchase_price <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'PrecioCompra' con valor '{purchase_price}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'PrecioCompra' con valor '{purchase_price}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if consideration and not 1 <= consideration <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'Contraprestacion' con valor '{consideration}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'Contraprestacion' con valor '{consideration}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if alm_fee and not 1 <= alm_fee <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'Contraprestacion' con valor '{alm_fee}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'Contraprestacion' con valor '{alm_fee}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if alm_cap_fee and not 1 <= alm_cap_fee <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'CargoPorCapacidadALmac' con valor '{alm_cap_fee}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'CargoPorCapacidadALmac' con valor '{alm_cap_fee}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if alm_use_fee and not 1 <= alm_use_fee <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'CargoPorUsoAlmac' con valor '{alm_use_fee}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'CargoPorUsoAlmac' con valor '{alm_use_fee}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if alm_volum_fee and not 1 <= alm_volum_fee <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'CargoVolumetricoAlmac' con valor '{alm_volum_fee}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'CargoVolumetricoAlmac' con valor '{alm_volum_fee}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if discount and not 1 <= discount <= 1000000000000:
                        self.catch_error(ValorMinMaxError, f"Error: Clave 'Descuento' con valor '{discount}' no tiene el valor min 0 o max 1000000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: Clave 'Descuento' con valor '{discount}' no tiene el valor min 0 o max 1000000000000."
                        # )
                    if not re.match(UTC_FORMAT_REGEX, transaction_date):
                        self.catch_error(RegexError, f"Error: clave 'FechaYHoraTransaccion' con valor {transaction_date} no cumple con el regex {UTC_FORMAT_REGEX}")
                        # raise RegexError(
                        #     f"Error: clave 'FechaYHoraTransaccion' con valor {transaction_date} no cumple con el regex {UTC_FORMAT_REGEX}"
                        # )
                    if not 0 <= num_value <= 100000000000:
                        self.catch_error(ValorMinMaxError, f"Error: clave 'ValorNumerico' con valor {num_value} no tiene el valor min 0 o max 100000000000.")
                        # raise ValorMinMaxError(
                        #     f"Error: clave 'ValorNumerico' con valor {num_value} no tiene el valor min 0 o max 100000000000."
                        #     )
                    if not re.match(MEASURE_UNIT, measure_unit):
                        self.catch_error(RegexError, f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")
                        # raise RegexError(
                        #     f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                        #     )

    @exception_wrapper
    def _validate_extranjero(self) -> None:
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return
        import_permission = foreign.get("PermisoImportacion")
        pedimentos = foreign.get("Pedimentos")

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=foreign, dict_type=complement_foreign):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
        if import_permission is None:
            self.catch_error(KeyError, "Error: clave 'PermisoImportacion' no se encuentra.")
            # raise KeyError("Error: clave 'PermisoImportacion' no se encuentra.")

        if not re.match(IMPORT_PERMISSION_REGEX, import_permission):
            self.catch_error(RegexError, f"Error: clave 'PermisoImportacion' con valor {import_permission} no cumple con el regex {IMPORT_PERMISSION_REGEX}")
            # raise RegexError(
            #     f"Error: clave 'PermisoImportacion' con valor {import_permission} no cumple con el regex {IMPORT_PERMISSION_REGEX}"
            # )

        # for pedimento in pedimentos:
        #     self.__validate_pedimentos(pedimento=pedimento)

    @exception_wrapper
    def __validate_extranjero_pedimentos(self) -> None:
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return
        if (pedimentos := foreign.get("Pedimentos")) is None:
            return

        for pedimento in pedimentos:
            intern_point = pedimento.get("PuntoDeInternacion")
            origin_country = pedimento.get("PaisOrigen")
            aduanal_transp = pedimento.get("MedioDeTransEntraAduana")
            aduanal_pedimento = pedimento.get("PedimentoAduanal")
            incoterm = pedimento.get("Incoterms")
            import_price = pedimento.get("PrecioDeImportacion")
            documented_volume = pedimento.get("VolumenDocumentado")

            if documented_volume:
                num_value = documented_volume.get("ValorNumerico")
                measure_unit = documented_volume.get("UnidadDeMedida")
                if num_value is None:
                    self.catch_error(KeyError, "Error: clave 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'.")
                if measure_unit is None:
                    self.catch_error(KeyError, "Error: clave 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'.")
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=pedimento,
                                                                dict_type=compl_foreign_pedimentos):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
            if intern_point is None:
                self.catch_error(KeyError, "Error: clave 'PuntoDeInternacion' no se encuentra.")
                # raise KeyError("Error: clave 'PuntoDeInternacion' no se encuentra.")
            if origin_country is None:
                self.catch_error(KeyError, "Error: clave 'PaisOrigen' no se encuentra.")
                # raise KeyError("Error: clave 'PaisOrigen' no se encuentra.")
            if aduanal_pedimento is None:
                self.catch_error(KeyError, "Error: clave 'PedimentoAduanal' no se encuentra.")
                # raise KeyError("Error: clave 'PedimentoAduanal' no se encuentra.")
            if incoterm is None:
                self.catch_error(KeyError, "Error: clave 'Incoterms' no se encuentra.")
                # raise KeyError("Error: clave 'Incoterms' no se encuentra.")
            if import_price is None:
                self.catch_error(KeyError, "Error: clave 'PrecioDeImportacion' no se encuentra.")
                # raise KeyError("Error: clave 'PrecioDeImportacion' no se encuentra.")
            if documented_volume is None:
                self.catch_error(KeyError, "Error: clave 'VolumenDocumentado' no se encuentra.")
                # raise KeyError("Error: clave 'VolumenDocumentado' no se encuentra.")

            if not re.match(INTERN_SPOT_REGEX, intern_point):
                self.catch_error(RegexError, f"Error: clave 'PuntoDeInternacion' con valor {intern_point} no cumple con el patron {INTERN_SPOT_REGEX}")
                # raise RegexError(f"Error: clave 'PuntoDeInternacion' con valor {intern_point} no cumple con el patron {INTERN_SPOT_REGEX}")
            if not 2 <= intern_point <= 3:
                self.catch_error(ValorMinMaxError, f"Error: clave 'PuntoDeInternacion' con valor {intern_point} no tiene la longitud min 2 o max 3.")
                # raise ValorMinMaxError(
                #     f"Error: clave 'PuntoDeInternacion' con valor {intern_point} no tiene la longitud min 2 o max 3."
                # )
            if origin_country not in CountryCode:
                self.catch_error(ValueError, f"Error: valor '{origin_country}' en clave 'PaisOrigen' no válido.")
                # raise ValueError(f"Error: valor '{origin_country}' en clave 'PaisOrigen' no válido.")
            if aduanal_transp not in [item.value for item in AduanaEntrance]:
                self.catch_error(ValueError, f"Error: valor '{aduanal_transp}' en clave 'MedioDeTransporteAduana' no válido.")
                # raise ValueError(f"Error: valor '{aduanal_transp}' en clave 'MedioDeTransporteAduana' no válido.")
            if not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
                self.catch_error(RegexError, f"Error: clave 'PedimentoAduanal' con valor {aduanal_pedimento} no cumple con el patron {ADUANAL_PEDIMENTO}")
                # raise RegexError(
                #     f"Error: clave 'PedimentoAduanal' con valor {aduanal_pedimento} no cumple con el patron {ADUANAL_PEDIMENTO}"
                # )
            if len(aduanal_pedimento) != 21:
                self.catch_error(LongitudError, f"Error: clave 'PedimentoAduanal' con valor '{aduanal_pedimento} no cumple con la longitud de 21.'")
                # raise LongitudError(
                #     f"Error: clave 'PedimentoAduanal' con valor '{aduanal_pedimento} no cumple con la longitud de 21.'"
                # )
            if incoterm not in IncotermCode.__members__:
                self.catch_error(ValueError, f"Error: clave 'Incoterms' con valor {incoterm} no válido.")
                # raise ValueError(f"Error: clave 'Incoterms' con valor {incoterm} no válido.")
            if not 0 <= import_price <= 100000000000:
                self.catch_error(ValorMinMaxError, f"Error: clave 'PrecioDeImportacion' con valor {import_price} no tiene el valor min 0 o max 100000000000.")
                # raise ValorMinMaxError(
                #     f"Error: clave 'PrecioDeImportacion' con valor {import_price} no tiene el valor min 0 o max 100000000000."
                #     )
            if not 0 <= num_value <= 100000000000:
                self.catch_error(ValorMinMaxError, f"Error: clave 'ValorNumerico' con valor {num_value} no está en el valor min 0 o max 100000000000.")
                # raise ValorMinMaxError(
                #     f"Error: clave 'ValorNumerico' con valor {num_value} no está en el valor min 0 o max 100000000000."
                #     )
            if not re.match(MEASURE_UNIT, measure_unit):
                self.catch_error(RegexError, f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")
                # raise RegexError(
                #     f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                #     )

    @exception_wrapper
    def _validate_aclaracion(self) -> None:
        if (clarif := self.current_complement.get("Aclaracion")) is None:
            return
        if not 10 <= len(clarif) <= 600:
            self.catch_error(LongitudError, "Error: valor 'Aclaracion' no cumple con la longitud min 10 o max 600.")
            # raise LongitudError("Error: valor 'Aclaracion' no cumple con la longitud min 10 o max 600.")

    def _current_complement(self) -> dict:
        return self.current_complement[self._comp_index]

    def _next_complement(self) -> bool:
        return self._comp_index < self.comp_len

    def _update_index(self) -> None:
        self._comp_index += 1
        if self._next_complement():
            self.current_complement = self.complement[self._comp_index]

    def catch_error(self, err_type: BaseException, err_message: str) -> None:
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message
            }

    @property
    def errors(self) -> dict:
        """Get errors from product validation obj."""
        return self._errors

    def get_error_list(self) -> list:
        return self._errors_list

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in product validation obj."""
        if "excepciones" in errors:
            errors.pop("excepciones")
            if "excepciones" in self._errors:
                self._errors["excepciones"].append(errors)
            if "excepciones" not in self._errors:
                self._errors["excepciones"] = [errors]
                # self._errors["excepciones"].append(errors)

        self._errors_list.append(errors)
        self._errors[errors["type_error"]] = errors["error"]
