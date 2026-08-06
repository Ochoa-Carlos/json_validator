"""This module validate Transporte Complement Element."""
from typing import Any

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (CFDI_STRICT_REGEX, CLIENT_NAME_REGEX,
                                       PERMISSION_ALM_DIST_REGEX, RFC_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import CfdiType
from src.custom_exceptions import ValorError
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (national_client, transp_cfdis, transp_complement,
                            transp_terminal_alm_dist)


class TransportComplement(ComplementBuilder):
    """Validation of transport complement type."""

    def validate_complemento(self) -> None:
        """Validate every Transporte complement declared in the report."""
        while self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_dist()
            self._validate_trasvase()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_aclaracion()

            self._update_index()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        """Validate value types declared at the Transporte complement root.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement,
                                                              dict_type=transp_complement):
            self._type_error(err=err)

    @exception_wrapper
    def _validate_terminal_alm_dist(self) -> None:
        """Validate TerminalAlmYDist object, which is flat in the Transporte complement.\n
        :return: None."""
        if (alm_terminal := self.current_complement.get("TerminalAlmYDist")) is None:
            return
        if not isinstance(alm_terminal, dict):
            return

        terminal_parent = "TerminalAlmYDist"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm_terminal,
                                                              dict_type=transp_terminal_alm_dist):
            self._type_error(err=err, source=terminal_parent)

        alm_terminal_name = alm_terminal.get("TerminalAlmYDist")
        alm_permission = alm_terminal.get("PermisoAlmYDist")

        if alm_terminal_name is None:
            self._nonfound_key_error(key="TerminalAlmYDist", source=terminal_parent)
        if alm_permission is None:
            self._nonfound_key_error(key="PermisoAlmYDist", source=terminal_parent)

        if self._invalid_length(value=alm_terminal_name, min_long=5, max_long=250):
            self._longitud_error(
                key="TerminalAlmYDist", value=alm_terminal_name, min_long=5, max_long=250,
                source=f"{terminal_parent}.TerminalAlmYDist"
            )
        if self._invalid_pattern(value=alm_permission, pattern=PERMISSION_ALM_DIST_REGEX):
            self._regex_error(
                key="PermisoAlmYDist", value=alm_permission, pattern=PERMISSION_ALM_DIST_REGEX,
                source=f"{terminal_parent}.PermisoAlmYDist"
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
                                                                  dict_type=national_client):
                self._type_error(err=err, source=national_parent)

            client_rfc = national_item.get("RfcCliente")
            client_name = national_item.get("NombreCliente")
            cfdis = national_item.get("CFDIs")

            if client_rfc is None:
                self._nonfound_key_error(key="RfcCliente", source=national_parent)
            if client_name is None:
                self._nonfound_key_error(key="NombreCliente", source=national_parent)

            if self._invalid_pattern(value=client_rfc, pattern=RFC_REGEX):
                self._regex_error(
                    key="RfcCliente", value=client_rfc, pattern=RFC_REGEX,
                    source=f"{national_parent}.RfcCliente"
                )
            if self._invalid_length(value=client_name, min_long=1, max_long=150):
                self._longitud_error(
                    key="NombreCliente", value=client_name, min_long=1, max_long=150,
                    source=f"{national_parent}.NombreCliente"
                )
            if self._invalid_pattern(value=client_name, pattern=CLIENT_NAME_REGEX):
                self._regex_error(
                    key="NombreCliente", value=client_name, pattern=CLIENT_NAME_REGEX,
                    source=f"{national_parent}.NombreCliente"
                )

            if cfdis and isinstance(cfdis, list):
                for cfdi_index, cfdi in enumerate(cfdis):
                    self.__validate_cfdi(cfdi=cfdi, cfdi_parent=f"{national_parent}.CFDIs[{cfdi_index}]")

    @exception_wrapper
    def __validate_cfdi(self, cfdi: Any, cfdi_parent: str) -> None:
        """Validate a Nacional CFDIs object.\n
        :param cfdi: CFDIs object declared in the Nacional element.\n
        :param cfdi_parent: Object reference where the CFDIs object is placed.\n
        :return: None."""
        if not isinstance(cfdi, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi, dict_type=transp_cfdis):
            self._type_error(err=err, source=cfdi_parent)

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

        if cfdi_val is None:
            self._nonfound_key_error(key="Cfdi", source=cfdi_parent)
        if cfdi_type is None:
            self._nonfound_key_error(key="TipoCfdi", source=cfdi_parent)
        if consideration is None:
            self._nonfound_key_error(key="Contraprestacion", source=cfdi_parent)
        if transp_fee is None:
            self._nonfound_key_error(key="TarifaDeTransporte", source=cfdi_parent)
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
        if self._invalid_range(value=consideration, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="Contraprestacion", value=consideration, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.Contraprestacion"
            )
        if self._invalid_range(value=transp_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="TarifaDeTransporte", value=transp_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.TarifaDeTransporte"
            )
        if self._invalid_range(value=trans_cap_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorCapacidadDeTrans", value=trans_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoPorCapacidadDeTrans"
            )
        if self._invalid_range(value=trans_use_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=trans_use_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoPorUsoTrans"
            )
        if self._invalid_range(value=trans_vol_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=trans_vol_fee, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.CargoVolumetricoTrans"
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
