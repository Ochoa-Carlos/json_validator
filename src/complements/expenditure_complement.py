"""This module validate Expendio Complement Element."""
from typing import Any, Optional

from src.complements.complement_base import ComplementBuilder
from src.complements.constants import (ADUANAL_PEDIMENTO, CFDI_STRICT_REGEX,
                                       CLIENT_NAME_REGEX,
                                       IMPORT_EXPORT_PERMISSION_REGEX,
                                       INTERN_SPOT_REGEX,
                                       PERMISSION_ALM_DIST_REGEX,
                                       PERMISSION_PROOVE_CLIENT_EXO_REGEX,
                                       RFC_REGEX, TRANSPORT_PERM_EXO_REGEX,
                                       UTC_FORMAT_REGEX)
from src.complements.enumerators import (AduanaEntrance, CfdiType, CountryCode,
                                         IncotermCode)
from src.custom_exceptions import ClaveError, ValorError
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import (compl_foreign_pedimentos, complement_foreign,
                            complement_national, complement_transport,
                            exo_cfdis, exo_complement, exo_storage,
                            exo_terminal_alm_dist)


class ExpenditureComplement(ComplementBuilder):
    """Validation of expenditure complement type."""

    def validate_complemento(self) -> None:
        """Validate every Expendio complement declared in the report."""
        while self._next_complement():
            self._validate_complemento_tipado()
            self._validate_tipo_complemento()
            self._validate_terminal_alm_dist()
            self._validate_trasvase()
            self._validate_dictamen()
            self._validate_certificado()
            self._validate_nacional()
            self._validate_extranjero()
            self._validate_aclaracion()

            self._update_index()

    @exception_wrapper
    def _validate_complemento_tipado(self) -> None:
        """Validate value types declared at the Expendio complement root.\n
        :return: None."""
        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.current_complement,
                                                              dict_type=exo_complement):
            self._type_error(err=err)

    @exception_wrapper
    def _validate_terminal_alm_dist(self) -> None:
        """Validate TerminalAlmYDist object.\n
        :return: None."""
        if (alm_terminal := self.current_complement.get("TerminalAlmYDist")) is None:
            return
        if not isinstance(alm_terminal, dict):
            return

        terminal_parent = "TerminalAlmYDist"

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm_terminal,
                                                              dict_type=exo_terminal_alm_dist):
            self._type_error(err=err, source=terminal_parent)

        self.__validate_almacenamiento(
            alm=alm_terminal.get("Almacenamiento"), alm_parent=f"{terminal_parent}.Almacenamiento",
        )
        self.__validate_transporte(
            transp=alm_terminal.get("Transporte"), transp_parent=f"{terminal_parent}.Transporte",
        )

    @exception_wrapper
    def __validate_almacenamiento(self, alm: Optional[dict], alm_parent: str) -> None:
        """Validate TerminalAlmYDist Almacenamiento object.\n
        :param alm: Almacenamiento object declared in the complement.\n
        :param alm_parent: Object reference where the Almacenamiento object is placed.\n
        :return: None."""
        if alm is None or not isinstance(alm, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=alm, dict_type=exo_storage):
            self._type_error(err=err, source=alm_parent)

        alm_terminal = alm.get("TerminalAlmYDist")
        alm_permission = alm.get("PermisoAlmYDist")
        alm_fee = alm.get("TarifaDeAlmac")
        alm_cap_fee = alm.get("CargoPorCapacidadAlmac")
        alm_use_fee = alm.get("CargoPorUsoAlmac")
        alm_volum_fee = alm.get("CargoVolumetricoAlmac")

        if alm_terminal is None:
            self._nonfound_key_error(key="TerminalAlmYDist", source=alm_parent)
        if alm_permission is None:
            self._nonfound_key_error(key="PermisoAlmYDist", source=alm_parent)

        if self._invalid_length(value=alm_terminal, min_long=5, max_long=250):
            self._longitud_error(
                key="TerminalAlmYDist", value=alm_terminal, min_long=5, max_long=250,
                source=f"{alm_parent}.TerminalAlmYDist"
            )
        if self._invalid_pattern(value=alm_permission, pattern=PERMISSION_ALM_DIST_REGEX):
            self._regex_error(
                key="PermisoAlmYDist", value=alm_permission, pattern=PERMISSION_ALM_DIST_REGEX,
                source=f"{alm_parent}.PermisoAlmYDist"
            )
        if self._invalid_range(value=alm_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="TarifaDeAlmac", value=alm_fee, min_val=0, max_val=1000000000000,
                source=f"{alm_parent}.TarifaDeAlmac"
            )
        if self._invalid_range(value=alm_cap_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorCapacidadAlmac", value=alm_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{alm_parent}.CargoPorCapacidadAlmac"
            )
        if self._invalid_range(value=alm_use_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorUsoAlmac", value=alm_use_fee, min_val=0, max_val=1000000000000,
                source=f"{alm_parent}.CargoPorUsoAlmac"
            )
        if self._invalid_range(value=alm_volum_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoVolumetricoAlmac", value=alm_volum_fee, min_val=0, max_val=1000000000000,
                source=f"{alm_parent}.CargoVolumetricoAlmac"
            )

    @exception_wrapper
    def __validate_transporte(self, transp: Optional[dict], transp_parent: str) -> None:
        """Validate TerminalAlmYDist Transporte object.\n
        :param transp: Transporte object declared in the complement.\n
        :param transp_parent: Object reference where the Transporte object is placed.\n
        :return: None."""
        if transp is None or not isinstance(transp, dict):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=transp,
                                                              dict_type=complement_transport):
            self._type_error(err=err, source=transp_parent)

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

        if self._invalid_pattern(value=perm_transp, pattern=TRANSPORT_PERM_EXO_REGEX):
            self._regex_error(
                key="PermisoTransporte", value=perm_transp, pattern=TRANSPORT_PERM_EXO_REGEX,
                source=f"{transp_parent}.PermisoTransporte"
            )
        if self._invalid_length(value=vehicle_key, min_long=5, max_long=12):
            self._longitud_error(
                key="ClaveDeVehiculo", value=vehicle_key, min_long=5, max_long=12,
                source=f"{transp_parent}.ClaveDeVehiculo"
            )
        if self._invalid_range(value=transp_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="TarifaDeTransporte", value=transp_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.TarifaDeTransporte"
            )
        if self._invalid_range(value=transp_cap_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorCapacidadTrans", value=transp_cap_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorCapacidadTrans"
            )
        if self._invalid_range(value=transp_use_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoPorUsoTrans", value=transp_use_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoPorUsoTrans"
            )
        if self._invalid_range(value=transp_volume_fee, min_val=0, max_val=1000000000000):
            self._min_max_value_error(
                key="CargoVolumetricoTrans", value=transp_volume_fee, min_val=0, max_val=1000000000000,
                source=f"{transp_parent}.CargoVolumetricoTrans"
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
            deliv_permission = national_item.get("PermisoProveedor")
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
            if self._invalid_pattern(value=deliv_permission, pattern=PERMISSION_PROOVE_CLIENT_EXO_REGEX):
                self._regex_error(
                    key="PermisoProveedor", value=deliv_permission,
                    pattern=PERMISSION_PROOVE_CLIENT_EXO_REGEX,
                    source=f"{national_parent}.PermisoProveedor"
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

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=cfdi, dict_type=exo_cfdis):
            self._type_error(err=err, source=cfdi_parent)

        cfdi_val = cfdi.get("Cfdi")
        cfdi_type = cfdi.get("TipoCfdi")
        purch_price = cfdi.get("PrecioCompra")
        public_sale_price = cfdi.get("PrecioDeVentaAlPublico")
        sale_price = cfdi.get("PrecioVenta")
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
        if self._invalid_pattern(value=transaction_date, pattern=UTC_FORMAT_REGEX):
            self._regex_error(
                key="FechaYHoraTransaccion", value=transaction_date, pattern=UTC_FORMAT_REGEX,
                source=f"{cfdi_parent}.FechaYHoraTransaccion"
            )

        self.__validate_cfdi_prices(
            cfdi_type=cfdi_type, purch_price=purch_price, public_sale_price=public_sale_price,
            sale_price=sale_price, cfdi_parent=cfdi_parent,
        )

        self._validate_volumen_documentado(
            documented_volume=documented_volum, volume_parent=f"{cfdi_parent}.VolumenDocumentado",
        )

    @exception_wrapper
    def __validate_cfdi_prices(
            self,
            cfdi_type: Any,
            purch_price: Any,
            public_sale_price: Any,
            sale_price: Any,
            cfdi_parent: str,
        ) -> None:
        """Validate the three conditional price elements of an Expendio CFDI.\n
        :param cfdi_type: TipoCfdi value that drives which prices are expected.\n
        :param purch_price: PrecioCompra, expected on Egreso and Ingreso.\n
        :param public_sale_price: PrecioDeVentaAlPublico, expected on Ingreso.\n
        :param sale_price: PrecioVenta, expected on Ingreso.\n
        :param cfdi_parent: Object reference where the CFDIs object is placed.\n
        :return: None."""
        conditional = {
            "PrecioCompra": (purch_price, ("Egreso", "Ingreso")),
            "PrecioDeVentaAlPublico": (public_sale_price, ("Ingreso",)),
            "PrecioVenta": (sale_price, ("Ingreso",)),
        }

        for key, (value, expected_types) in conditional.items():
            if value is None and cfdi_type in expected_types:
                self.catch_error(
                    err_type=ClaveError,
                    err_message=(f"Error: clave '{key}' es condicional cuando 'TipoCfdi' es "
                                 f"{' o '.join(expected_types)}."),
                    source=cfdi_parent
                )
            if self._invalid_range(value=value, min_val=0, max_val=1000000000000):
                self._min_max_value_error(
                    key=key, value=value, min_val=0, max_val=1000000000000,
                    source=f"{cfdi_parent}.{key}"
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
            fore_parent = f"Extranjero[{foreign_index}]"

            if not isinstance(foreign_item, dict):
                self._value_error(key="Extranjero", value=foreign_item, source=fore_parent)
                continue

            if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=foreign_item,
                                                                  dict_type=complement_foreign):
                self._type_error(err=err, source=fore_parent)

            import_permission = foreign_item.get("PermisoImportacion")
            pedimentos = foreign_item.get("Pedimentos")

            if self._invalid_pattern(value=import_permission, pattern=IMPORT_EXPORT_PERMISSION_REGEX):
                self._regex_error(
                    key="PermisoImportacion", value=import_permission,
                    pattern=IMPORT_EXPORT_PERMISSION_REGEX,
                    source=f"{fore_parent}.PermisoImportacion"
                )

            if pedimentos and isinstance(pedimentos, list):
                for pedimento_index, pedimento in enumerate(pedimentos):
                    self.__validate_pedimentos(
                        pedimento=pedimento,
                        pedi_parent=f"{fore_parent}.Pedimentos[{pedimento_index}]",
                    )

    @exception_wrapper
    def __validate_pedimentos(self, pedimento: Any, pedi_parent: str) -> None:
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
