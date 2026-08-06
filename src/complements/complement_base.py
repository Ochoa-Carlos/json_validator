"""Base class for complement inheritance, implementing the Almacenamiento Complement rules."""
import re
from typing import Any, Optional, Type, Union

from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_STRICT_REGEX,
                                       CLIENT_NAME_REGEX, DATE_REGEX,
                                       FOLIO_REGEX,
                                       IMPORT_EXPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX, MEASURE_UNIT,
                                       PERMISSION_PROOVE_REGEX, RFC_REGEX,
                                       TRANSPORT_PERM_REGEX, UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType,
                                         ComplementTypeEnum, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import (ClaveError, LongitudError, RegexError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (compl_foreign_pedimentos, compl_volumen, complement,
                            complement_certified, complement_cfdis,
                            complement_dictamen, complement_foreign,
                            complement_national, complement_transport,
                            complement_trasvase)


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
        """Validate every Almacenamiento complement declared in the report."""
        while self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_transporte()
            self._validate_trasvase()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_extranjero()
            self._validate_aclaracion()

            self._update_index()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        """Validate value types declared at the complement root.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement,
                                                              dict_type=complement):
            self._type_error(err=err)

    @exception_wrapper
    def _validate_tipo_complemento(self) -> None:
        """Validate the TipoComplemento enum value.\n
        :return: None."""
        comp_type = self.current_complement.get("TipoComplemento")

        if comp_type not in {en.value for en in ComplementTypeEnum}:
            self._value_error(key="TipoComplemento", value=comp_type, source="TipoComplemento")

    @exception_wrapper
    def _validate_transporte(self) -> None:
        """Validate Transporte object.\n
        :return: None."""
        if (transportation := self.current_complement.get("Transporte")) is None:
            return
        if not isinstance(transportation, dict):
            return

        transp_parent = "Transporte"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transportation,
                                                              dict_type=complement_transport):
            self._type_error(err=err, source=transp_parent)

        transp_permission = transportation.get("PermisoTransporte")
        vehicle_key = transportation.get("ClaveDeVehiculo")
        trans_fee = transportation.get("TarifaDeTransporte")
        trans_cap_fee = transportation.get("CargoPorCapacidadTrans")
        trans_use_fee = transportation.get("CargoPorUsoTrans")
        trans_volum_charge = transportation.get("CargoVolumetricoTrans")

        if transp_permission is None:
            self._nonfound_key_error(key="PermisoTransporte", source=transp_parent)
        if trans_fee is None:
            self._nonfound_key_error(key="TarifaDeTransporte", source=transp_parent)

        if self._invalid_pattern(value=transp_permission, pattern=TRANSPORT_PERM_REGEX):
            self._regex_error(
                key="PermisoTransporte", value=transp_permission, pattern=TRANSPORT_PERM_REGEX,
                source=f"{transp_parent}.PermisoTransporte"
                )
        if self._invalid_length(value=vehicle_key, min_long=5, max_long=12):
            self._longitud_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_long=5, max_long=12,
                source=f"{transp_parent}.ClaveDeVehiculo"
                )
        if self._invalid_range(value=trans_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="TarifaDeTransporte", value=trans_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.TarifaDeTransporte"
                )
        if self._invalid_range(value=trans_cap_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorCapacidadTrans", value=trans_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorCapacidadTrans"
                )
        if self._invalid_range(value=trans_use_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=trans_use_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorUsoTrans"
                )
        if self._invalid_range(value=trans_volum_charge, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=trans_volum_charge, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoVolumetricoTrans"
                )

    @exception_wrapper
    def _validate_trasvase(self) -> None:
        """Validate Trasvase objs list.\n
        :return: None."""
        if (trasvase := self.current_complement.get("Trasvase")) is None:
            return
        if not isinstance(trasvase, list):
            return

        if not trasvase:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: clave 'Trasvase' debe declarar al menos un elemento.",
                source="Trasvase"
                )
            return

        for trasvase_index, trasvase_item in enumerate(trasvase):
            trasvase_parent = f"Trasvase[{trasvase_index}]"

            if not isinstance(trasvase_item, dict):
                self._value_error(key="Trasvase", value=trasvase_item, source=trasvase_parent)
                continue

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=trasvase_item,
                                                                  dict_type=complement_trasvase):
                self._type_error(err=err, source=trasvase_parent)

            trasvase_name = trasvase_item.get("NombreTrasvase")
            trasvase_rfc = trasvase_item.get("RfcTrasvase")
            trasvase_permission = trasvase_item.get("PermisoTrasvase")
            trasvase_description = trasvase_item.get("DescripcionTrasvase")
            trasvase_cfdi = trasvase_item.get("CfdiTrasvase")

            if trasvase_name is None:
                self._nonfound_key_error(key="NombreTrasvase", source=trasvase_parent)
            if trasvase_rfc is None:
                self._nonfound_key_error(key="RfcTrasvase", source=trasvase_parent)

            if self._invalid_length(value=trasvase_name, min_long=5, max_long=150):
                self._longitud_error(
                    key="NombreTrasvase", value=trasvase_name, min_long=5, max_long=150,
                    source=f"{trasvase_parent}.NombreTrasvase"
                    )
            if self._invalid_pattern(value=trasvase_rfc, pattern=RFC_REGEX):
                self._regex_error(
                    key="RfcTrasvase", value=trasvase_rfc, pattern=RFC_REGEX,
                    source=f"{trasvase_parent}.RfcTrasvase"
                    )
            if self._invalid_length(value=trasvase_permission, min_long=5, max_long=30):
                self._longitud_error(
                    key="PermisoTrasvase", value=trasvase_permission, min_long=5, max_long=30,
                    source=f"{trasvase_parent}.PermisoTrasvase"
                    )
            if self._invalid_length(value=trasvase_description, min_long=20, max_long=250):
                self._longitud_error(
                    key="DescripcionTrasvase", value=trasvase_description, min_long=20, max_long=250,
                    source=f"{trasvase_parent}.DescripcionTrasvase"
                    )
            if self._invalid_pattern(value=trasvase_cfdi, pattern=CFDI_STRICT_REGEX):
                self._regex_error(
                    key="CfdiTrasvase", value=trasvase_cfdi, pattern=CFDI_STRICT_REGEX,
                    source=f"{trasvase_parent}.CfdiTrasvase"
                    )

    @exception_wrapper
    def _validate_dictamen(self) -> None:
        """Validate Dictamen object.\n
        :return: None."""
        if (dictamen := self.current_complement.get("Dictamen")) is None:
            return
        if not isinstance(dictamen, dict):
            return

        dictamen_parent = "Dictamen"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=dictamen,
                                                              dict_type=complement_dictamen):
            self._type_error(err=err, source=dictamen_parent)

        dictamen_rfc = dictamen.get("RfcDictamen")
        dictamen_lote = dictamen.get("LoteDictamen")
        dictamen_folio = dictamen.get("NumeroFolioDictamen")
        dictamen_date = dictamen.get("FechaEmisionDictamen")
        dictamen_result = dictamen.get("ResultadoDictamen")

        if dictamen_rfc is None:
            self._nonfound_key_error(key="RfcDictamen", source=dictamen_parent)
        if dictamen_lote is None:
            self._nonfound_key_error(key="LoteDictamen", source=dictamen_parent)
        if dictamen_folio is None:
            self._nonfound_key_error(key="NumeroFolioDictamen", source=dictamen_parent)
        if dictamen_date is None:
            self._nonfound_key_error(key="FechaEmisionDictamen", source=dictamen_parent)
        if dictamen_result is None:
            self._nonfound_key_error(key="ResultadoDictamen", source=dictamen_parent)

        if self._invalid_pattern(value=dictamen_rfc, pattern=RFC_REGEX):
            self._regex_error(
                key="RfcDictamen", value=dictamen_rfc, pattern=RFC_REGEX,
                source=f"{dictamen_parent}.RfcDictamen"
                )
        if self._invalid_length(value=dictamen_lote, min_long=1, max_long=50):
            self._longitud_error(
                key="LoteDictamen", value=dictamen_lote, min_long=1, max_long=50,
                source=f"{dictamen_parent}.LoteDictamen"
                )
        if self._invalid_pattern(value=dictamen_folio, pattern=FOLIO_REGEX):
            self._regex_error(
                key="NumeroFolioDictamen", value=dictamen_folio, pattern=FOLIO_REGEX,
                source=f"{dictamen_parent}.NumeroFolioDictamen"
                )
        if self._invalid_pattern(value=dictamen_date, pattern=DATE_REGEX):
            self._regex_error(
                key="FechaEmisionDictamen", value=dictamen_date, pattern=DATE_REGEX,
                source=f"{dictamen_parent}.FechaEmisionDictamen"
                )
        if self._invalid_length(value=dictamen_result, min_long=10, max_long=300):
            self._longitud_error(
                key="ResultadoDictamen", value=dictamen_result, min_long=10, max_long=300,
                source=f"{dictamen_parent}.ResultadoDictamen"
                )

    @exception_wrapper
    def _validate_certificado(self) -> None:
        """Validate Certificado object.\n
        :return: None."""
        if (certified := self.current_complement.get("Certificado")) is None:
            return
        if not isinstance(certified, dict):
            return

        cert_parent = "Certificado"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=certified,
                                                              dict_type=complement_certified):
            self._type_error(err=err, source=cert_parent)

        certified_rfc = certified.get("RfcCertificado")
        certified_folio = certified.get("NumeroFolioCertificado")
        certified_date = certified.get("FechaEmisionCertificado")
        certified_result = certified.get("ResultadoCertificado")

        if certified_rfc is None:
            self._nonfound_key_error(key="RfcCertificado", source=cert_parent)
        if certified_folio is None:
            self._nonfound_key_error(key="NumeroFolioCertificado", source=cert_parent)
        if certified_date is None:
            self._nonfound_key_error(key="FechaEmisionCertificado", source=cert_parent)
        if certified_result is None:
            self._nonfound_key_error(key="ResultadoCertificado", source=cert_parent)

        if self._invalid_pattern(value=certified_rfc, pattern=RFC_REGEX):
            self._regex_error(
                key="RfcCertificado", value=certified_rfc, pattern=RFC_REGEX,
                source=f"{cert_parent}.RfcCertificado"
                )
        if self._invalid_pattern(value=certified_folio, pattern=FOLIO_REGEX):
            self._regex_error(
                key="NumeroFolioCertificado", value=certified_folio, pattern=FOLIO_REGEX,
                source=f"{cert_parent}.NumeroFolioCertificado"
                )
        if self._invalid_pattern(value=certified_date, pattern=DATE_REGEX):
            self._regex_error(
                key="FechaEmisionCertificado", value=certified_date, pattern=DATE_REGEX,
                source=f"{cert_parent}.FechaEmisionCertificado"
                )
        if self._invalid_length(value=certified_result, min_long=10, max_long=300):
            self._longitud_error(
                key="ResultadoCertificado", value=certified_result, min_long=10, max_long=300,
                source=f"{cert_parent}.ResultadoCertificado"
                )

    @exception_wrapper
    def _validate_nacional(self) -> None:
        """Validate Nacional objs list.\n
        :return: None."""
        if (national := self.current_complement.get("Nacional")) is None:
            return
        if not isinstance(national, list):
            return

        if not national:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: clave 'Nacional' debe declarar al menos un elemento.",
                source="Nacional"
                )
            return

        for national_index, national_item in enumerate(national):
            national_parent = f"Nacional[{national_index}]"

            if not isinstance(national_item, dict):
                self._value_error(key="Nacional", value=national_item, source=national_parent)
                continue

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                  dict_type=complement_national):
                self._type_error(err=err, source=national_parent)

            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            supplier_permission = national_item.get("PermisoProveedor")
            cfdis = national_item.get("CFDIs")

            if custom_client_rfc is None:
                self._nonfound_key_error(key="RfcClienteOProveedor", source=national_parent)
            if custom_client_name is None:
                self._nonfound_key_error(key="NombreClienteOProveedor", source=national_parent)

            if self._invalid_pattern(value=custom_client_rfc, pattern=RFC_REGEX):
                self._regex_error(
                    key="RfcClienteOProveedor", value=custom_client_rfc, pattern=RFC_REGEX,
                    source=f"{national_parent}.RfcClienteOProveedor"
                    )
            if self._invalid_length(value=custom_client_name, min_long=1, max_long=150):
                self._longitud_error(
                    key="NombreClienteOProveedor", value=custom_client_name, min_long=1, max_long=150,
                    source=f"{national_parent}.NombreClienteOProveedor"
                    )
            if self._invalid_pattern(value=custom_client_name, pattern=CLIENT_NAME_REGEX):
                self._regex_error(
                    key="NombreClienteOProveedor", value=custom_client_name, pattern=CLIENT_NAME_REGEX,
                    source=f"{national_parent}.NombreClienteOProveedor"
                    )
            if self._invalid_pattern(value=supplier_permission, pattern=PERMISSION_PROOVE_REGEX):
                self._regex_error(
                    key="PermisoProveedor", value=supplier_permission, pattern=PERMISSION_PROOVE_REGEX,
                    source=f"{national_parent}.PermisoProveedor"
                    )

            if cfdis and isinstance(cfdis, list):
                for cfdi_index, cfdi in enumerate(cfdis):
                    self.__validate_cfdi(cfdi=cfdi, cfdi_parent=f"{national_parent}.CFDIs[{cfdi_index}]")

    @exception_wrapper
    def __validate_cfdi(self, cfdi: dict, cfdi_parent: str) -> None:
        """Validate a Nacional CFDIs object.\n
        :param cfdi: CFDIs object declared in the Nacional element.\n
        :param cfdi_parent: Object reference where the CFDIs object is placed.\n
        :return: None."""
        if not isinstance(cfdi, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi, dict_type=complement_cfdis):
            self._type_error(err=err, source=cfdi_parent)

        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        purchase_price = cfdi.get("PrecioCompra")
        consideration = cfdi.get("Contraprestacion")
        alm_fee = cfdi.get("TarifaDeAlmacenamiento")
        alm_cap_fee = cfdi.get("CargoPorCapacidadAlmac")
        alm_use_fee = cfdi.get("CargoPorUsoAlmac")
        alm_volum_fee = cfdi.get("CargoVolumetricoAlmac")
        discount = cfdi.get("Descuento")
        transaction_date = cfdi.get("FechaYHoraTransaccion")
        documented_volum = cfdi.get("VolumenDocumentado")

        if cfdi_val is None:
            self._nonfound_key_error(key="Cfdi", source=cfdi_parent)
        if cfdi_type is None:
            self._nonfound_key_error(key="TipoCfdi", source=cfdi_parent)
        if transaction_date is None:
            self._nonfound_key_error(key="FechaYHoraTransaccion", source=cfdi_parent)
        if documented_volum is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=cfdi_parent)

        if self._invalid_pattern(value=cfdi_val, pattern=CFDI_STRICT_REGEX):
            self._regex_error(
                key="Cfdi", value=cfdi_val, pattern=CFDI_STRICT_REGEX,
                source=f"{cfdi_parent}.Cfdi"
                )
        if cfdi_type and cfdi_type not in [item.value for item in CfdiType]:
            self._value_error(
                key="TipoCfdi", value=cfdi_type,
                source=f"{cfdi_parent}.TipoCfdi"
                )
        if self._invalid_range(value=purchase_price, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="PrecioCompra", value=purchase_price, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.PrecioCompra"
                )
        if self._invalid_range(value=consideration, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="Contraprestacion", value=consideration, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.Contraprestacion"
                )
        if self._invalid_range(value=alm_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="TarifaDeAlmacenamiento", value=alm_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.TarifaDeAlmacenamiento"
                )
        if self._invalid_range(value=alm_cap_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorCapacidadAlmac", value=alm_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoPorCapacidadAlmac"
                )
        if self._invalid_range(value=alm_use_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorUsoAlmac", value=alm_use_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoPorUsoAlmac"
                )
        if self._invalid_range(value=alm_volum_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoVolumetricoAlmac", value=alm_volum_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoVolumetricoAlmac"
                )
        if self._invalid_range(value=discount, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="Descuento", value=discount, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.Descuento"
                )
        if self._invalid_pattern(value=transaction_date, pattern=UTC_FORMAT_REGEX):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
                source=f"{cfdi_parent}.FechaYHoraTransaccion"
                )

        self._validate_volumen_documentado(
            documented_volume=documented_volum, volume_parent=f"{cfdi_parent}.VolumenDocumentado",
            )

    @exception_wrapper
    def _validate_extranjero(self) -> None:
        """Validate Extranjero objs list.\n
        :return: None."""
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return
        if not isinstance(foreign, list):
            return

        if not foreign:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: clave 'Extranjero' debe declarar al menos un elemento.",
                source="Extranjero"
                )
            return

        for foreign_index, foreign_item in enumerate(foreign):
            foreign_parent = f"Extranjero[{foreign_index}]"

            if not isinstance(foreign_item, dict):
                self._value_error(key="Extranjero", value=foreign_item, source=foreign_parent)
                continue

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=foreign_item,
                                                                  dict_type=complement_foreign):
                self._type_error(err=err, source=foreign_parent)

            import_permission = foreign_item.get("PermisoImportacion")
            pedimentos = foreign_item.get("Pedimentos")

            if self._invalid_pattern(value=import_permission, pattern=IMPORT_EXPORT_PERMISSION_REGEX):
                self._regex_error(
                    key="PermisoImportacion", value=import_permission, pattern=IMPORT_EXPORT_PERMISSION_REGEX,
                    source=f"{foreign_parent}.PermisoImportacion"
                    )

            if pedimentos and isinstance(pedimentos, list):
                for pedimento_index, pedimento in enumerate(pedimentos):
                    self.__validate_pedimento(
                        pedimento=pedimento,
                        pedi_parent=f"{foreign_parent}.Pedimentos[{pedimento_index}]",
                        )

    @exception_wrapper
    def __validate_pedimento(self, pedimento: dict, pedi_parent: str) -> None:
        """Validate an Extranjero Pedimentos object.\n
        :param pedimento: Pedimentos object declared in the Extranjero element.\n
        :param pedi_parent: Object reference where the Pedimentos object is placed.\n
        :return: None."""
        if not isinstance(pedimento, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=pedimento,
                                                              dict_type=compl_foreign_pedimentos):
            self._type_error(err=err, source=pedi_parent)

        intern_point = pedimento.get("PuntoDeInternacion")
        origin_country = pedimento.get("PaisOrigen")
        aduanal_transp = pedimento.get("MedioDeTransEntraAduana")
        aduanal_pedimento = pedimento.get("PedimentoAduanal")
        incoterm = pedimento.get("Incoterms")
        import_price = pedimento.get("PrecioDeImportacion")
        documented_volume = pedimento.get("VolumenDocumentado")

        if intern_point is None:
            self._nonfound_key_error(key="PuntoDeInternacion", source=pedi_parent)
        if origin_country is None:
            self._nonfound_key_error(key="PaisOrigen", source=pedi_parent)
        if aduanal_transp is None:
            self._nonfound_key_error(key="MedioDeTransEntraAduana", source=pedi_parent)
        if aduanal_pedimento is None:
            self._nonfound_key_error(key="PedimentoAduanal", source=pedi_parent)
        if incoterm is None:
            self._nonfound_key_error(key="Incoterms", source=pedi_parent)
        if import_price is None:
            self._nonfound_key_error(key="PrecioDeImportacion", source=pedi_parent)
        if documented_volume is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=pedi_parent)

        if self._invalid_pattern(value=intern_point, pattern=INTERN_SPOT_REGEX):
            self._regex_error(
                key="PuntoDeInternacion", value=intern_point, pattern=INTERN_SPOT_REGEX,
                source=f"{pedi_parent}.PuntoDeInternacion"
                )
        if origin_country and origin_country not in [item.value for item in CountryCode]:
            self._value_error(
                key="PaisOrigen", value=origin_country,
                source=f"{pedi_parent}.PaisOrigen"
                )
        if aduanal_transp and aduanal_transp not in [item.value for item in AduanaEntrance]:
            self._value_error(
                key="MedioDeTransEntraAduana", value=aduanal_transp,
                source=f"{pedi_parent}.MedioDeTransEntraAduana"
                )
        if self._invalid_pattern(value=aduanal_pedimento, pattern=ADUANAL_PEDIMENTO):
            self._regex_error(
                key="PedimentoAduanal", value=aduanal_pedimento, pattern=ADUANAL_PEDIMENTO,
                source=f"{pedi_parent}.PedimentoAduanal"
                )
        if incoterm and incoterm not in [item.value for item in IncotermCode]:
            self._value_error(
                key="Incoterms", value=incoterm,
                source=f"{pedi_parent}.Incoterms"
                )
        if self._invalid_range(value=import_price, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="PrecioDeImportacion", value=import_price, min_val=0, max_val=1000000000000,
                source=f"{pedi_parent}.PrecioDeImportacion"
                )

        self._validate_volumen_documentado(
            documented_volume=documented_volume, volume_parent=f"{pedi_parent}.VolumenDocumentado",
            )

    @exception_wrapper
    def _validate_volumen_documentado(self, documented_volume: Optional[dict], volume_parent: str) -> None:
        """Validate a VolumenDocumentado object against the Volumen definition.\n
        :param documented_volume: VolumenDocumentado object declared in the parent element.\n
        :param volume_parent: Object reference where the VolumenDocumentado object is placed.\n
        :return: None."""
        if documented_volume is None or not isinstance(documented_volume, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=documented_volume,
                                                              dict_type=compl_volumen):
            self._type_error(err=err, source=volume_parent)

        num_value = documented_volume.get("ValorNumerico")
        measure_unit = documented_volume.get("UnidadDeMedida")

        if num_value is None:
            self._nonfound_key_error(key="ValorNumerico", source=volume_parent)
        if measure_unit is None:
            self._nonfound_key_error(key="UnidadDeMedida", source=volume_parent)

        if self._invalid_range(value=num_value, min_val=0, max_val=100000000000):
            self._min_max_value_error(
                key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
                source=f"{volume_parent}.ValorNumerico"
                )
        if self._invalid_pattern(value=measure_unit, pattern=MEASURE_UNIT):
            self._regex_error(
                key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                source=f"{volume_parent}.UnidadDeMedida"
                )

    @exception_wrapper
    def _validate_aclaracion(self) -> None:
        """Validate Aclaracion element.\n
        :return: None."""
        if (clarif := self.current_complement.get("Aclaracion")) is None:
            return
        if self._invalid_length(value=clarif, min_long=10, max_long=600):
            self._longitud_error(
                key="Aclaracion", value=clarif, min_long=10, max_long=600,
                source="Aclaracion"
                )

    def _invalid_pattern(self, value: Any, pattern: str) -> bool:
        """Return True when value is a non-empty string that does not satisfy the pattern.\n
        :param value: Value to test; non-string values are skipped since typing already reports them.\n
        :param pattern: Regex the value must satisfy.\n
        """
        return isinstance(value, str) and bool(value) and re.match(pattern, value) is None

    def _invalid_length(self, value: Any, min_long: int, max_long: int) -> bool:
        """Return True when value has a length outside the accepted range.\n
        :param value: Value to test; values without a length are skipped since typing already reports them.\n
        :param min_long: Minimum accepted length.\n
        :param max_long: Maximum accepted length.\n
        """
        if not isinstance(value, (str, list, dict)) or not value:
            return False
        return not min_long <= len(value) <= max_long

    def _invalid_range(self, value: Any, min_val: float, max_val: float) -> bool:
        """Return True when value is a number outside the accepted range.\n
        :param value: Value to test; non-numeric values are skipped since typing already reports them.\n
        :param min_val: Minimum accepted value.\n
        :param max_val: Maximum accepted value.\n
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not value:
            return False
        return not min_val <= value <= max_val

    def _next_complement(self) -> bool:
        """Return True while there are complements left to validate."""
        return self._comp_index < self.comp_len

    def _update_index(self) -> None:
        """Advance to the next complement in the list.\n
        :return: None."""
        self._comp_index += 1
        if self._next_complement():
            self.current_complement = self.complement[self._comp_index]

    def catch_error(self, err_type: Type[BaseException], err_message: str, source: Optional[str] = None) -> None:
        """Store given error in class error list.
        :param err_type: Class from BaseException inherit.\n
        :param err_message: Message of the given error.\n
        :param source: Source reference of the error\n
        :return: None."""
        self.errors = {
            "type_error": err_type.__name__,
            "error": err_message,
            "source": f"Complemento[{self._comp_index}].{source}"
            }

    def _type_error(
            self,
            err: dict,
            source: Optional[str] = None,
        ) -> None:
        """Store the type mismatch reported by DictionaryTypeValidator in self.errors.\n
        :param err: Type mismatch returned by DictionaryTypeValidator.validate_dict_type.\n
        :param source: Object reference where key and value are placed.\n
        :return: None."""
        self.catch_error(
            err_type=err["type_err"],
            err_message=err["err_message"],
            source=source
        )

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
            value: Any,
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
            value: Any,
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
            value: Any,
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
            value: Any,
            pattern: str,
            source: Optional[str] = None,
        ) -> None:
        """Store RegexError in self.errors.\n
        :param key: Dict Key element.\n
        :param value: value that unmatch regex.\n
        :param pattern: Reggex pattern.\n
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

        self._errors_list.append(errors)
        self._errors[errors["type_error"]] = errors["error"]
