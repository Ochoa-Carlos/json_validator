import re

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_REGEX, PERMISSION_ALM_CDLRGN_REGEX, TRANSP_PERM_CDLRGN_REGEX,
                                   IMPORT_PERMISSION_REGEX, INTERN_SPOT_REGEX,
                                   MEASURE_UNIT, PERMISSION_ALM_DIST_REGEX,
                                   PERMISSION_PROOVE_CLIENT_REGEX, RFC_REGEX,
                                   TRANSPORT_PERM_REGEX, UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType, CountryCode,
                                     IncotermCode)
from src.custom_exceptions import LongitudError, RegexError, ValorMinMaxError
from src.decorators import exception_wrapper

# TODO claves de CDLRNG => TIPOCOMPLEMENTO TERMINALAMYTRANS CERTIFICADO NACIONAL EXTRANJERO ACLARACION
class CDLRGNComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemeto(self) -> None:
        if self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_dist()
            self._validate_certificado()
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

        alm_terminal = alm.get("TerminalAlm")
        alm_permission = alm.get("PermisoAlmacenamiento")

        if alm_terminal is None:
            raise KeyError("Error: clave 'TerminalAlm' no encontrada")
        if alm_permission is None:
            raise KeyError("Error: clave 'PermisoAlmacenamiento' no encontrada")

        if not 5 <= len(alm_terminal) <= 250:
            raise LongitudError(
                f"Error: clave 'TerminalAlm' con valor {alm_terminal} no tiene la longitud min 5 o max 250."
            )
        if not re.match(PERMISSION_ALM_CDLRGN_REGEX, alm_permission):
            raise RegexError(
                f"Error: clave 'PermisoAlmacenamiento' con valor {alm_permission} no cumple con el patrón {PERMISSION_ALM_CDLRGN_REGEX}"
            )

    @exception_wrapper
    def __validate_transporte(self, transp: dict) -> None:
        if transp is None:
            return

        perm_transp = transp.get("Permisotransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")

        if perm_transp is None:
            raise KeyError("Error: clave 'PermisoTransporte' no encontrada.")

        if not re.match(TRANSP_PERM_CDLRGN_REGEX, perm_transp):
            raise RegexError(
                f"Error: clave 'PermisoTransporte' con valor {perm_transp} no cumple con el patrón {TRANSP_PERM_CDLRGN_REGEX}"
            )
        if vehicle_key and 6 <= len(vehicle_key) <= 12:
            raise ValorMinMaxError(
                f"Error: clave 'ClaveDeVehiculo' con valor {vehicle_key} no se encuentra en el rango min 6 o max 12."
            )

    @exception_wrapper
    def _validate_nacional(self):
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            client_rfc = national_item.get("RfcCliente")
            client_name = national_item.get("NombreCliente")
            cfdis = national_item.get("CFDIs")

            if client_rfc is None:
                raise KeyError("Error: clave 'RfcCliente' no encontrada.")
            if client_name is None:
                raise KeyError("Error: clave 'NombreCliente' no encontrada.")

            if not re.match(RFC_REGEX, client_rfc):
                raise RegexError(
                    f"Error: clave 'RfcCliente' con valor {client_rfc} no cumple con el patron {RFC_REGEX}"
                    )
            if not 10 <= len(client_name) <= 150:
                raise LongitudError(
                    f"Error: clave 'NombreCliente' con valor '{client_name}' no se encuentra en el rango min 10 o max 300."
                    )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi: dict) -> None:
        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        consideration = cfdi.get("Contraprestacion")
        transaction_date = cfdi.get("FechaYHoraTransaccion")
        documented_volum = cfdi.get("VolumenDocumentado")
        num_value = documented_volum.get("ValorNumerico")
        measure_unit = documented_volum.get("UnidadDeMedida")

        if cfdi_val is None:
            raise KeyError("Error: clave 'Cfdi' no se encuentra.")
        if cfdi_type is None:
            raise KeyError("Error: clave 'TipoCfdi' no se encuentra.")
        if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            raise KeyError(f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válida.")
        if consideration is None:
            raise KeyError("Error: clave 'Contraprestacion' no se encuentra.")
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
        if not 1 <= consideration <= 1000000000000:
            raise ValorMinMaxError(
                f"Error: Clave 'Contraprestacion' con valor '{consideration}' no tiene el valor min 0 o max 1000000000000."
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
                f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}.")

    @exception_wrapper
    def _validate_extranjero(self):
        if (foreign := self.current_complement.get("Extranjero")) is None:
            return

        import_export_permission = foreign.get("PermisoImportacionOExportacion")
        pedimentos = foreign.get("Pedimentos")

        if import_export_permission is None:
            raise KeyError("Error: clave 'PermisoImportacionOExportacion' no se encuentra.")

        if not re.match(IMPORT_PERMISSION_REGEX, import_export_permission):
            raise RegexError(
                f"Error: clave 'PermisoImportacionOExportacion' con valor {import_export_permission} no cumple con el patron {IMPORT_PERMISSION_REGEX}"
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
        import_price = pedimento.get("PrecioDeImportacion")
        documented_volume = pedimento.get("VolumenDocumentado")
        num_value = documented_volume.get("ValorNumerico")
        measure_unit = documented_volume.get("UnidadDeMedida")

        if intern_extrac_point is None:
            raise KeyError("Error: clave 'PuntoDeInternacionOExtraccion' no se encuentra.")
        if origin_destiny_country is None:
            raise KeyError("Error: clave 'PaisOrigenODestino' no se encuentra.")
        if aduana_transp_med is None:
            raise KeyError("Error: clave 'MedioDeTransEntraOSaleAduana' no se encuentra.")
        if aduanal_pedimento is None:
            raise KeyError("Error: clave 'PedimentoAduanal' no se encuentra.")
        if incoterm is None:
            raise KeyError("Error: clave 'Incoterms' no se encuentra.")
        if import_price is None:
            raise KeyError("Error: clave 'PrecioDeImportacion' no se encuentra.")
        if documented_volume is None:
            raise KeyError("Error: clave 'VolumenDocumentado' no se encuentra.")
        if num_value is None:
            raise KeyError("Error: valor 'ValorNumerico' no se encuentra en clave 'ValorDocumentado'.")
        if measure_unit is None:
            raise KeyError("Error: valor 'UnidadDeMedida' no se encuentra en clave 'ValorDocumentado'.")

        if not re.match(INTERN_SPOT_REGEX, intern_extrac_point):
            raise RegexError(f"Error: clave 'PuntoDeInternacionOExtraccion' con valor {intern_extrac_point} no cumple con el patron {INTERN_SPOT_REGEX}")
        if not 2 <= intern_extrac_point <= 3:
            raise ValorMinMaxError(
                f"Error: clave 'PuntoDeInternacion' con valor {intern_extrac_point} no tiene la longitud min 2 o max 3."
            )
        if origin_destiny_country not in CountryCode:
            raise ValueError(f"Error: valor '{origin_destiny_country}' en clave 'PaisOrigenODestino' no válido.")
        if aduana_transp_med not in [item.value for item in AduanaEntrance]:
            raise ValueError(f"Error: valor '{aduana_transp_med}' en clave 'MedioDeTransporteAduana' no válido.")
        if not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
            raise RegexError(
                f"Error: clave 'PedimentoAduanal' con valor {aduanal_pedimento} no cumple con el patron {ADUANAL_PEDIMENTO}"
            )
        if len(aduanal_pedimento) != 21:
            raise LongitudError(
                f"Error: clave 'PedimentoAduanal' con valor '{aduanal_pedimento} no cumple con la longitud de 21.'"
            )
        if incoterm not in IncotermCode.__members__:
            raise ValueError(f"Error: clave 'Incoterms' con valor {incoterm} no válido.")
        if not 0 <= import_price <= 100000000000:
            raise ValorMinMaxError(
                f"Error: clave 'PrecioDeImportacion' con valor {import_price} no está en el valor min 0 o max 100000000000."
                )
        if not 0 <= num_value <= 100000000000:
            raise ValorMinMaxError(
                f"Error: clave 'ValorNumerico' con valor {num_value} no está en el valor min 0 o max 100000000000."
                )
        if not re.match(MEASURE_UNIT, measure_unit):
            raise RegexError(
                f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                )
