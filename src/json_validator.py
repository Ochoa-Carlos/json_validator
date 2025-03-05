import re
import traceback

from src.constants import (MODALITY_PERMISSION_REGEX, RFC_CONTR_REGEX,
                           UTC_FORMAT_REGEX, VERSION_REGEX, caracteres)
from src.custom_exceptions import (CaracterAsignatarioError,
                                   CaracterContratistaError,
                                   CaracterPermisionarioError,
                                   CaracterUsuarioError, ClaveError,
                                   LongitudError, RegexError, ValorMinMaxError)
from src.decorators import wrapper_handler
from src.enumerators import CaracterTypeEnum
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

# TODO descomentar montly_log y adecuar los errores
    def validate_json(self) -> None:
        """Return True or False if JSON are validated according type and bound."""
        try:
            print("==================================== VALIDATE JSON ====================================")
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
            print("=ERRORSOTE AQUI ALVASDASD")
        except Exception as exc:
            self.catch_error(err_type=SystemError, err_message=f"Error al validar JSON {exc}")
            logging.warning(f"Error al validar JSON: {exc}")
            logging.warning(f": {traceback.format_exc()}")

    @wrapper_handler
    def _validate_version(self) -> bool:
        version = self.json_report.get("Version")
        if re.match(VERSION_REGEX, version):
            return True
        else:
            self.catch_error(err_type=RegexError, err_message=f"Error: La version {version} no cumple con el patron {VERSION_REGEX}")
            # raise RegexError(f"Error: La version {version} no cumple con el patron {VERSION_REGEX}")

# TODO revisar mas detenidamente los casos para el regex de RFC contribuyente
# TODO valiar y averiguar la diferencia entre el rfc de persona moral y contribuyente
    @wrapper_handler
    def _validate_rfc_contribuyente(self) -> None:
        rfc = self.json_report.get("RfcContribuyente")

        if not re.match(RFC_CONTR_REGEX, rfc):
            self.catch_error(err_type=RegexError, err_message=f"Error: RfcContribuyente {rfc} no cumple con el patron {RFC_CONTR_REGEX}")
            # raise RegexError(f"Error: RfcContribuyente {rfc} no cumple con el patron {RFC_CONTR_REGEX}")
        if not 12 <= len(rfc) <= 13:
            self.catch_error(err_type=LongitudError, err_message="Error: 'RfcContribuyente' no cumple con la longitud min 12 o max 13.")
            # raise LongitudError("Error: 'RfcContribuyente' no cumple con la longitud min 12 o max 13.")

