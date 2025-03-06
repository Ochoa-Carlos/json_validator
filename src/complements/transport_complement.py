import re

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (CFDI_REGEX, MEASURE_UNIT,
                                       PERMISSION_ALM_TRANSP_REGEX, RFC_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import CfdiType
from src.custom_exceptions import (ClaveError, LongitudError, RegexError,
                                   ValorMinMaxError)
from src.decorators import exception_wrapper


class TransportComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemeto(self) -> None:
        if self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_dist()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_aclaracion()

            self._update_index()
            self.validate_complemento()

    @exception_wrapper
    def _validate_terminal_alm_dist(self) -> None:
        if (alm_terminal := self.current_complement.get("TerminalAlmYDist")) is None:
            return

        alm_terminal = alm_terminal.get("TerminalAlmYDist")
        alm_permission = alm_terminal.get("PermisoAlmYDist")

        if alm_terminal is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TerminalAlmYDist' no encontrada"
                )
        if alm_permission is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'PermisoAlmYDist' no encontrada"
                )

        if alm_terminal and not 5 <= len(alm_terminal) <= 250:
            self.catch_error(
                err_type=LongitudError,
                err_message=f"Error: clave 'TerminalAlmYDist' con valor {alm_terminal} no tiene la longitud min 5 ó max 250."
                )
        if alm_permission and not re.match(PERMISSION_ALM_TRANSP_REGEX, alm_permission):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'PermisoAlmYDist' con valor {alm_permission} no cumple con el patrón {PERMISSION_ALM_TRANSP_REGEX}"
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
                self.catch_error(
                    err_type=RegexError,
                    err_message=f"Error: clave 'RfcCliente' con valor {client_rfc} no cumple con el patron {RFC_REGEX}"
                    )
            if client_name and not 10 <= len(client_name) <= 150:
                self.catch_error(
                    err_type=LongitudError,
                    err_message=f"Error: clave 'NombreCliente' con valor '{client_name}' no se encuentra en el rango min 10 o max 300."
                    )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi: dict) -> None:
        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        consideration = cfdi.get("Contraprestacion")
        transp_fee = cfdi.get("TarifaDeTransporte")
        trans_cap_fee = cfdi.get("CargoPorCapacidadDeTrans")
        trans_use_fee = cfdi.get("CargoPorUsoTrans")
        trans_vol_fee = cfdi.get("CargoVolumetricoTrans")
        discount = cfdi.get("Descuento")
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
        if cfdi_type and cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            self.catch_error(
                err_type=ClaveError,
                err_message=f"Error: clave 'TipoCfdi' con valor {cfdi_type} no válida."
                )
        if consideration is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Contraprestacion' no se encuentra."
                )
        if transp_fee is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TarifaDeTransporte' no se encuentra."
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
        if documented_volum:
            num_value = documented_volum.get("ValorNumerico")
            measure_unit = documented_volum.get("UnidadDeMedida")
            if num_value is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: objeto 'ValorNumerico' no se encuentra en clave 'VolumenDocumentado'."
                    )
            if measure_unit is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: objeto 'UnidadDeMedida' no se encuentra en clave 'VolumenDocumentado'."
                    )
            if num_value and not 0 <= num_value <= 100000000000:
                self.catch_error(
                    err_type=ValorMinMaxError,
                    err_message=f"Error: clave 'ValorNumerico' con valor {num_value} no tiene el valor min 0 o max 100000000000."
                    )
            if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
                self.catch_error(
                    err_type=RegexError,
                    err_message=f"Error: clave 'UnidadDeMedida' con valor {measure_unit} no cumple con el patron {MEASURE_UNIT}."
                    )

        if cfdi_val and not re.match(CFDI_REGEX, cfdi_val):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'Cfdi' con valor {cfdi_val} no cumple con el regex {CFDI_REGEX}"
                )
        if consideration and not 1 <= consideration <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'Contraprestacion' con valor '{consideration}' no tiene el valor min 0 o max 1000000000000."
                )
        if transp_fee and not 1 <= transp_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'TarifaDeTransporte' con valor '{transp_fee}' no tiene el valor min 0 o max 1000000000000."
                )
        if trans_cap_fee and not 1 <= trans_cap_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'CargoPorCapacidadDeTrans' con valor '{trans_cap_fee}' no tiene el valor min 0 o max 1000000000000."
                )
        if trans_use_fee and not 1 <= trans_use_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'CargoPorUsoTrans' con valor '{trans_use_fee}' no tiene el valor min 0 o max 1000000000000."
                )
        if trans_vol_fee and not 1 <= trans_vol_fee <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'CargoVolumetricoTrans' con valor '{trans_vol_fee}' no tiene el valor min 0 o max 1000000000000."
                )
        if discount and not 1 <= discount <= 1000000000000:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message=f"Error: Clave 'CargoVolumetricoTrans' con valor '{discount}' no tiene el valor min 0 o max 1000000000000."
                )
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: clave 'FechaYHoraTransaccion' con valor {transaction_date} no se expresa en formato yyyy-mm-ddThh:mm:ss+-hh:mm"
                )
