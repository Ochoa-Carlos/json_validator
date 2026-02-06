"""This module handle Transporte complemento."""
import re
from typing import Any, Dict

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (CFDI_REGEX, MEASURE_UNIT,
                                       PERMISSION_ALM_TRANSP_REGEX, RFC_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import CfdiType
from src.decorators import exception_wrapper


class TransportComplement(ComplementBuilder):
    """Complement for comercialization type."""
    def validate_complemento(self) -> None:
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
        """Validate Alm y Dist obj."""
        if (alm_terminal := self.current_complement.get("TerminalAlmYDist")) is None:
            return

        alm_terminal = alm_terminal.get("TerminalAlmYDist")
        alm_permission = alm_terminal.get("PermisoAlmYDist")

        if alm_terminal is None:
            self._nonfound_key_error(key="TerminalAlmYDist")
        if alm_permission is None:
            self._nonfound_key_error(key="PermisoAlmYDist")

        if alm_terminal and not 5 <= len(alm_terminal) <= 250:
            self._longitud_error(
                key="TerminalAlmYDist", value=alm_terminal, min_long=21, max_long=21,
                )
        if alm_permission and not re.match(PERMISSION_ALM_TRANSP_REGEX, alm_permission):
            self._regex_error(
                key="RfcCliente", value=alm_permission, pattern=PERMISSION_ALM_TRANSP_REGEX,
                )

    @exception_wrapper
    def _validate_nacional(self):
        """Validate Nacional list."""
        if (national := self.current_complement.get("Nacional")) is None:
            return

        for national_item in national:
            client_rfc = national_item.get("RfcCliente")
            client_name = national_item.get("NombreCliente")
            cfdis = national_item.get("CFDIs")

            if client_rfc is None:
                self._nonfound_key_error(key="RfcCliente")
            if client_name is None:
                self._nonfound_key_error(key="NombreCliente")
            if client_rfc and not re.match(RFC_REGEX, client_rfc):
                self._regex_error(
                    key="RfcCliente", value=client_rfc, pattern=RFC_REGEX,
                )
            if client_name and not 10 <= len(client_name) <= 150:
                self._longitud_error(
                    key="NombreCliente", value=client_name, min_long=10, max_long=150,
                )

            if cfdis:
                for cfdi in cfdis:
                    self.__validate_cfdi(cfdi=cfdi)

    @exception_wrapper
    def __validate_cfdi(self, cfdi: Dict[str, Any]) -> None:
        """Validate cfdis obj."""
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
            self._nonfound_key_error(key="Cfdi")
        if cfdi_type is None:
            self._nonfound_key_error(key="TipoCfdi")
        if cfdi_type and cfdi_type not in [cfdi.value for cfdi in CfdiType]:
            self._value_error(key="TipoCfdi", value=cfdi_type)
        if consideration is None:
            self._nonfound_key_error(key="Contraprestacion")
        if transp_fee is None:
            self._nonfound_key_error(key="TarifaDeTransporte")
        if transaction_date is None:
            self._nonfound_key_error(key="FechaYHoraTransaccion")
        if documented_volum is None:
            self._nonfound_key_error(key="VolumenDocumentado")
        if documented_volum:
            num_value = documented_volum.get("ValorNumerico")
            measure_unit = documented_volum.get("UnidadDeMedida")
            if num_value is None:
                self._nonfound_key_error(key="ValorNumerico")
            if measure_unit is None:
                self._nonfound_key_error(key="UnidadDeMedida")
            if num_value and not 0 <= num_value <= 100000000000:
                self._min_max_value_error(
                    key="ValorNumerico", value=num_value, min_val=0, max_val=100000000000,
                )
            if measure_unit and not re.match(MEASURE_UNIT, measure_unit):
                self._regex_error(
                    key="UnidadDeMedida", value=measure_unit, pattern=MEASURE_UNIT,
                )

        if cfdi_val and not re.match(CFDI_REGEX, cfdi_val):
            self._regex_error(
                key="Cfdi", value=cfdi_val, pattern=CFDI_REGEX,
            )
        if consideration and not 1 <= consideration <= 1000000000000:
            self._min_max_value_error(
                key="Contraprestacion", value=consideration, min_val=1, max_val=1000000000000,
            )
        if transp_fee and not 1 <= transp_fee <= 1000000000000:
            self._min_max_value_error(
                key="TarifaDeTransporte", value=transp_fee, min_val=1, max_val=1000000000000,
            )
        if trans_cap_fee and not 1 <= trans_cap_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorCapacidadDeTrans", value=trans_cap_fee, min_val=1, max_val=1000000000000,
            )
        if trans_use_fee and not 1 <= trans_use_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=trans_use_fee, min_val=1, max_val=1000000000000,
            )
        if trans_vol_fee and not 1 <= trans_vol_fee <= 1000000000000:
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=trans_vol_fee, min_val=1, max_val=1000000000000,
            )
        if discount and not 1 <= discount <= 1000000000000:
            self._min_max_value_error(
                key="Descuento", value=discount, min_val=1, max_val=1000000000000,
            )
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
            )
