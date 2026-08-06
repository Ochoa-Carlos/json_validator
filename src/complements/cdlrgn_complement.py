"""This module validate CDLRGN Complement Element."""
import re
from typing import Optional

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_STRICT_REGEX,
                                       CLIENT_NAME_REGEX,
                                       IMPORT_EXPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX,
                                       PERMISSION_ALM_CDLRGN_REGEX, RFC_REGEX,
                                       TRANSP_PERM_CDLRGN_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import ValorError
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (cdlrgn_cfdis, cdlrgn_complement, cdlrgn_foreign,
                            cdlrgn_foreign_pedimentos, cdlrgn_storage,
                            cdlrgn_terminal_alm_trans, cdlrgn_transport,
                            national_client)


class CDLRGNComplement(ComplementBuilder):
    """Complement for CDLRGN type."""

    def validate_complemento(self) -> None:
        """Validate every CDLRGN complement declared in the report."""
        if self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_trans()
            self._validate_trasvase()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_extranjero()
            self._validate_aclaracion()

            self._update_index()
            self.validate_complemento()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        """Validate value types declared at the CDLRGN complement root.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement,
                                                               dict_type=cdlrgn_complement):
            self._type_error(err=err)

    @exception_wrapper
    def _validate_terminal_alm_trans(self) -> None:
        """Validate TerminalAlmYTrans object.\n
        :return: None."""
        if (alm_trans_terminal := self.current_complement.get("TerminalAlmYTrans")) is None:
            return

        terminal_parent = "TerminalAlmYTrans"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm_trans_terminal,
                                                               dict_type=cdlrgn_terminal_alm_trans):
            self._type_error(err=err, source=terminal_parent)
            return

        self.__validate_almacenamiento(
            alm=alm_trans_terminal.get("Almacenamiento"), alm_parent=f"{terminal_parent}.Almacenamiento",
        )
        self.__validate_transporte(
            transp=alm_trans_terminal.get("Transporte"), transp_parent=f"{terminal_parent}.Transporte",
        )

    @exception_wrapper
    def __validate_almacenamiento(self, alm: Optional[dict], alm_parent: str) -> None:
        """Validate TerminalAlmYTrans Almacenamiento object.\n
        :param alm: Almacenamiento object declared in the complement.\n
        :param alm_parent: Object reference where the Almacenamiento object is placed.\n
        :return: None."""
        if alm is None:
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm, dict_type=cdlrgn_storage):
            self._type_error(err=err, source=alm_parent)
            return

        alm_terminal = alm.get("TerminalAlm")
        alm_permission = alm.get("PermisoAlmacenamiento")

        if alm_terminal is None:
            self._nonfound_key_error(key="TerminalAlm", source=alm_parent)
        if alm_permission is None:
            self._nonfound_key_error(key="PermisoAlmacenamiento", source=alm_parent)

        if alm_terminal and not 5 <= len(alm_terminal) <= 250:
            self._longitud_error(
                key="TerminalAlm", value=alm_terminal, min_long=5, max_long=250,
                source=f"{alm_parent}.TerminalAlm"
            )
        if alm_permission and not re.match(PERMISSION_ALM_CDLRGN_REGEX, alm_permission):
            self._regex_error(
                key="PermisoAlmacenamiento", value=alm_permission, pattern=PERMISSION_ALM_CDLRGN_REGEX,
                source=f"{alm_parent}.PermisoAlmacenamiento"
            )

    @exception_wrapper
    def __validate_transporte(self, transp: Optional[dict], transp_parent: str) -> None:
        """Validate TerminalAlmYTrans Transporte object.\n
        :param transp: Transporte object declared in the complement.\n
        :param transp_parent: Object reference where the Transporte object is placed.\n
        :return: None."""
        if transp is None:
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transp, dict_type=cdlrgn_transport):
            self._type_error(err=err, source=transp_parent)
            return

        perm_transp = transp.get("PermisoTransporte")
        vehicle_key = transp.get("ClaveDeVehiculo")

        if perm_transp is None:
            self._nonfound_key_error(key="PermisoTransporte", source=transp_parent)

        if perm_transp and not re.match(TRANSP_PERM_CDLRGN_REGEX, perm_transp):
            self._regex_error(
                key="PermisoTransporte", value=perm_transp, pattern=TRANSP_PERM_CDLRGN_REGEX,
                source=f"{transp_parent}.PermisoTransporte"
            )
        if vehicle_key and not 5 <= len(vehicle_key) <= 12:
            self._longitud_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_long=5, max_long=12,
                source=f"{transp_parent}.ClaveDeVehiculo"
            )

    @exception_wrapper
    def _validate_nacional(self) -> None:
        """Validate Nacional objs list.\n
        :return: None."""
        if (national := self.current_complement.get("Nacional")) is None:
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

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=national_item,
                                                                   dict_type=national_client):
                self._type_error(err=err, source=national_parent)
                continue

            client_rfc = national_item.get("RfcCliente")
            client_name = national_item.get("NombreCliente")
            cfdis = national_item.get("CFDIs")

            if client_rfc is None:
                self._nonfound_key_error(key="RfcCliente", source=national_parent)
            if client_name is None:
                self._nonfound_key_error(key="NombreCliente", source=national_parent)

            if client_rfc and not re.match(RFC_REGEX, client_rfc):
                self._regex_error(
                    key="RfcCliente", value=client_rfc, pattern=RFC_REGEX,
                    source=f"{national_parent}.RfcCliente"
                )
            if client_name and not 1 <= len(client_name) <= 150:
                self._longitud_error(
                    key="NombreCliente", value=client_name, min_long=1, max_long=150,
                    source=f"{national_parent}.NombreCliente"
                )
            if client_name and not re.match(CLIENT_NAME_REGEX, client_name):
                self._regex_error(
                    key="NombreCliente", value=client_name, pattern=CLIENT_NAME_REGEX,
                    source=f"{national_parent}.NombreCliente"
                )

            if cfdis:
                for cfdi_index, cfdi in enumerate(cfdis):
                    self.__validate_cfdi(cfdi=cfdi, cfdi_parent=f"{national_parent}.CFDIs[{cfdi_index}]")

    @exception_wrapper
    def __validate_cfdi(self, cfdi: dict, cfdi_parent: str) -> None:
        """Validate a Nacional CFDIs object.\n
        :param cfdi: CFDIs object declared in the Nacional element.\n
        :param cfdi_parent: Object reference where the CFDIs object is placed.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi, dict_type=cdlrgn_cfdis):
            self._type_error(err=err, source=cfdi_parent)
            return

        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        consideration = cfdi.get("Contraprestacion")
        transaction_date = cfdi.get("FechaYHoraTransaccion")
        documented_volum = cfdi.get("VolumenDocumentado")

        if cfdi_val is None:
            self._nonfound_key_error(key="Cfdi", source=cfdi_parent)
        if cfdi_type is None:
            self._nonfound_key_error(key="TipoCfdi", source=cfdi_parent)
        if consideration is None:
            self._nonfound_key_error(key="Contraprestacion", source=cfdi_parent)
        if transaction_date is None:
            self._nonfound_key_error(key="FechaYHoraTransaccion", source=cfdi_parent)
        if documented_volum is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=cfdi_parent)

        if cfdi_val and not re.match(CFDI_STRICT_REGEX, cfdi_val):
            self._regex_error(
                key="Cfdi", value=cfdi_val, pattern=CFDI_STRICT_REGEX,
                source=f"{cfdi_parent}.Cfdi"
            )
        if cfdi_type and cfdi_type not in [item.value for item in CfdiType]:
            self._value_error(
                key="TipoCfdi", value=cfdi_type,
                source=f"{cfdi_parent}.TipoCfdi"
            )
        if consideration and not 0 <= consideration <= 1000000000000:
            self._min_max_value_error(
                key="Contraprestacion", value=consideration, min_val=0, max_val=1000000000000,
                source=f"{cfdi_parent}.Contraprestacion"
            )
        if transaction_date and not re.match(UTC_FORMAT_REGEX, transaction_date):
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

        if not foreign:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: clave 'Extranjero' debe declarar al menos un elemento.",
                source="Extranjero"
            )
            return

        for foreign_index, foreign_item in enumerate(foreign):
            foreign_parent = f"Extranjero[{foreign_index}]"

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=foreign_item,
                                                                   dict_type=cdlrgn_foreign):
                self._type_error(err=err, source=foreign_parent)
                continue

            import_export_permission = foreign_item.get("PermisoImportacionOExportacion")
            pedimentos = foreign_item.get("Pedimentos")

            if import_export_permission and not re.match(IMPORT_EXPORT_PERMISSION_REGEX,
                                                         import_export_permission):
                self._regex_error(
                    key="PermisoImportacionOExportacion", value=import_export_permission,
                    pattern=IMPORT_EXPORT_PERMISSION_REGEX,
                    source=f"{foreign_parent}.PermisoImportacionOExportacion"
                )

            if pedimentos:
                for pedimento_index, pedimento in enumerate(pedimentos):
                    self.__validate_pedimentos(
                        pedimento=pedimento,
                        pedi_parent=f"{foreign_parent}.Pedimentos[{pedimento_index}]",
                    )

    @exception_wrapper
    def __validate_pedimentos(self, pedimento: dict, pedi_parent: str) -> None:
        """Validate an Extranjero Pedimentos object.\n
        :param pedimento: Pedimentos object declared in the Extranjero element.\n
        :param pedi_parent: Object reference where the Pedimentos object is placed.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=pedimento,
                                                               dict_type=cdlrgn_foreign_pedimentos):
            self._type_error(err=err, source=pedi_parent)
            return

        intern_extrac_point = pedimento.get("PuntoDeInternacionOExtraccion")
        origin_destiny_country = pedimento.get("PaisOrigenODestino")
        aduana_transp_med = pedimento.get("MedioDeTransEntraOSaleAduana")
        aduanal_pedimento = pedimento.get("PedimentoAduanal")
        incoterm = pedimento.get("Incoterms")
        import_price = pedimento.get("PrecioDeImportacion")
        documented_volume = pedimento.get("VolumenDocumentado")

        if intern_extrac_point is None:
            self._nonfound_key_error(key="PuntoDeInternacionOExtraccion", source=pedi_parent)
        if origin_destiny_country is None:
            self._nonfound_key_error(key="PaisOrigenODestino", source=pedi_parent)
        if aduana_transp_med is None:
            self._nonfound_key_error(key="MedioDeTransEntraOSaleAduana", source=pedi_parent)
        if aduanal_pedimento is None:
            self._nonfound_key_error(key="PedimentoAduanal", source=pedi_parent)
        if incoterm is None:
            self._nonfound_key_error(key="Incoterms", source=pedi_parent)
        if import_price is None:
            self._nonfound_key_error(key="PrecioDeImportacion", source=pedi_parent)
        if documented_volume is None:
            self._nonfound_key_error(key="VolumenDocumentado", source=pedi_parent)

        if intern_extrac_point and not re.match(INTERN_SPOT_REGEX, intern_extrac_point):
            self._regex_error(
                key="PuntoDeInternacionOExtraccion", value=intern_extrac_point, pattern=INTERN_SPOT_REGEX,
                source=f"{pedi_parent}.PuntoDeInternacionOExtraccion"
            )
        if origin_destiny_country and origin_destiny_country not in [item.value for item in CountryCode]:
            self._value_error(
                key="PaisOrigenODestino", value=origin_destiny_country,
                source=f"{pedi_parent}.PaisOrigenODestino"
            )
        if aduana_transp_med and aduana_transp_med not in [item.value for item in AduanaEntrance]:
            self._value_error(
                key="MedioDeTransEntraOSaleAduana", value=aduana_transp_med,
                source=f"{pedi_parent}.MedioDeTransEntraOSaleAduana"
            )
        if aduanal_pedimento and not re.match(ADUANAL_PEDIMENTO, aduanal_pedimento):
            self._regex_error(
                key="PedimentoAduanal", value=aduanal_pedimento, pattern=ADUANAL_PEDIMENTO,
                source=f"{pedi_parent}.PedimentoAduanal"
            )
        if incoterm and incoterm not in [item.value for item in IncotermCode]:
            self._value_error(
                key="Incoterms", value=incoterm,
                source=f"{pedi_parent}.Incoterms"
            )
        if import_price and not 0 <= import_price <= 1000000000000:
            self._min_max_value_error(
                key="PrecioDeImportacion", value=import_price, min_val=0, max_val=1000000000000,
                source=f"{pedi_parent}.PrecioDeImportacion"
            )

        self._validate_volumen_documentado(
            documented_volume=documented_volume, volume_parent=f"{pedi_parent}.VolumenDocumentado",
        )
