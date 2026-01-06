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
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TerminalAlmYDist' no encontrada"
                )
        if alm_dist_alm is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoAlmYDist' no encontrada"
                )

        if alm_dist_terminal and not 5 <= len(alm_dist_terminal) <= 250:
            self._longitud_error(
                key="TerminalAlmYDist", value=alm_dist_terminal, min_long=5, max_long=250,
            )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message=f"Error: clave 'TerminalAlmYDist'
            # con valor {alm_dist_terminal} no tiene la longitud min 5 o max 250.")
        if alm_dist_alm and not re.match(PERMISSION_ALM_DIST_REGEX, alm_dist_alm):
            self._regex_error(
                key="PermisoAlmYDist", value=alm_dist_alm, pattern=PERMISSION_ALM_DIST_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PermisoAlmYDist'
            # con valor {alm_dist_alm} no cumple con el patrón {PERMISSION_ALM_DIST_REGEX}")
        if alm_fee and not 0 <= alm_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeAlmacenamiento", value=alm_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'TarifaDeAlmacenamiento'
            # con valor {alm_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if alm_cap_fee and not 0 <= alm_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadAlmac", value=alm_cap_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'CargoPorCapacidadAlmac'
            # con valor {alm_cap_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if alm_use_fee and not 0 <= alm_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoAlamc", value=alm_use_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'CargoPorUsoAlamc'
            # con valor {alm_use_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if volume_alm_fee and not 0 <= volume_alm_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoAlmac", value=volume_alm_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'CargoVolumetricoAlmac'
            # con valor {volume_alm_fee} no se encuentra en el rango min 0 o max 1000000000000.")

    @exception_wrapper
    def __validate_transporte(self, transp: dict) -> None:
        if transp is None:
            return
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transp,
                                                                    dict_type=terminal_alm):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
            return

        perm_transp = transp.get("PermisoTransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")
        transp_fee = transp.get("TarifaDeTransporte")
        transp_cap_fee = transp.get("CargoPorCapacidadTrans")
        transp_use_fee = transp.get("CargoPorUsoTrans")
        transp_volume_fee = transp.get("CargoVolumetricoTrans")

        if perm_transp is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoTransporte' no encontrada."
                )
        if transp_fee is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TarifaDeTransporte' no encontrada."
                )

        if perm_transp and not re.match(TRANSPORT_PERM_REGEX, perm_transp):
            self._regex_error(
                key="PermisoTransporte", value=perm_transp, pattern=TRANSPORT_PERM_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PermisoTransporte'
            # con valor {perm_transp} no cumple con el patrón {TRANSPORT_PERM_REGEX}")
        if vehicle_key and 6 <= len(vehicle_key) <= 12:
            self._min_max_value_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_val=6, max_val=12,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'ClaveDeVehiculo'
            # con valor {vehicle_key} no se encuentra en el rango min 6 o max 12.")
        if transp_fee and not 0 <= transp_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeTransporte", value=transp_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'TarifaDeTransporte'
            # con valor {transp_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if transp_cap_fee and not 0 <= transp_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadTrans", value=transp_cap_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'CargoPorCapacidadTrans'
            # con valor {transp_cap_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if transp_use_fee and not 0 <= transp_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=transp_use_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
                # err_type=ValorMinMaxError,
                # err_message=f"Error: clave 'CargoPorUsoTrans'
            # con valor {transp_use_fee} no se encuentra en el rango min 0 o max 1000000000000.")
        if transp_volume_fee and not 0 <= transp_volume_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=transp_volume_fee, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'CargoVolumetricoTrans'
            # con valor {transp_volume_fee} no se encuentra en el rango min 0 o max 1000000000000.")

    @exception_wrapper
    def _validate_nacional(self):
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                    dict_type=complement_national):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
                return

            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            custom_client_permission = national_item.get("PermisoClienteOProveedor")
            cfdis = national_item.get("CFDIs")

            if custom_client_rfc is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: clave 'RfcClienteOProveedor' no encontrada."
                    )
            if custom_client_rfc and not re.match(RFC_REGEX, custom_client_rfc):
                self._regex_error(
                    key="RfcClienteOProveedor", value=custom_client_rfc, pattern=RFC_REGEX,
                )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'RfcClienteOProveedor'
                # con valor {custom_client_rfc} no cumple con el patron {RFC_REGEX}")
            if custom_client_name and not 10 <= len(custom_client_name) <= 150:
                self._longitud_error(
                    key="NombreClienteOProveedor", value=custom_client_name, min_long=10, max_long=150,
                )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message=f"Error: clave 'NombreClienteOProveedor'
                # con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300.")
            if custom_client_permission and not re.match(PERMISSION_PROOVE_CLIENT_REGEX, custom_client_permission):
                self._regex_error(
                    key="PermisoClienteOProveedor", value=custom_client_permission,
                    pattern=PERMISSION_PROOVE_CLIENT_REGEX,
                )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'PermisoClienteOProveedor'
                # con valor {custom_client_permission} no cumple con el patron {PERMISSION_PROOVE_CLIENT_REGEX}")

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi):
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
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Cfdi' no se encuentra."
                )
        if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            self.catch_error(
                err_type=ClaveError,
                err_message=f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válido."
                )
        if consid_purch_sale_price is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PrecioVentaOCompraContrap' no se encuentra."
                )
        if documented_volum is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'VolumenDocumentado' no se encuentra."
                )
        if transaction_date is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'FechaYHoraTransaccion' no se encuentra."
                )
        if num_value is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'."
                )
        if measure_unit is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'."
                )
        if cfdi_val and not re.match(CFDI_REGEX, cfdi_val):
            self._regex_error(
                key="Cfdi", value=cfdi_val, pattern=CFDI_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el patron {CFDI_REGEX}")
        if consid_purch_sale_price and not 0 <= consid_purch_sale_price <= 1000000000000:
            self._min_max_value_error(
                key="PrecioVentaOCompraOContrap", value=consid_purch_sale_price, min_val=0, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: Clave 'PrecioVentaOCompraOContrap'
            # con valor '{consid_purch_sale_price}' no tiene el valor min 0 o max 1000000000000.")
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'FechaYHoraTransaccion'
            # con valor {transaction_date} no cumple con el patron {UTC_FORMAT_REGEX}")
        if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
            self._regex_error(
                key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'UnidadDeMedida'
            # con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")

    @exception_wrapper
    def _validate_extranjero(self):
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return

        for fore_elem in foreign:
            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=fore_elem,
                                                                    dict_type=complement_foreign):
                type_err = err.get("type_err")
                err_message = err.get("err_message")
                self.catch_error(err_type=type_err, err_message=err_message)
                return

            import_export_permission = fore_elem.get("PermisoImportacionOExportacion")
            pedimentos = fore_elem.get("Pedimentos")

            if import_export_permission is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: clave 'PermisoImportacionOExportacion' no se encuentra."
                    )
            if import_export_permission and not re.match(IMPORT_PERMISSION_REGEX, import_export_permission):
                self._regex_error(
                    key="PermisoImportacionOExportacion", value=import_export_permission,
                    pattern=IMPORT_PERMISSION_REGEX,
                )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'PermisoImportacionOExportacion'
                # con valor {import_export_permission} no cumple con el patron {IMPORT_PERMISSION_REGEX}")

            if pedimentos:
                for pedimento in pedimentos:
                    self.__validate_pedimentos(pedimento=pedimento)

    @exception_wrapper
    def __validate_pedimentos(self, pedimento: dict) -> None:
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
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PuntoDeInternacionOExtraccion' no se encuentra."
                )
        if origin_destiny_country is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PaisOrigenODestino' no se encuentra."
                )
        if aduana_transp_med is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'MedioDeTransEntraOSaleAduana' no se encuentra."
                )
        if aduanal_pedimento is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PedimentoAduanal' no se encuentra."
                )
        if incoterm is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Incoterms' no se encuentra."
                )
        if import_export_price is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PrecioDeImportacionOExportacion' no se encuentra."
                )
        if documented_volume is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'VolumenDocumentado' no se encuentra."
                )
        if num_value is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: valor 'ValorNumerico' no se encuentra en clave 'ValorDocumentado'."
                )
        if measure_unit is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: valor 'UnidadDeMedida' no se encuentra en clave 'ValorDocumentado'."
                )
        if intern_extrac_point and not re.match(INTERN_SPOT_REGEX, intern_extrac_point):
            self._regex_error(
                key="PuntoDeInternacionOExtraccion", value=intern_extrac_point, pattern=INTERN_SPOT_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PuntoDeInternacionOExtraccion'
            # con valor {intern_extrac_point} no cumple con el patron {INTERN_SPOT_REGEX}")
        if intern_extrac_point and not 2 <= len(intern_extrac_point) <= 3:
            self._min_max_value_error(
                key="PuntoDeInternacion", value=intern_extrac_point, min_val=2, max_val=3,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'PuntoDeInternacion'
            # con valor {intern_extrac_point} no tiene la longitud min 2 o max 3.")
        if origin_destiny_country and origin_destiny_country not in CountryCode:
            self._value_error(
                key="PaisOrigenODestino", value=origin_destiny_country
                )
            # self.catch_error(
            #     err_type=ValorError,
            #     err_message=f"Error: valor '{origin_destiny_country}'
            # en clave 'PaisOrigenODestino' no válido.")
        if aduana_transp_med and aduana_transp_med not in [item.value for item in AduanaEntrance]:
            self._value_error(
                key="MedioDeTransporteAduana", value=aduana_transp_med
                )
            # self.catch_error(
            #     err_type=ValorError,
            #     err_message=f"Error: valor '{aduana_transp_med}'
            # en clave 'MedioDeTransporteAduana' no válido.")
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
        if import_export_price and not 0 <= import_export_price <= 100000000000:
            self._min_max_value_error(
                key="PrecioDeImportacion", value=import_export_price, min_val=0, max_val=100000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'PrecioDeImportacion'
            # con valor {import_export_price} no tiene el valor min 0 o max 100000000000.")
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
