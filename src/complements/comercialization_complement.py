"""This module validate Comercializacion Complement Element."""
import re

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_REGEX,
                                       IMPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX, MEASURE_UNIT,
                                       PERMISSION_ALM_DIST_REGEX,
                                       PERMISSION_PROOVE_CLIENT_REGEX,
                                       RFC_REGEX, TRANSPORT_PERM_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import (ClaveError, LongitudError, RegexError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (com_comp_cfdis, compl_foreign_pedimentos,
                            complement, complement_certified, complement_cfdis,
                            complement_dictamen, complement_foreign,
                            complement_national, complement_transport,
                            terminal_alm)


class ComercializationComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemento(self) -> None:
        """Validate comercialization complement items."""
        while self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_dist()
            self._validate_dictamen()
            self._validate_nacional()
            self._validate_extranjero()
            self._validate_aclaracion()

            self._update_index()
            self.validate_complemento()

    @exception_wrapper
    def _validate_terminal_alm_dist(self) -> None:
        if (alm_terminal := self.current_complement.get("TerminalAlmYDist")) is None:
            return

        alm = alm_terminal.get("Almacenamiento")
        transp = alm_terminal.get("Transporte")

        self.__validate_almacenamiento(alm=alm)
        self.__validate_transporte(transp=transp)

    @exception_wrapper
    def __validate_almacenamiento(self, alm: dict) -> None:
        """Validate Almacenamiento objs.\n
        :return: None."""
        if alm is None:
            return
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm,
                                                                    dict_type=terminal_alm):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
            return

        alm_dist_terminal = alm.get("TerminalAlmYDist")
        alm_dist_alm = alm.get("PermisoAlmYDist")
        alm_fee = alm.get("TarifaDeAlmacenamiento")
        alm_cap_fee = alm.get("CargoPorCapacidadAlmac")
        alm_use_fee = alm.get("CargoPorUsoAlmac")
        volume_alm_fee = alm.get("CargoVolumetricoAlmac")

        if alm_dist_terminal is None:
            self._nonfound_key_error(key="TerminalAlmYDist")
            # self.catch_error(
            #     err_type=ClaveError,
            #     err_message="Error: clave 'TerminalAlmYDist' no encontrada")
        if alm_dist_alm is None:
            self._nonfound_key_error(key="PermisoAlmYDist")
            # self.catch_error(
            #     err_type=ClaveError,
            #     err_message="Error: clave 'PermisoAlmYDist' no encontrada")

        if alm_dist_terminal and not 5 <= len(alm_dist_terminal) <= 250:
            self._longitud_error(
                key="TerminalAlmYDist", value=alm_dist_terminal, min_long=5, max_long=250,
            )
        if alm_dist_alm and not re.match(PERMISSION_ALM_DIST_REGEX, alm_dist_alm):
            self._regex_error(
                key="PermisoAlmYDist", value=alm_dist_alm, pattern=PERMISSION_ALM_DIST_REGEX,
            )
        if alm_fee and not 0 <= alm_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeAlmacenamiento", value=alm_fee, min_val=0, max_val=1000000000000,
            )
        if alm_cap_fee and not 0 <= alm_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadAlmac", value=alm_cap_fee, min_val=0, max_val=1000000000000,
            )
        if alm_use_fee and not 0 <= alm_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoAlamc", value=alm_use_fee, min_val=0, max_val=1000000000000,
            )
        if volume_alm_fee and not 0 <= volume_alm_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoAlmac", value=volume_alm_fee, min_val=0, max_val=1000000000000,
            )

    @exception_wrapper
    def __validate_transporte(self, transp: dict) -> None:
        """Validate Transporte objs.\n
        :return: None."""
        if transp is None:
            return
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transp,
                                                                    dict_type=terminal_alm):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
            return

        transp_parent = "TerminalAlmYDist.Transporte"
        perm_transp = transp.get("PermisoTransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")
        transp_fee = transp.get("TarifaDeTransporte")
        transp_cap_fee = transp.get("CargoPorCapacidadTrans")
        transp_use_fee = transp.get("CargoPorUsoTrans")
        transp_volume_fee = transp.get("CargoVolumetricoTrans")

        if perm_transp is None:
            self._nonfound_key_error(key="PermisoTransporte", source=transp_parent)
        if transp_fee is None:
            self._nonfound_key_error(key="TarifaDeTransporte", source=transp_parent)

        if perm_transp and not re.match(TRANSPORT_PERM_REGEX, perm_transp):
            self._regex_error(
                key="PermisoTransporte", value=perm_transp, pattern=TRANSPORT_PERM_REGEX,
                source=f"{transp_parent}.PermisoTransporte"
            )
        if vehicle_key and 6 <= len(vehicle_key) <= 12:
            self._min_max_value_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_val=6, max_val=12,
                source=f"{transp_parent}.ClaveDeVehiculo"
            )
        if transp_fee and not 0 <= transp_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeTransporte", value=transp_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.TarifaDeTransporte"
            )
        if transp_cap_fee and not 0 <= transp_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadTrans", value=transp_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorCapacidadTrans"
            )
        if transp_use_fee and not 0 <= transp_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=transp_use_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorUsoTrans"
            )
        if transp_volume_fee and not 0 <= transp_volume_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=transp_volume_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoVolumetricoTrans"
            )

    @exception_wrapper
    def _validate_nacional(self):
        """Validate Nacional objs list.\n
        :return: None."""
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                    dict_type=complement_national):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
                return

            national_parent = f"Nacional[{national.index(national_item)}]"
            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            custom_client_permission = national_item.get("PermisoClienteOProveedor")
            cfdis = national_item.get("CFDIs")

            if custom_client_rfc is None:
                self._nonfound_key_error(key="RfcClienteOProveedor", source=national_parent)
            if custom_client_rfc and not re.match(RFC_REGEX, custom_client_rfc):
                self._regex_error(
                    key="RfcClienteOProveedor", value=custom_client_rfc, pattern=RFC_REGEX,
                    source=f"{national_parent}.RfcClienteOProveedor"
                )
            if custom_client_name and not 10 <= len(custom_client_name) <= 150:
                self._longitud_error(
                    key="NombreClienteOProveedor", value=custom_client_name, min_long=10, max_long=150,
                    source=f"{national_parent}.NombreClienteOProveedor"
                )
            if custom_client_permission and not re.match(PERMISSION_PROOVE_CLIENT_REGEX, custom_client_permission):
                self._regex_error(
                    key="PermisoClienteOProveedor", value=custom_client_permission,
                    pattern=PERMISSION_PROOVE_CLIENT_REGEX, source=f"{national_parent}.PermisoClienteOProveedor"
                )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi, cfdi_parent=f"{national_parent}.CFDIs[{cfdis.index(cfdi)}]")

    @exception_wrapper
    def __validate_cfdi(self, cfdi, cfdi_parent: str):
        """Validate Cfdis objs list.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi,
                                                                    dict_type=com_comp_cfdis):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
            return

        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        consid_purch_sale_price = cfdi.get("PrecioVentaOCompraOContrap")
        transaction_date = cfdi.get("FechaYHoraTransaccion")
        documented_volum = cfdi.get("VolumenDocumentado")
        num_value = documented_volum.get("ValorNumerico")
        measure_unit = documented_volum.get("UnidadDeMedida")

        if cfdi_val is None:
            self._nonfound_key_error(key="Cfdi", source=cfdi_parent)
        if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            self._value_error(key="TipoCfdi", value=cfdi_type, source=f"{cfdi_parent}.TipoCfdi")
        if consid_purch_sale_price is None:
            self._nonfound_key_error(key="PrecioVentaOCompraContrap", source=cfdi_parent)
        if documented_volum is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=cfdi_parent)
        if transaction_date is None:
            self._nonfound_key_error(key="FechaYHoraTransaccion", source=cfdi_parent)
        if num_value is None:
            self._nonfound_key_error(key="ValorNumerico", source=cfdi_parent)
        if measure_unit is None:
            self._nonfound_key_error(key="UnidadDeMedida", source=cfdi_parent)

        if cfdi_val and not re.match(CFDI_REGEX, cfdi_val):
            self._regex_error(
                key="Cfdi", value=cfdi_val, pattern=CFDI_REGEX,
                source=f"{cfdi_parent}.Cfdi"
            )
        if consid_purch_sale_price and not 0 <= consid_purch_sale_price <= 1000000000000:
            self._min_max_value_error(
                key="PrecioVentaOCompraOContrap", value=consid_purch_sale_price, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.PrecioVentaOCompraOContrap"
            )
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
                source=f"{cfdi_parent}.FechaYHoraTransaccion"
            )
        if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
            self._regex_error(
                key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                source=f"{cfdi_parent}.VolumenDocumentado.UnidadDeMedida"
            )

    @exception_wrapper
    def _validate_extranjero(self):
        """Validate Extrajero objs.\n
        :return: None."""
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return
        # foreign_parent = "Extranjero"

        for fore_elem in foreign:
            fore_parent = f"Extranjero[{foreign.index(fore_elem)}]"
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=fore_elem,
                                                                    dict_type=complement_foreign):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message, source=fore_parent)
                return

            import_export_permission = fore_elem.get("PermisoImportacionOExportacion")
            pedimentos = fore_elem.get("Pedimentos")

            if import_export_permission is None:
                self._nonfound_key_error(key="PermisoImportacionOExportacion", source=f"{fore_parent}.Pedimentos")
            if import_export_permission and not re.match(IMPORT_PERMISSION_REGEX, import_export_permission):
                self._regex_error(
                    key="PermisoImportacionOExportacion", value=import_export_permission,
                    pattern=IMPORT_PERMISSION_REGEX, source=f"{fore_parent}.PermisoImportacionOExportacion"
                )

            if pedimentos:
                for pedimento in pedimentos:
                    self.__validate_pedimentos(pedimento=pedimento,
                                               pedi_parent=f"{fore_parent}.Pedimentos[{pedimentos.index(pedimento)}]"
                                               )

    @exception_wrapper
    def __validate_pedimentos(self, pedimento: dict, pedi_parent: str) -> None:
        """Validate Pedimentos objs.\n
        :return: None."""
        intern_extrac_point = pedimento.get("PuntoDeInternacionOExtraccion")
        origin_destiny_country = pedimento.get("PaisOrigenODestino")
        aduana_transp_med = pedimento.get("MedioDeTransEntraOSaleAduana")
        aduanal_pedimento = pedimento.get("PedimentoAduanal")
        incoterm = pedimento.get("Incoterms")
        import_export_price = pedimento.get("PrecioDeImportacionOExportacion")
        documented_volume = pedimento.get("VolumenDocumentado")
        num_value = documented_volume.get("ValorNumerico")
        measure_unit = documented_volume.get("UnidadDeMedida")

        if intern_extrac_point is None:
            self._nonfound_key_error(key="PuntoDeInternacionOExtraccion", source=f"{pedi_parent}")
        if origin_destiny_country is None:
            self._nonfound_key_error(key="PaisOrigenODestino", source=f"{pedi_parent}")
        if aduana_transp_med is None:
            self._nonfound_key_error(key="MedioDeTransEntraOSaleAduana", source=f"{pedi_parent}")
        if aduanal_pedimento is None:
            self._nonfound_key_error(key="PedimentoAduanal", source=f"{pedi_parent}")
        if incoterm is None:
            self._nonfound_key_error(key="Incoterms", source=f"{pedi_parent}")
        if import_export_price is None:
            self._nonfound_key_error(key="PrecioDeImportacionOExportacion")
        if documented_volume is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=f"{pedi_parent}")
        if num_value is None:
            self._nonfound_key_error(key="ValorNumerico", source=f"{pedi_parent}.VolumenDocumentado")
        if measure_unit is None:
            self._nonfound_key_error(key="UnidadDeMedida", source=f"{pedi_parent}.VolumenDocumentado")

        if intern_extrac_point and not re.match(INTERN_SPOT_REGEX, intern_extrac_point):
            self._regex_error(
                key="PuntoDeInternacionOExtraccion", value=intern_extrac_point, pattern=INTERN_SPOT_REGEX,
                source=f"{pedi_parent}.PuntoDeInternacionOExtraccion"
            )
        if intern_extrac_point and not 2 <= len(intern_extrac_point) <= 3:
            self._min_max_value_error(
                key="PuntoDeInternacionOExtraccion", value=intern_extrac_point, min_val=2, max_val=3,
                source=f"{pedi_parent}.PuntoDeInternacionOExtraccion"
            )
        if origin_destiny_country and origin_destiny_country not in CountryCode:
            self._value_error(
                key="PaisOrigenODestino", value=origin_destiny_country,
                source=f"{pedi_parent}.PaisOrigenODestino"
                )
        if aduana_transp_med and aduana_transp_med not in [item.value for item in AduanaEntrance]:
            self._value_error(
                key="MedioDeTransporteAduana", value=aduana_transp_med,
                source=f"{pedi_parent}.MedioDeTransporteAduana"
                )
        if aduanal_pedimento and not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
            print("entro aqui")
            self._regex_error(
                key="PedimentoAduanal", value=aduanal_pedimento, pattern=ADUANAL_PEDIMENTO,
                source=f"{pedi_parent}.PedimentoAduanal"
            )
        if aduanal_pedimento and len(aduanal_pedimento) != 21:
            self._longitud_error(
                key="PedimentoAduanal", value=aduanal_pedimento, min_long=21, max_long=21,
                source=f"{pedi_parent}.PedimentoAduanal"
            )
        if incoterm and incoterm not in IncotermCode.__members__:
            self._value_error(
                key="Incoterms", value=incoterm,
                source=f"{pedi_parent}.Incoterms"
                )
        if import_export_price and not 0 <= import_export_price <= 100000000000:
            self._min_max_value_error(
                key="PrecioDeImportacion", value=import_export_price, min_val=0, max_val=100000000000,
                source=f"{pedi_parent}.PrecioDeImportacion"
            )
        if num_value and not 0 <= num_value <= 100000000000:
            self._min_max_value_error(
                key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
                source=f"{pedi_parent}.VolumenDocumentado.ValorNumerico"
            )
        if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
            self._regex_error(
                key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                source=f"{pedi_parent}.VolumenDocumentado.UnidadDeMedida"
            )