# TODO rfc representante legal
    @wrapper_handler
    def _validate_rfc_representante_legal(self) -> None:
        # rfc = self.json_report.get("RfcRepresentanteLegal")

        # if not re.match(RFC_CONTR_REGEX, rfc):
        #     raise RegexError(f"Error: RfcContribuyente {rfc} no cumple con el patron {RFC_CONTR_REGEX}")
        # if not 12 <= len(rfc) <= 13:
        #     raise LongitudError("Error: 'RfcContribuyente' no cumple con la longitud min 12 o max 13.")
        return

    @wrapper_handler
    def _validate_info_according_caracter(self) -> bool:
        caracter = self.json_report.get("Caracter")
        useless_caracter_keys = {key: val for key, val in caracteres.items() if key != caracter}
        useless_caracter_keys = list({key for key in useless_caracter_keys.values() for key in key})
        # TODO quitar cond key presence, ya existe la validacion al formar el json en json_model
        keys_prescence: bool = any(key in self.json_report for key in useless_caracter_keys)

        if caracter == CaracterTypeEnum.PERMISIONARIO.value:
            mod_permission = self.json_report.get("ModalidadPermiso")
            num_permission = self.json_report.get("NumPermiso")

            if not re.match(MODALITY_PERMISSION_REGEX, mod_permission):
                self.catch_error(err_type=CaracterPermisionarioError, err_message=f"Error: ModalidadPermiso '{mod_permission}' no cumple con el patron {MODALITY_PERMISSION_REGEX}")
                # raise CaracterPermisionarioError(
                #     f"Error: ModalidadPermiso '{mod_permission}' no cumple con el patron {MODALITY_PERMISSION_REGEX}"
                #     )
            if not 14 <= len(num_permission) <= 24:
                self.catch_error(err_type=LongitudError, err_message="Error: 'NumPermiso' no cumple con la longitud min 14 o max 24.")
                # raise LongitudError(
                #     "Error: 'NumPermiso' no cumple con la longitud min 14 o max 24."
                # )
            if keys_prescence:
                self.catch_error(err_type=CaracterPermisionarioError, err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON.")
                # raise CaracterPermisionarioError(
                #     f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                #     )

        if caracter == CaracterTypeEnum.CONTRATISTA.value and keys_prescence:
            num_contract = self.json_report.get("NumContratoOAsignacion")

            if not 14 <= len(num_contract) <= 24:
                self.catch_error(err_type=LongitudError, err_message="Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24.")
                # raise LongitudError(
                #     "Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                # )
            if keys_prescence:
                self.catch_error(err_type=CaracterContratistaError, err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON.")
                # raise CaracterContratistaError(
                #     f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                # )

        if caracter == CaracterTypeEnum.ASIGNATARIO.value and keys_prescence:
            num_asignation = self.json_report.get("NumContratoOAsignacion")

            if not 14 <= len(num_asignation) <= 24:
                self.catch_error(err_type=LongitudError, err_message="Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24.")
                # raise LongitudError(
                #     "Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                # )
            if keys_prescence:
                self.catch_error(err_type=CaracterAsignatarioError, err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON.")
                # raise CaracterAsignatarioError(
                #     f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                # )

        if caracter == CaracterTypeEnum.USUARIO.value and keys_prescence:
            alm_gas = self.json_report.get("InstalacionAlmacenGasNatural")

            if not 16 <= len(alm_gas) <= 250:
                self.catch_error(err_type=LongitudError, err_message="Error: 'InstalacionAlmacenGasNatural' no cumple con la longitud min 14 o max 24.")
                # raise LongitudError(
                #     "Error: 'InstalacionAlmacenGasNatural' no cumple con la longitud min 14 o max 24."
                # )
            if keys_prescence:
                self.catch_error(err_type=CaracterUsuarioError, err_message=f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON.")
                # raise CaracterUsuarioError(
                #     f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                # )

    @wrapper_handler
    def _validate_clave_instalacion(self) -> None:
        clave_instalacion = self.json_report.get("ClaveInstalacion")

        if not 8 <= len(clave_instalacion) <= 30:
            self.catch_error(err_type=LongitudError, err_message="Error: 'ClaveInstalacion' no cumple con la longitud min 8 o max 30.")
            # raise LongitudError(
            #     "Error: 'ClaveInstalacion' no cumple con la longitud min 8 o max 30."
            # )

    @wrapper_handler
    def _validate_descripcion_instalacion(self) -> None:
        desc_instllation = self.json_report.get("DescripcionInstalacion")

        if not 5 <= len(desc_instllation) <= 250:
            self.catch_error(err_type=LongitudError, err_message="Error: 'DescripcionInstalacion' no cumple con la longitud min 5 o max 250.")
            # raise LongitudError(
            #     "Error: 'DescripcionInstalacion' no cumple con la longitud min 5 o max 250."
            # )

    @wrapper_handler
    def _validate_geolocalizacion(self) -> None:
        if (geolocalizacion := self.json_report.get("Geolocalizacion")) is None:
            return

        geo_lat = geolocalizacion[0].get("GeolocalizacionLatitud")
        geo_lon = geolocalizacion[0].get("GeolocalizacionLongitud")

        if abs(geo_lat) > 90:
            self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'GeolocalizacionLatitud' no está en el rango min -90 o max 90.")
            # raise ValorMinMaxError("Error: 'GeolocalizacionLatitud' no está en el rango min -90 o max 90.")
        if abs(geo_lon) > 180:
            self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'GeolocalizacionLongitud' no está en el rango min -180 o max 180.")
            # raise ValorMinMaxError("Error: 'GeolocalizacionLongitud' no está en el rango min -180 o max 180.")


    @wrapper_handler
    def _validate_numero_pozos(self) -> None:
        if "NumeroPozos" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroPozos' no fue encontrada.")
            # raise KeyError(
            #     "Error: 'NumeroPozos' no fue encontrada."
            #     )

    @wrapper_handler
    def _validate_numero_tanques(self) -> None:
        if "NumeroTanques" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroTanques' no fue encontrada.")
            # raise KeyError(
            #     "Error: 'NumeroTanques' no fue encontrada."
            #     )

    @wrapper_handler
    def _validate_ductos_io(self) -> None:
        if "NumeroDuctosEntradaSalida" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroDuctosEntradaSalida' no fue encontrada.")
            # raise KeyError(
            #     "Error: 'NumeroDuctosEntradaSalida' no fue encontrada."
            #     )

    @wrapper_handler
    def _validate_ductos_distribucion(self) -> None:
        if "NumeroDuctosTransporteDistribucion" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroDuctosTransporteDistribucion' no fue encontrada.")
            # raise KeyError(
            #     "Error: 'NumeroDuctosTransporteDistribucion' no fue encontrada."
            #     )

    @wrapper_handler
    def _validate_num_dispensarios(self) -> None:
        if "NumeroDispensarios" not in self.json_report:
            self.catch_error(err_type=ClaveError, err_message="Error: 'NumeroDispensarios' no fue encontrada.")
            # raise KeyError(
            #     "Error: 'NumeroDispensarios' no fue encontrada."
            #     )

    # TODO adaptar para el JSON Diario
    @wrapper_handler
    def _validate_report_date(self) -> None:
        date = self.json_report.get("FechaYHoraReporteMes")

        if not re.match(UTC_FORMAT_REGEX, date):
            self.catch_error(err_type=TypeError, err_message="Error: 'FechaYHoraReporteMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'.")
            # raise TypeError(
            #     "Error: 'FechaYHoraReporteMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
            # )

    @wrapper_handler
    def _validate_rfc_proveedores(self) -> None:
        if rfc := self.json_report.get("RfcProveedores"):
            if len(rfc) < 12:
                self.catch_error(err_type=LongitudError, err_message="Error: 'RfcProveedores' no cumple con la longitud min 1.")
                # raise LongitudError(
                #     "Error: 'RfcProveedores' no cumple con la longitud min 1."
                #     )

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
            self.errors = self.errors | log_errors

    def catch_error(self, err_type: BaseException, err_message: str) -> dict:
        """Catch error from validations."""
        self._errors.append({"type_error": err_type.__name__,
                             "error": err_message})
        # self._errors[err_type.__name__] = err_message

    def get_errors(self) -> dict:
        return self._errors


# # HACER DISTINCION ENTRE LAS CLAVES Y VALORES
# # VALIDAR TIPOS
# # LO COMPLICADO SON LOS COMPLEMENTOS DEL MENSUAL
#         log_obj = MonthlyLogValidator(month_log=month_log)
#         log_obj.validate_log()

#         if log_errors := log_obj.errors:
#             self.errors = self.errors | log_errors

# HACER DISTINCION ENTRE LAS CLAVES Y VALORES
# VALIDAR TIPOS
# LO COMPLICADO SON LOS COMPLEMENTOS DEL MENSUAL