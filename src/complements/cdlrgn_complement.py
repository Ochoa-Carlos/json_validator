"""This module handle CDLRGN complemento."""
import re

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_REGEX,
                                       IMPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX, MEASURE_UNIT,
                                       PERMISSION_ALM_CDLRGN_REGEX, RFC_REGEX,
                                       TRANSP_PERM_CDLRGN_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import (ClaveError, LongitudError, RegexError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper


class CDLRGNComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemento(self) -> None:
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
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TerminalAlm' no encontrada"
                )
        if alm_permission is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoAlmacenamiento' no encontrada"
                )

        if alm_terminal and not 5 <= len(alm_terminal) <= 250:
            self._longitud_error(
                key="TerminalAlm", value=alm_terminal, min_long=5, max_long=250,
            )
            # self.catch_error(
            #     err_type=LongitudError,
            #     err_message=f"Error: clave 'TerminalAlm'
            # con valor {alm_terminal} no tiene la longitud min 5 o max 250.")
        if alm_permission and not re.match(PERMISSION_ALM_CDLRGN_REGEX, alm_permission):
            self._regex_error(
                key="PermisoAlmacenamiento", value=alm_permission, pattern=PERMISSION_ALM_CDLRGN_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PermisoAlmacenamiento'
            # con valor {alm_permission} no cumple con el patrón {PERMISSION_ALM_CDLRGN_REGEX}")

    @exception_wrapper
    def __validate_transporte(self, transp: dict) -> None:
        if transp is None:
            return

        perm_transp = transp.get("PermisoTransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")

        if perm_transp is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoTransporte' no encontrada."
                )
        if perm_transp and not re.match(TRANSP_PERM_CDLRGN_REGEX, perm_transp):
            self._regex_error(
                key="PermisoTransporte", value=perm_transp, pattern=TRANSP_PERM_CDLRGN_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'PermisoTransporte'
            # con valor {perm_transp} no cumple con el patrón {TRANSP_PERM_CDLRGN_REGEX}")
        if vehicle_key and 6 <= len(vehicle_key) <= 12:
            self._min_max_value_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_val=6, max_val=12,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'ClaveDeVehiculo'
            # con valor {vehicle_key} no se encuentra en el rango min 6 o max 12.")

    @exception_wrapper
    def _validate_nacional(self):
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            client_rfc = national_item.get("RfcCliente")
            client_name = national_item.get("NombreCliente")
            cfdis = national_item.get("CFDIs")

            if client_rfc is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: clave 'RfcCliente' no encontrada."
                    )
            if client_name is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: clave 'NombreCliente' no encontrada."
                    )
            if client_rfc and not re.match(RFC_REGEX, client_rfc):
                self._regex_error(
                    key="RfcCliente", value=client_rfc, pattern=RFC_REGEX,
                )
                # self.catch_error(
                #     err_type=RegexError,
                #     err_message=f"Error: clave 'RfcCliente'
                # con valor {client_rfc} no cumple con el patron {RFC_REGEX}")
            if client_name and not 10 <= len(client_name) <= 150:
                self._longitud_error(
                    key="NombreCliente", value=client_name, min_long=10, max_long=150,
                )
                # self.catch_error(
                #     err_type=LongitudError,
                #     err_message=f"Error: clave 'NombreCliente'
                # con valor '{client_name}' no se encuentra en el rango min 10 o max 300.")

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
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Cfdi' no se encuentra."
                )
        if cfdi_type is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TipoCfdi' no se encuentra."
                )
        if cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            self.catch_error(
                err_type=ClaveError,
                err_message=f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válida."
                )
        if consideration is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Contraprestacion' no se encuentra."
                )
        if transaction_date is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'FechaYHoraTransaccion' no se encuentra."
                )
        if documented_volum is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'VolumenDocumentado' no se encuentra."
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
            #     err_type=RegexError,err_message=f"Error: clave 'Cfdi'
            # con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}")
        if consideration and not 1 <= consideration <= 1000000000000:
            self._min_max_value_error(
                key="Contraprestacion", value=consideration, min_val=1, max_val=1000000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: Clave 'Contraprestacion'
            # con valor '{consideration}' no tiene el valor min 0 o max 1000000000000.")
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
            )
            # self.catch_error(
            #     err_type=RegexError,
            #     err_message=f"Error: clave 'FechaYHoraTransaccion'
            # con valor {transaction_date} no cumple con el regex {UTC_FORMAT_REGEX}")
        if num_value and not 0 <= num_value <= 100000000000:
            self._min_max_value_error(
                key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'ValorNumerico'
            # con valor {num_value} no tiene el valor min 0 o max 100000000000.")
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

        import_export_permission = foreign.get("PermisoImportacionOExportacion")
        pedimentos = foreign.get("Pedimentos")

        if import_export_permission is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoImportacionOExportacion' no se encuentra."
                )
        if import_export_permission and not re.match(IMPORT_PERMISSION_REGEX, import_export_permission):
            self._regex_error(
                key="PermisoImportacionOExportacion", value=import_export_permission, pattern=IMPORT_PERMISSION_REGEX,
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
        import_price = pedimento.get("PrecioDeImportacion")
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
        if import_price is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PrecioDeImportacion' no se encuentra."
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
        if intern_extrac_point and not 2 <= intern_extrac_point <= 3:
            self._min_max_value_error(
                key="PuntoDeInternacion", value=intern_extrac_point, min_val=2, max_val=3,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'PuntoDeInternacion'
            # con valor {intern_extrac_point} no tiene la longitud min 2 o max 3.")
        if CountryCode and origin_destiny_country not in CountryCode:
            self._value_error(
                key="PaisOrigenODestino", value=origin_destiny_country
                )
            # self.catch_error(
            #     err_type=ValorError,
            #     err_message=f"Error: valor '{origin_destiny_country}' en clave 'PaisOrigenODestino' no válido."
            #     )
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
            #     err_message=f"Error: clave 'Incoterms'
            # con valor {incoterm} no válido.")
        if import_price and not 0 <= import_price <= 100000000000:
            self._min_max_value_error(
                key="PrecioDeImportacion", value=import_price, min_val=0, max_val=100000000000,
            )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message=f"Error: clave 'PrecioDeImportacion'
            # con valor {import_price} no está en el valor min 0 o max 100000000000.")
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
