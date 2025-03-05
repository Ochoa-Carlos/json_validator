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


class ComercializationComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemeto(self) -> None:
        """Validate comercialization complement items."""
        if self._next_complement():
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

        alm_dist_terminal = alm.get("TerminalAlmYDist")
        alm_dist_alm = alm.get("PermisoAlmYDist")
        alm_fee = alm.get("TarifaDeAlmacenamiento")
        alm_cap_fee = alm.get("CargoPorCapacidadAlmac")
        alm_use_fee = alm.get("CargoPorUsoAlmac")
        volume_alm_fee = alm.get("CargoVolumetricoAlmac")

        if alm_dist_terminal is None:
            self.catch_error(
                err_type=KeyError,
                err_message="Error: clave 'TerminalAlmYDist' no encontrada"
                )

        if not 5 <= len(alm_dist_terminal) <= 250:
            self.catch_error(
                err_type=LongitudError,
                err_message=f"Error: clave 'PermisoAlmYDist' con valor {alm_dist_alm} no tiene la longitud min 5 o max 250."
                )
        if not re.match(PERMISSION_ALM_DIST_REGEX, alm_dist_alm):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PermisoAlmYDist' con valor {alm_dist_alm} no cumple con el patrón {PERMISSION_ALM_DIST_REGEX}"
                )
        if alm_fee and not 0 <= alm_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'TarifaDeAlmacenamiento' con valor {alm_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if alm_cap_fee and not 0 <= alm_cap_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoPorCapacidadAlmac' con valor {alm_cap_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if alm_use_fee and not 0 <= alm_use_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoPorUsoAlamc' con valor {alm_use_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if volume_alm_fee and not 0 <= volume_alm_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoVolumetricoAlmac' con valor {volume_alm_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )

    @exception_wrapper
    def __validate_transporte(self, transp: dict) -> None:
        if transp is None:
            return

        perm_transp = transp.get("PermisoTransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")
        transp_fee = transp.get("TarifaDeTransporte")
        transp_cap_fee = transp.get("CargoPorCapacidadTrans")
        transp_use_fee = transp.get("CargoPorUsoTrans")
        transp_volume_fee = transp.get("CargoVolumetricoTrans")

        if perm_transp is None:
            self.catch_error(
                err_type=KeyError,
                err_message="Error: clave 'PermisoTransporte' no encontrada."
                )
        if transp_fee is None:
            self.catch_error(
                err_type=KeyError,
                err_message="Error: clave 'TarifaDeTransporte' no encontrada."
                )

        if not re.match(TRANSPORT_PERM_REGEX, perm_transp):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PermisoTransporte' con valor {perm_transp} no cumple con el patrón {TRANSPORT_PERM_REGEX}"
                )
        if vehicle_key and 6 <= len(vehicle_key) <= 12:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'ClaveDeVehiculo' con valor {vehicle_key} no se encuentra en el rango min 6 o max 12."
                )
        if transp_fee and not 0 <= transp_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'TarifaDeTransporte' con valor {transp_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if transp_cap_fee and not 0 <= transp_cap_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoPorCapacidadTrans' con valor {transp_cap_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if transp_use_fee and not 0 <= transp_use_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoPorCapacidadTrans' con valor {transp_use_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )
        if transp_volume_fee and not 0 <= transp_volume_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'CargoVolumetricoTrans' con valor {transp_volume_fee} no se encuentra en el rango min 0 o max 1000000000000."
                )

    @exception_wrapper
    def _validate_nacional(self):
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            custom_client_rfc = national_item.get("RfcClienteOProveedor")
            custom_client_name = national_item.get("NombreClienteOProveedor")
            custom_client_permission = national_item.get("PermisoClienteOProveedor")
            cfdis = national_item.get("CFDIs")

            if custom_client_rfc is None:
                self.catch_error(
                    err_type=KeyError,
                    err_message="Error: clave 'RfcClienteOProveedor' no encontrada."
                    )
            if custom_client_permission is None:
                self.catch_error(
                    err_type=KeyError,
                    err_message="Error: clave 'PermisoClienteOProveedor' no encontrada."
                    )

            if not re.match(RFC_REGEX, custom_client_rfc):
                self.catch_error(
                    err_type=RegexError,
                    err_message=f"Error: clave 'RfcClienteOProveedor' con valor {custom_client_rfc} no cumple con el patron {RFC_REGEX}"
                    )
            if not 10 <= len(custom_client_name) <= 150:
                self.catch_error(
                    err_type=LongitudError,
                    err_message=f"Error: clave 'NombreClienteOProveedor' con valor '{custom_client_name}' no se encuentra en el rango min 10 o max 300."
                    )
            if custom_client_permission and not re.match(PERMISSION_PROOVE_CLIENT_REGEX, custom_client_permission):
                self.catch_error(
                    err_type=RegexError,
                    err_message=f"Error: clave 'PermisoClienteOProveedor' con valor {custom_client_permission} no cumple con el patron {PERMISSION_PROOVE_CLIENT_REGEX}"
                    )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi):
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

        if not re.match(CFDI_REGEX, cfdi_val):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el patron {CFDI_REGEX}"
                )
        if not 1 <= consid_purch_sale_price <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'PrecioVentaOCompraOContrap' con valor '{consid_purch_sale_price}' no tiene el valor min 0 o max 1000000000000."
                )
        if not re.match(UTC_FORMAT_REGEX, transaction_date):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'FechaYHoraTransaccion' con valor {transaction_date} no cumple con el patron {UTC_FORMAT_REGEX}"
                )
        if not re.match(MEASURE_UNIT, measure_unit):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                )

    @exception_wrapper
    def _validate_extranjero(self):
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return

        import_export_permission = foreign.get("PermisoImportacionOExportacion")
        pedimentos = foreign.get("Pedimentos")

        if import_export_permission is None:
            self.catch_error(
                err_type=KeyError,
                err_message="Error: clave 'PermisoImportacionOExportacion' no se encuentra."
                )

        if not re.match(IMPORT_PERMISSION_REGEX, import_export_permission):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PermisoImportacionOExportacion' con valor {import_export_permission} no cumple con el patron {IMPORT_PERMISSION_REGEX}"
                )

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

        if not re.match(INTERN_SPOT_REGEX, intern_extrac_point):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PuntoDeInternacionOExtraccion' con valor {intern_extrac_point} no cumple con el patron {INTERN_SPOT_REGEX}"
                )
        if not 2 <= intern_extrac_point <= 3:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'PuntoDeInternacion' con valor {intern_extrac_point} no tiene la longitud min 2 o max 3."
                )
        if origin_destiny_country not in CountryCode:
            self.catch_error(
                err_type=ValorError,
                err_message=f"Error: valor '{origin_destiny_country}' en clave 'PaisOrigenODestino' no válido."
                )
        if aduana_transp_med not in [item.value for item in AduanaEntrance]:
            self.catch_error(
                err_type=ValorError,
                err_message=f"Error: valor '{aduana_transp_med}' en clave 'MedioDeTransporteAduana' no válido."
                )
        if not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PedimentoAduanal' con valor {aduanal_pedimento} no cumple con el patron {ADUANAL_PEDIMENTO}"
                )
        if len(aduanal_pedimento) != 21:
            self.catch_error(
                err_type=LongitudError,
                err_message=f"Error: clave 'PedimentoAduanal' con valor '{aduanal_pedimento} no cumple con la longitud de 21.'"
                )
        if incoterm not in IncotermCode.__members__:
            self.catch_error(
                err_type=ValorError,
                err_message=f"Error: clave 'Incoterms' con valor {incoterm} no válido."
                )
        if not 0 <= import_export_price <= 100000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'PrecioDeImportacion' con valor {import_export_price} no tiene el valor min 0 o max 100000000000."
                )
        if not 0 <= num_value <= 100000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: clave 'ValorNumerico' con valor {num_value} no está en el valor min 0 o max 100000000000."
                )
        if not re.match(MEASURE_UNIT, measure_unit):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                )
