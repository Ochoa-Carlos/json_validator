"""Json validation orchestrator."""
import re
import traceback

from src.constants import (FILE_NAME_REGEX, MODALITY_PERMISSION_REGEX,
                           RFC_CONTR_REGEX, RFC_PERSONA_FISICA,
                           UTC_FORMAT_REGEX, VERSION_REGEX, caracteres,
                           monthly_json_schema)
from src.custom_exceptions import (CaracterAsignatarioError,
                                   CaracterContratistaError,
                                   CaracterPermisionarioError,
                                   CaracterUsuarioError, ClaveError,
                                   LongitudError, RegexError, TipadoError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper, wrapper_handler
from src.enumerators import CaracterTypeEnum, PermisoEnum
from src.json_model import JsonRoot
from src.monthly_log import MonthlyLogValidator
from src.product_validator import ProductValidator
from src.utils.logger import logger

logging = logger()


class JsonValidator():
    """Validates JSON strucutre according bound cases"""
    def __init__(self, json_report: dict) -> None:
        self.json_report = json_report
        self.json_model = JsonRoot
        self.error = []
        self.errors = {}
        self._errors = []
        self.executed_functions = set()


    def set_json(self) -> None:
        """Make a copy of json and set copy structure according data."""
        try:
            json_copy = self.json_report.copy()
            self.json_model.set_caracter_structure(caracter=self.json_report.get("Caracter"))

            if rfc_proveedores := self.json_report.get("RfcProveedores", None):
                self.json_model.set_rfc_proveedores(rfc=rfc_proveedores)
                json_copy.pop("RfcProveedores", None)

            if geo_dict := self.json_report.get("Geolocalizacion", None):
                self.json_model.set_geolocalization(geo_dict=geo_dict)
                json_copy.pop("Geolocalizacion", None)

            self.json_model.set_json(json_data=self.json_report)
        except Exception as e:
            self.error.append(e)

# TODO Validar JSON diario
    def validate_json(self) -> None:
        """Return True or False if JSON are validated according type and bound."""
        try:
            logging.info(f"{'':*^20} Validando Json {'':*^20}")
            self._validate_json_schema()
            self._validate_version()
            self._validate_rfc_contribuyente()
            self._validate_rfc_representante_legal()
            self._validate_info_according_caracter()
            self._validate_clave_instalacion()
            self._validate_descripcion_instalacion()
            self._validate_geolocalizacion()
            self._validate_numero_pozos()
            self._validate_numero_tanques()
            self._validate_ductos_io()
            self._validate_ductos_distribucion()
            self._validate_num_dispensarios()
            self._validate_report_date()
            self._validate_rfc_proveedores()
            self._validate_products()
            self._validate_monthly_log()
        except Exception as exc:
            self.catch_error(err_type=SystemError, err_message=f"Error al validar JSON {exc}")
            logging.warning(f"Error al validar JSON: {exc}")
            logging.warning(f": {traceback.format_exc()}")

    @exception_wrapper
    def _validate_json_schema(self) -> bool:
        for key in self.json_report.keys():
            if key not in monthly_json_schema:
                print("entro")
                self.catch_error(
                    err_type=ValorError,
                    err_message=f"Error: elemento '{key}' no definido en esquema.",
                )

    # @wrapper_handler
    @exception_wrapper
    def _validate_version(self) -> bool:
        if (version := self.json_report.get("Version")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Version' no fue encontrada."
                )
            return
        if not re.match(VERSION_REGEX, version):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: La version {version} no cumple con el patron {VERSION_REGEX}"
                )

    @wrapper_handler
    def _validate_rfc_contribuyente(self) -> None:
        if (rfc_cont := self.json_report.get("RfcContribuyente")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'RfcContribuyente' no fue encontrada."
                )
            return

        if not re.match(RFC_CONTR_REGEX, rfc_cont):
            self.catch_error(
                err_type=RegexError,
                err_message=f"Error: RfcContribuyente {rfc_cont} no cumple con el patron {RFC_CONTR_REGEX}"
                )
        if not 12 <= len(rfc_cont) <= 13:
            self.catch_error(
                err_type=LongitudError,
                err_message="Error: 'RfcContribuyente' no cumple con la longitud min 12 o max 13."
                )

    @wrapper_handler
    def _validate_rfc_representante_legal(self) -> None:
        """Rfc Representante loca"""
        if len(self.json_report.get("RfcContribuyente")) == 12:
            rfc_rep_leg = self.json_report.get("RfcRepresentanteLegal")

            if rfc_rep_leg is None:
                self.catch_error(
                    err_type=ClaveError,
                    err_message="Error: clave 'RfcRepresentanteLegal' es requerida en caso que el elemento 'RfcContribuyente' se manifieste de una persona moral (12 caracteres)"
                    )
                return
            if not re.match(RFC_PERSONA_FISICA, rfc_rep_leg):
                self.catch_error(
                    err_type=RegexError,
                    err_message=f"Error: clave 'RfcRepresentanteLegal' {rfc_rep_leg} no cumple con el patron {RFC_PERSONA_FISICA}"
                    )
            if len(rfc_rep_leg) != 13:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: clave 'RfcRepresentanteLegal' no cumple con la longitud min 13 o max 13."
                    )

    @wrapper_handler
    def _validate_info_according_caracter(self) -> bool:
        """Validate caracter info."""
        if (caracter := self.json_report.get("Caracter")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Caracter' no fue encontrada."
            )
            return

        useless_caracter_keys = {key: val for key, val in caracteres.items() if key != caracter}
        useless_caracter_keys = list({key for key in useless_caracter_keys.values() for key in key})
        keys_prescence: bool = any(key in self.json_report for key in useless_caracter_keys)

        if caracter == CaracterTypeEnum.PERMISIONARIO.value:
            mod_permission = self.json_report.get("ModalidadPermiso")
            num_permission = self.json_report.get("NumPermiso")
            perm_pattern = PermisoEnum[mod_permission].value
            pattern_parts = perm_pattern.split("/")
            perm_parts = num_permission.split("/")

            if mod_permission and not re.match(MODALITY_PERMISSION_REGEX, mod_permission):
                self.catch_error(
                    err_type=CaracterPermisionarioError,
                    err_message=f"Error: ModalidadPermiso '{mod_permission}' no cumple con el patron {MODALITY_PERMISSION_REGEX}"
                    )
            if num_permission and not 14 <= len(num_permission) <= 24:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: 'NumPermiso' no cumple con la longitud min 14 o max 24."
                    )
            if keys_prescence:
                self.catch_error(
                    err_type=CaracterPermisionarioError,
                    err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                    )

            if len(pattern_parts) != len(perm_parts):
                self.catch_error(
                    err_type=CaracterPermisionarioError,
                    err_message=f"Error: el NumPermiso {num_permission} no coincide con el patrón {perm_pattern}."
                    )
            for patt, perm in zip(pattern_parts, perm_parts):
                err = None
                if patt == "XXXXX":
                    if not (perm.isdigit() and len(perm) == 5):
                        err = True
                elif patt == "AAAA":
                    if not (perm.isdigit() and len(perm) == 4):
                        err = True
                elif patt != perm:
                    err = True
                if err:
                    self.catch_error(
                        err_type=CaracterPermisionarioError,
                        err_message=f"Error: el NumPermiso {num_permission} no coincide con el patrón {perm_pattern}."
                        )

        if caracter == CaracterTypeEnum.CONTRATISTA.value and keys_prescence:
            num_contract = self.json_report.get("NumContratoOAsignacion")

            if num_contract and not 14 <= len(num_contract) <= 24:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                    )
            if keys_prescence:
                self.catch_error(
                    err_type=CaracterContratistaError,
                    err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                    )

        if caracter == CaracterTypeEnum.ASIGNATARIO.value and keys_prescence:
            num_asignation = self.json_report.get("NumContratoOAsignacion")

            if num_asignation and not 14 <= len(num_asignation) <= 24:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                    )
            if keys_prescence:
                self.catch_error(
                    err_type=CaracterAsignatarioError,
                    err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                    )

        if caracter == CaracterTypeEnum.USUARIO.value and keys_prescence:
            alm_gas = self.json_report.get("InstalacionAlmacenGasNatural")

            if not 16 <= len(alm_gas) <= 250:
                self.catch_error(
                    err_type=LongitudError,
                    err_message="Error: 'InstalacionAlmacenGasNatural' no cumple con la longitud min 14 o max 24."
                    )
            if keys_prescence:
                self.catch_error(
                    err_type=CaracterUsuarioError,
                    err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                    )

    @wrapper_handler
    def _validate_clave_instalacion(self) -> None:
        if (clave_instalacion := self.json_report.get("ClaveInstalacion")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'ClaveInstalacion' no fue encontrada."
                )
            return

        if not 8 <= len(clave_instalacion) <= 30:
            self.catch_error(
                err_type=LongitudError,
                err_message="Error: 'ClaveInstalacion' no cumple con la longitud min 8 o max 30."
                )

    @wrapper_handler
    def _validate_descripcion_instalacion(self) -> None:
        if (desc_instllation := self.json_report.get("DescripcionInstalacion")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'DescripcionInstalacion' no no fue encontrada."
                )
            return

        if not 5 <= len(desc_instllation) <= 250:
            self.catch_error(
                err_type=LongitudError,
                err_message="Error: 'DescripcionInstalacion' no cumple con la longitud min 5 o max 250."
                )

    @wrapper_handler
    def _validate_geolocalizacion(self) -> None:
        if (geolocalizacion := self.json_report.get("Geolocalizacion")) is None:
            return

        geo_lat = geolocalizacion[0].get("GeolocalizacionLatitud")
        geo_lon = geolocalizacion[0].get("GeolocalizacionLongitud")

        if geo_lat and abs(geo_lat) > 90:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message="Error: 'GeolocalizacionLatitud' no está en el rango min -90 o max 90."
                )
        if geo_lon and abs(geo_lon) > 180:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message="Error: 'GeolocalizacionLongitud' no está en el rango min -180 o max 180."
                )


    @wrapper_handler
    def _validate_numero_pozos(self) -> None:
        if "NumeroPozos" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: clave 'NumeroPozos' no fue encontrada.")
            return
        if not isinstance(self.json_report.get("NumeroPozos"), int) or self.json_report.get("NumeroPozos") < 0:
            self.catch_error(err_type=ValorError, err_message="Error: valor 'NumeroPozos' no válido.")


    @wrapper_handler
    def _validate_numero_tanques(self) -> None:
        if "NumeroTanques" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: clave 'NumeroTanques' no fue encontrada.")
            return
        if not isinstance(self.json_report.get("NumeroTanques"), int) or self.json_report.get("NumeroTanques") < 0:
            self.catch_error(err_type=ValorError, err_message="Error: valor 'NumeroTanques' no válido.")

    @wrapper_handler
    def _validate_ductos_io(self) -> None:
        if "NumeroDuctosEntradaSalida" not in self.json_report:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'NumeroDuctosEntradaSalida' no fue encontrada."
                )
            return
        if not isinstance(
            self.json_report.get("NumeroDuctosEntradaSalida"),
            int) or self.json_report.get("NumeroDuctosEntradaSalida") < 0:
            self.catch_error(err_type=ValorError, err_message="Error: valor 'NumeroDuctosEntradaSalida' no válido.")

    @wrapper_handler
    def _validate_ductos_distribucion(self) -> None:
        if "NumeroDuctosTransporteDistribucion" not in self.json_report:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'NumeroDuctosTransporteDistribucion' no fue encontrada."
                )
            return
        if not isinstance(self.json_report.get("NumeroDuctosTransporteDistribucion"),
                          int) or self.json_report.get("NumeroDuctosTransporteDistribucion") < 0:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: valor 'NumeroDuctosTransporteDistribucion' no válido."
                )

    @wrapper_handler
    def _validate_num_dispensarios(self) -> None:
        if "NumeroDispensarios" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroDispensarios' no fue encontrada.")
            return
        if not isinstance(self.json_report.get("NumeroDispensarios"),
                          int) or self.json_report.get("NumeroDispensarios") < 0:
            self.catch_error(err_type=ValorError, err_message="Error: valor 'NumeroDispensarios' no válido.")

    @wrapper_handler
    def _validate_report_date(self) -> None:
        if (date := self.json_report.get("FechaYHoraReporteMes")) is None:
            self.catch_error(
                err_type=TipadoError,
                err_message="Error: clave 'FechaYHoraReporteMes' no fue encontrada."
                )
            return

        if not re.match(UTC_FORMAT_REGEX, date):
            self.catch_error(
                err_type=TipadoError,
                err_message="Error: 'FechaYHoraReporteMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
                )

    @wrapper_handler
    def _validate_rfc_proveedores(self) -> None:
        if (rfc := self.json_report.get("RfcProveedor")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'RfcProveedor' no fue encontrada."
                )
            return

        if len(rfc) < 12:
            self.catch_error(
                err_type=LongitudError,
                err_message="Error: clave 'RfcProveedor' no cumple con la longitud min 12 o max 13."
                )

    # @wrapper_handler
    def _validate_products(self) -> None:
        if products := self.json_report.get("Producto"):
            caracter = self.json_report.get("Caracter")

            product_obj = ProductValidator(products=products, caracter=caracter)
            product_obj.validate_products()

            if product_errors := product_obj.errors:
                self._errors.extend(product_errors)
                # self.errors = self.errors | product_errors
                # self._errors = self.errors | product_errors
        else:
            self.catch_error(err_type=ClaveError, err_message="Error: clave 'Producto' no encontrada.")

    # @wrapper_handler
    def _validate_monthly_log(self) -> None:
        if (month_log := self.json_report.get("BitacoraMensual")) is None:
            self.catch_error(err_type=ClaveError, err_message="Error: clave 'Bitácora' no encontrada.")
            return
        log_obj = MonthlyLogValidator(month_log=month_log)
        log_obj.validate_log()

        if log_errors := log_obj.errors:
            self._errors.extend(log_errors)

    def validate_json_name(self, name: str) -> None:
        """Check for name."""
        if len(name.split("_")) != 8:
            self.catch_error(
                err_type=ValorError,
                err_message="Error: nombre de archivo no está compuesto por 'IdentificadorTipo_IdentificadorEnvio_RfcCV_RFCProveedor_Periodo_CveInstalacion_TipoReporte_TipoEstandar'."
                )
        if not re.match(FILE_NAME_REGEX, name.replace(".json", "")):
            self.catch_error(err_type=ValorError,
                             err_message="Error: nombre de archivo no válido."
                             )

    def catch_error(self, err_type: BaseException, err_message: str) -> dict:
        """Catch error from validations."""
        self._errors.append({"type_error": err_type.__name__,
                             "error": err_message})
        # self._errors[err_type.__name__] = err_message

    def get_errors(self) -> dict:
        """Return list of object errors."""
        return self._errors
