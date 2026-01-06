"""Base class for components inheratence using Almacenamiento Complement"""
import re
from typing import Optional, Union

from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_REGEX,
                                       DATE_REGEX, FOLIO_CERTIFIED_REGEX,
                                       FOLIO_DICTAMEN_REGEX,
                                       IMPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX, MEASURE_UNIT,
                                       PERMISSION_PROOVE_REGEX,
                                       RFC_PERSONA_MORAL_REGEX, RFC_REGEX,
                                       TRANSPORT_PERM_REGEX, UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType,
                                         ComplementTypeEnum, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import (ClaveError, LongitudError, RegexError,
                                   TipadoError, ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (compl_foreign_pedimentos, complement,
                            complement_certified, complement_cfdis,
                            complement_dictamen, complement_foreign,
                            complement_national, complement_transport)


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
        """Base complement validations"""
        while self._next_complement():
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
            # self.validate_complemento()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement, dict_type=complement):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)

    @exception_wrapper
    def _validate_tipo_complemento(self) -> None:
        comp_type = self.current_complement.get("TipoComplemento")

        if comp_type not in {en.value for en in ComplementTypeEnum}:
            self._value_error(key="TipoComplemento", value=comp_type)
            # self.catch_error(err_type=TipadoError, err_message=f"Error: TipoComplemento {comp_type} no válido.")

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
            self._nonfound_key_error(key="PermisoTransporte")
            # self.catch_error(err_type=ClaveError, err_message="Error: clave 'PermisoTransporte' no encontrada.")
        if trans_fee is None:
            self._nonfound_key_error(key="TarifaDeTransporte")
            # self.catch_error(ClaveError, "Error: clave 'TarifaDeTransporte' no encontrada.")

        if transp_permission and not re.match(TRANSPORT_PERM_REGEX, transp_permission):
            self._regex_error(
                key="PermisoTransporte", value=transp_permission, pattern=TRANSPORT_PERM_REGEX,
                )
            # self.catch_error(RegexError,
            # f"Error: valor 'PermisoTransporte' no cumple con el patron {TRANSPORT_PERM_REGEX}")
        if vehicle_key and not 6 <= len(vehicle_key) <= 12:
            self._longitud_error(
                key="ClaveVehiculo", value=vehicle_key, min_long=6, max_long=12,
                )
            # self.catch_error(LongitudError, "Error: 'ClaveVehiculo' no cumple con la longitud min 6 o max 12.")
        if trans_fee and not 0 <= trans_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeTransporte", value=trans_fee, min_val=0, max_val=1000000000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: valor 'TarifaDeTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_cap_fee and 0 <= trans_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadTransporte", value=trans_cap_fee, min_val=0, max_val=1000000000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error:
            # valor 'CargoPorCapacidadTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_use_fee and 0 <= trans_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=ValorMinMaxError, min_val=0, max_val=1000000000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: valor 'CargoPorUsoTrans' no se encuentra en el rango min 0 o max 1000000000000."
            #     )
        if trans_volum_charge and 0 <= trans_volum_charge <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoTransporte", value=trans_volum_charge, min_val=0, max_val=1000000000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error:
            # valor 'CargoVolumetricoTransporte' no se encuentra en el rango min 0 o max 1000000000000."
            #     )

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
            self._nonfound_key_error(key="RfcDictamen")
            # self.catch_error(ClaveError, "Error: clave 'RfcDictamen no encontrada.")
        if dictamen_lote is None:
            self._nonfound_key_error(key="LoteDictamen")
            # self.catch_error(ClaveError, "Error: clave 'LoteDictamen' no encontrada.")
        if dictamen_folio is None:
            self._nonfound_key_error(key="NumeroFolioDictamen")
            # self.catch_error(ClaveError, "Error: clave 'NumeroFolioDictamen' no encontrada.")
        if dictamen_date is None:
            self._nonfound_key_error(key="FechaEmisionDictamen")
            # self.catch_error(ClaveError, "Error: clave 'FechaEmisionDictamen' no encontrada.")
        if dictamen_result is None:
            self._nonfound_key_error(key="ResultadoDictamen")
            # self.catch_error(ClaveError, "Error: clave 'ResultadoDictamen' no encontrada.")

        if dictamen_rfc and not re.match(RFC_PERSONA_MORAL_REGEX, dictamen_rfc):
            self._regex_error(
                key="RfcDictamen", value=dictamen_rfc, pattern=RFC_PERSONA_MORAL_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'RfcDictamen'
            # con valor '{dictamen_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}'")
        if dictamen_lote and not 1 <= len(dictamen_lote) <= 50:
            self._longitud_error(
                key="LoteDictamen", value=dictamen_lote, min_long=1, max_long=50,
                )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message=f"Error:
            # clave 'LoteDictamen' con valor '{dictamen_lote}' no se encuentra en el rango min 1 o max 50."
            #     )
        if dictamen_folio and not re.match(FOLIO_DICTAMEN_REGEX, dictamen_folio):
            self._regex_error(
                key="NumeroFolioDictamen", value=dictamen_folio, pattern=FOLIO_DICTAMEN_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error:
            # clave 'NumeroFolioDictamen' con valor {dictamen_folio} no cumple con el regex {FOLIO_DICTAMEN_REGEX}"
            #     )
        if dictamen_date and not re.match(DATE_REGEX, dictamen_date):
            self._regex_error(
                key="FechaEmisionDictamen", value=dictamen_date, pattern=DATE_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error:
            # clave 'FechaEmisionDictamen' con valor {dictamen_date} no se expresa en formato yyyy-mm-dd"
            #     )
        if dictamen_result and not 10 <= len(dictamen_result) <= 300:
            self._longitud_error(
                key="ResultadoDictamen", value=dictamen_result, min_long=10, max_long=300,
                )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message=f"Error: clave 'ResultadoDictamen'
            # con valor {dictamen_result} no se encuentra en el rango min 10 o max 300.")

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
            self._nonfound_key_error(key="RfcCertificado")
            # self.catch_error(ClaveError, "Error: clave 'RfcCertificado' no encontrada.")
        if certified_folio is None:
            self._nonfound_key_error(key="NumeroFolioCertificado")
            # self.catch_error(ClaveError, "Error: clave 'NumeroFolioCertificado' no encontrada.")
        if certified_date is None:
            self._nonfound_key_error(key="FechaEmisionCertificado")
            # self.catch_error(ClaveError, "Error: clave 'FechaEmisionCertificado' no encontrada.")
        if certified_result is None:
            self._nonfound_key_error(key="ResultadoCertificado")
            # self.catch_error(ClaveError, "Error: clave 'ResultadoCertificado' no encontrada.")

        if certified_rfc and not re.match(RFC_PERSONA_MORAL_REGEX, certified_rfc):
            self._regex_error(
                key="RfcCertificado", value=certified_rfc, pattern=RFC_PERSONA_MORAL_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'RfcCertificado'
            # con valor {certified_rfc} no cumple con el regex {RFC_PERSONA_MORAL_REGEX}")
        if certified_folio and not re.match(FOLIO_CERTIFIED_REGEX, certified_folio):
            self._regex_error(
                key="NumeroFolioCertificado", value=certified_folio, pattern=FOLIO_CERTIFIED_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'NumeroFolioCertificado'
            # con valor {certified_folio} no cumple con el regex {FOLIO_CERTIFIED_REGEX}")
        if certified_date and not re.match(DATE_REGEX, certified_date):
            self._regex_error(
                key="FechaEmisionCertificado", value=certified_date, pattern=DATE_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'FechaEmisionCertificado'
            # con valor {certified_date} no se expresa en formato yyyy-mm-dd")
        if certified_result and not 10 <= len(certified_result) <= 300:
            self._longitud_error(
                key="ResultadoCertificado", value=certified_result, min_long=10, max_long=300,
                )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message=f"Error: clave 'ResultadoCertificado'
            # con valor {certified_result} no se encuentra en el rango min 10 o max 300."
            #     )

    @exception_wrapper
    def _validate_nacional(self) -> None:
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            supplier_permission = national_item.get("PermisoProveedor")

            national_parent = f"Nacional[{national.index(national_item)}]"

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                dict_type=complement_national):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
            if custom_client_rfc is None:
                self._nonfound_key_error(
                    key="RfcClienteOProveedor",
                    source=f"{national_parent}.RfcClienteOProveedor"
                    )
                # self.catch_error(
                #     err_type=ClaveError,
                #     err_message="Error: clave 'RfcClienteOProveedor' no encontrada.")
            if custom_client_name is None:
                self._nonfound_key_error(
                    key="NombreClienteOProveedor",
                    source=f"{national_parent}.NombreClienteOProveedor"
                    )
                # self.catch_error(
                #     err_type=ClaveError,
                #     err_message="Error: clave 'NombreClienteOProveedor' no encontrada.")
            if custom_client_rfc and not re.match(RFC_REGEX, custom_client_rfc):
                self._regex_error(
                    key="RfcClienteOProveedor", value=custom_client_rfc, pattern=RFC_REGEX,
                    source=f"{national_parent}.RfcClienteOProveedor"
                    )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'RfcClienteOProveedor'
                # con valor {custom_client_rfc} no cumple con el regex {RFC_REGEX}")
            if custom_client_name and not 10 <= len(custom_client_name) <= 150:
                self._longitud_error(
                    key="NombreClienteOProveedor", value=custom_client_name, min_long=10, max_long=150,
                    source=f"{national_parent}.NombreClienteOProveedor"
                    )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message=f"Error: clave 'NombreClienteOProveedor'
                # con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300.")
            if supplier_permission and not re.match(PERMISSION_PROOVE_REGEX, supplier_permission):
                self._regex_error(
                    key="PermisoProveedor", value=supplier_permission, pattern=PERMISSION_PROOVE_REGEX,
                    source=f"{national_parent}.PermisoProveedor"
                    )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'PermisoProveedor'
                # con valor {supplier_permission} no cumple con el regex {PERMISSION_PROOVE_REGEX}")

    @exception_wrapper
    def __validate_national_cfdi(self) -> None:
        if (national := self.current_complement.get("Nacional")) is None:
            return
        for national_item in national:
            national_parent = f"Nacional[{national.index(national_item)}]"

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

                    cfdi_parent = f"CFDIs[{cfdis.index(cfdi)}]"
                    if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi,
                                                                        dict_type=complement_cfdis):
                        type_err = err.get("type_err")
                        err_message = err.get("err_message")
                        self.catch_error(err_type=type_err, err_message=err_message)

                    if cfdi_val is None:
                        self._nonfound_key_error(
                            key="Cfdi",
                            )
                        # self.catch_error(
                        #     err_type=ClaveError,
                        #     err_message="Error: clave 'Cfdi' no se encuentra.")
                    if cfdi_type is None:
                        self._nonfound_key_error(
                            key="TipoCfdi",
                            )
                        # self.catch_error(
                        #     err_type=ClaveError,
                        #     err_message="Error: clave 'TipoCfdi' no se encuentra.")
                    if cfdi_type and cfdi_type not in [cfdi.value for cfdi in CfdiType]:
                        self._value_error(
                            key="TipoCfdi", value=cfdi_type,
                            source=f"{national_parent}.{cfdi_parent}.TipoCfdi"
                            )
                        # self.catch_error(
                        #     err_type=ClaveError,
                        #     err_message=f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válido.")
                    if transaction_date is None:
                        self._nonfound_key_error(
                            key="FechaYHoraTransaccion",
                            )
                        # self.catch_error(
                        #     err_type=ClaveError,
                        #     err_message="Error: clave 'FechaYHoraTransaccion' no se encuentra.")
                    if documented_volum is None:
                        self._nonfound_key_error(
                            key="VolumenDocumentado",
                            )
                        # self.catch_error(
                        #     err_type=ClaveError,
                        #     err_message="Error: clave 'VolumenDocumentado' no se encuentra.")
                    if documented_volum:
                        num_value = documented_volum.get("ValorNumerico")
                        measure_unit = documented_volum.get("UnidadDeMedida")
                        if num_value is None:
                            self._nonfound_key_error(
                                key="ValorNumerico",
                                source=f"{national_parent}.{cfdi_parent}.VolumenDocumentado"
                                )
                            # self.catch_error(
                            #     err_type=ClaveError,
                            #     err_message="Error: clave 'ValorNumerico'
                            # no se encuentra en clave 'VolumenDocumentado'.")
                        if measure_unit is None:
                            self._nonfound_key_error(
                                key="UnidadDeMedida",
                                source=f"{national_parent}.{cfdi_parent}.VolumenDocumentado"
                                )
                            # self.catch_error(
                            #     err_type=ClaveError,
                            #     err_message="Error: clave 'UnidadDeMedida'
                            # no se encuentra en clave 'VolumenDocumentado'.")
                        if num_value and not 0 <= num_value <= 100000000000:
                            self._min_max_value_error(
                                key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
                                source=f"{national_parent}.{cfdi_parent}.VolumenDocumentado.ValorNumerico"
                                )
                            # self.catch_error(
                            #     err_type=ValorMinMaxError,
                            #     err_message=f"Error: clave 'ValorNumerico'
                            # con valor {num_value} no tiene el valor min 0 o max 100000000000.")
                        if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
                            self._regex_error(
                                key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                                source=f"{national_parent}.{cfdi_parent}.VolumenDocumentado.UnidadDeMedida"
                                )
                            # self.catch_error(
                            #     err_type=RegexError,
                            #     err_message=f"Error: clave 'UnidadDeMedida'
                            # con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")

                    if cfdi_val and not re.match(CFDI_REGEX, cfdi_val):
                        self._regex_error(
                            key="Cfdi", value=cfdi_val, pattern=CFDI_REGEX,
                            source=f"{national_parent}.{cfdi_parent}.VolumenDocumentado.UnidadDeMedida"
                            )
                        # self.catch_error(
                        #     err_type=RegexError,
                        #     err_message=f"Error: clave 'Cfdi'
                        # con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}")
                    if purchase_price and not 0 <= purchase_price <= 1000000000000:
                        self._min_max_value_error(
                            key="PrecioCompra", value=purchase_price, min_val=0, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.PrecioCompra"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'PrecioCompra'
                        # con valor '{purchase_price}' no tiene el valor min 0 o max 1000000000000.")
                    if consideration and not 1 <= consideration <= 1000000000000:
                        self._min_max_value_error(
                            key="Contraprestacion", value=consideration, min_val=0, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.Contraprestacion"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'Contraprestacion'
                        # con valor '{consideration}' no tiene el valor min 0 o max 1000000000000.")
                    if alm_fee and not 1 <= alm_fee <= 1000000000000:
                        self._min_max_value_error(
                            key="CargoPorCapacidadAlmac", value=alm_fee, min_val=1, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.CargoPorCapacidadAlmac"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'Contraprestacion'
                        # con valor '{alm_fee}' no tiene el valor min 0 o max 1000000000000.")
                    if alm_cap_fee and not 1 <= alm_cap_fee <= 1000000000000:
                        self._min_max_value_error(
                            key="CargoPorCapacidadAlmac", value=alm_cap_fee, min_val=1, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.CargoPorCapacidadAlmac"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'CargoPorCapacidadALmac'
                        # con valor '{alm_cap_fee}' no tiene el valor min 0 o max 1000000000000.")
                    if alm_use_fee and not 1 <= alm_use_fee <= 1000000000000:
                        self._min_max_value_error(
                            key="CargoPorUsoAlmac", value=alm_use_fee, min_val=1, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.CargoPorUsoAlmac"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'CargoPorUsoAlmac'
                        # con valor '{alm_use_fee}' no tiene el valor min 0 o max 1000000000000.")
                    if alm_volum_fee and not 1 <= alm_volum_fee <= 1000000000000:
                        self._min_max_value_error(
                            key="CargoVolumetricoAlmac", value=alm_volum_fee, min_val=1, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.CargoVolumetricoAlmac"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'CargoVolumetricoAlmac'
                        # con valor '{alm_volum_fee}' no tiene el valor min 0 o max 1000000000000.")
                    if discount and not 1 <= discount <= 1000000000000:
                        self._min_max_value_error(
                            key="Descuento", value=discount, min_val=1, max_val=1000000000000,
                            source=f"{national_parent}.{cfdi_parent}.Descuento"
                            )
                        # self.catch_error(
                        #     err_type=ValorMinMaxError,
                        #     err_message=f"Error: Clave 'Descuento'
                        # con valor '{discount}' no tiene el valor min 0 o max 1000000000000.")
                    if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
                        self._regex_error(
                            key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
                            source=f"{national_parent}.{cfdi_parent}.FechaYHoraTransaccion"
                            )
                        # self.catch_error(
                        #     err_type=RegexError,
                        #     err_message=f"Error: clave 'FechaYHoraTransaccion'
                        # con valor {transaction_date} no se expresa en formato yyyy-mm-ddThh:mm:ss+-hh:mm")

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
            self._nonfound_key_error(key="PermisoImportacion")
            # self.catch_error(err_type=ClaveError, err_message="Error: clave 'PermisoImportacion' no se encuentra.")

        if import_permission and not re.match(IMPORT_PERMISSION_REGEX, import_permission):
            self._regex_error(
                key="PermisoImportacion", value=import_permission, pattern=IMPORT_PERMISSION_REGEX,
                )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PermisoImportacion'
            # con valor {import_permission} no cumple con el regex {IMPORT_PERMISSION_REGEX}")

        # for pedimento in pedimentos:
        #     self.__validate_pedimentos(pedimento=pedimento)

    @exception_wrapper
    def __validate_extranjero_pedimentos(self) -> None:
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return
        # print("=====================================asdasd")
        # print(type(foreign))
        # print(foreign)
        if (pedimentos := foreign[0].get("Pedimentos")) is None:
            return
        for fore in foreign:
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=fore,
                                                                    dict_type=complement_foreign):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
                return
            pedimento = fore.get("Pedimentos")
            # print("PEDIMENTO =>", pedimento)
        # for pedimento in pedimentos:
            intern_point = pedimento.get("PuntoDeInternacion")
            origin_country = pedimento.get("PaisOrigen")
            aduanal_transp = pedimento.get("MedioDeTransEntraAduana")
            aduanal_pedimento = pedimento.get("PedimentoAduanal")
            incoterm = pedimento.get("Incoterms")
            import_price = pedimento.get("PrecioDeImportacion")
            documented_volume = pedimento.get("VolumenDocumentado")

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=pedimento,
                                                                dict_type=compl_foreign_pedimentos):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
            if intern_point is None:
                self._nonfound_key_error(key="PuntoDeInternacion")
                # self.catch_error(err_type=ClaveError, err_message="Error: clave 'PuntoDeInternacion' no se encuentra")
            if origin_country is None:
                self._nonfound_key_error(key="PaisOrigen")
                # self.catch_error(err_type=ClaveError, err_message="Error: clave 'PaisOrigen' no se encuentra")
            if aduanal_pedimento is None:
                self._nonfound_key_error(key="PedimentoAduanal")
                # self.catch_error(err_type=ClaveError, err_message="Error: clave 'PedimentoAduanal' no se encuentra")
            if incoterm is None:
                self._nonfound_key_error(key="Incoterms")
                # self.catch_error(err_type=ClaveError, err_message="Error: clave 'Incoterms' no se encuentra")
            if import_price is None:
                self._nonfound_key_error(key="PrecioDeImportacion")
                #self.catch_error(err_type=ClaveError, err_message="Error: clave 'PrecioDeImportacion' no se encuentra")
            if documented_volume is None:
                self._nonfound_key_error(key="VolumenDocumentado")
                # self.catch_error(err_type=ClaveError, err_message="Error: clave 'VolumenDocumentado' no se encuentra")
            if documented_volume:
                num_value = documented_volume.get("ValorNumerico")
                measure_unit = documented_volume.get("UnidadDeMedida")
                if num_value is None:
                    self._nonfound_key_error(key="ValorNumerico")
                    # self.catch_error(
                    #     err_type=ClaveError,
                    #     err_message="Error: clave 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'.")
                if measure_unit is None:
                    self._nonfound_key_error(key="UnidadDeMedida")
                    # self.catch_error(
                    #     err_type=ClaveError,
                    #     err_message="Error: clave 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'.")
                if num_value and not 0 <= num_value <= 100000000000:
                    self._min_max_value_error(
                        key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
                        )
                    # self.catch_error(
                    #     err_type=ValorMinMaxError,
                    #     err_message=f"Error: clave 'ValorNumerico'
                    # con valor {num_value} no está en el valor min 0 o max 100000000000.")
                if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
                    self._regex_error(
                        key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                        )
                    # self.catch_error(
                    #     err_type=RegexError,
                    #     err_message=f"Error: clave 'UnidadDeMedida'
                    # con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")

            if intern_point and not re.match(INTERN_SPOT_REGEX, intern_point):
                self._regex_error(
                    key="PuntoDeInternacion", value=intern_point, pattern=INTERN_SPOT_REGEX,
                    )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'PuntoDeInternacion'
                # con valor {intern_point} no cumple con el patron {INTERN_SPOT_REGEX}")
            if intern_point and not 2 <= intern_point <= 3:
                self._min_max_value_error(
                    key="PuntoDeInternacion", value=intern_point, min_val=2, max_val=3,
                    )
                # self.catch_error(
                #     err_type=ValorMinMaxError,
                #     err_message=f"Error: clave 'PuntoDeInternacion'
                # con valor {intern_point} no tiene la longitud min 2 o max 3.")
            if origin_country and origin_country not in CountryCode:
                self._value_error(
                    key="PaisOrigen", value=origin_country,
                    )
                # self.catch_error(
                #     err_type=ValorError,
                #     err_message=f"Error: valor '{origin_country}' en clave 'PaisOrigen' no válido.")
            if aduanal_transp and aduanal_transp not in [item.value for item in AduanaEntrance]:
                self._value_error(
                    key="MedioDeTransporteAduana", value=aduanal_transp,
                    )
                # self.catch_error(
                #     err_type=ValorError,
                #     err_message=f"Error: valor '{aduanal_transp}' en clave 'MedioDeTransporteAduana' no válido.")
            if aduanal_pedimento and not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
                self._regex_error(
                    key="PedimentoAduanal", value=aduanal_pedimento, pattern=ADUANAL_PEDIMENTO,
                    )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'PedimentoAduanal'
                # con valor {aduanal_pedimento} no cumple con el patron {ADUANAL_PEDIMENTO}")
            if aduanal_pedimento and len(aduanal_pedimento) != 21:
                self._longitud_error(
                    key="PedimentoAduanal", value=aduanal_pedimento, min_long=21, max_long=21,
                    )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message=f"Error: clave 'PedimentoAduanal'
                # con valor '{aduanal_pedimento} no cumple con la longitud de 21.'")
            if incoterm and incoterm not in IncotermCode.__members__:
                self._value_error(
                    key="Incoterms", value=incoterm
                    )
                # self.catch_error(
                #     err_type=ValorError,
                #     err_message=f"Error: clave 'Incoterms' con valor {incoterm} no válido.")
            if import_price and not 0 <= import_price <= 100000000000:
                self._min_max_value_error(
                    key="PrecioDeImportacion", value=import_price, min_val=0, max_val=100000000000,
                    )
                # self.catch_error(
                #     err_type=ValorMinMaxError,
                #     err_message=f"Error: clave 'PrecioDeImportacion'
                # con valor {import_price} no tiene el valor min 0 o max 100000000000.")

    @exception_wrapper
    def _validate_aclaracion(self) -> None:
        if (clarif := self.current_complement.get("Aclaracion")) is None:
            return
        if clarif and not 10 <= len(clarif) <= 600:
            self._longitud_error(
                key="Aclaracion", value=clarif, min_long=10, max_long=600,
                )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message="Error: valor 'Aclaracion' no cumple con la longitud min 10 o max 600.")

    def _current_complement(self) -> dict:
        return self.current_complement[self._comp_index]

    def _next_complement(self) -> bool:
        return self._comp_index < self.comp_len

    def _update_index(self) -> None:
        self._comp_index += 1
        if self._next_complement():
            self.current_complement = self.complement[self._comp_index]

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
            "source": f"Complemento[{self.complement.index(self.current_complement)}].{source}"
            }

    def _nonfound_key_error(
            self,
            key: str,
            source: Optional[str] = None,
        ) -> None:
        """Store ClaveError in self.errors.\n
        :param key: Dict key element.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ClaveError,
            err_message=f"Error: Elemento '{key}' no declarado.",
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
        return self._errors

    def get_error_list(self) -> list:
        """Return recopiled error through Complemento validations.\n
        :return: List[Dict[str | Any]]."""
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
