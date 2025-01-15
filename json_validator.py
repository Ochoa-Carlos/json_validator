import re

from constants import (MODALITY_PERMISSION_REGEX, RFC_CONTR_REGEX,
                       UTC_FORMAT_REGEX, VERSION_REGEX, caracteres)
from custom_exceptions import (CaracterAsignatarioError,
                               CaracterContratistaError,
                               CaracterPermisionarioError,
                               CaracterUsuarioError, LongitudError, RegexError,
                               ValorMinMaxError)
from decorators import wrapper_handler
from enumerators import CaracterTypeEnum
from json_model import JsonRoot
from monthly_log import MonthlyLogValidator
from product_validator import ProductValidator


class JsonValidator():
    """Validates JSON strucutre according bound cases"""
    def __init__(self, json_report: dict) -> None:
        self.json_report = json_report
        self.json_model = JsonRoot
        self.errors = []
        self.error = {}
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
            self.errors.append(e)

    def validate_json(self) -> None:
        """Return True or False if JSON are validated according type and bound."""
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

    @wrapper_handler
    def _validate_version(self) -> bool:
        version = self.json_report.get("Version")
        if re.match(VERSION_REGEX, version):
            return True
        else:
            raise RegexError(f"Error: La version {version} no cumple con el patron {VERSION_REGEX}")

# TODO revisar mas detenidamente los casos para el regex de RFC contribuyente
# TODO valiar y averiguar la diferencia entre el rfc de persona moral y contribuyente
    @wrapper_handler
    def _validate_rfc_contribuyente(self) -> None:
        rfc = self.json_report.get("RfcContribuyente")

        if not re.match(RFC_CONTR_REGEX, rfc):
            raise RegexError(f"Error: RfcContribuyente {rfc} no cumple con el patron {RFC_CONTR_REGEX}")
        if not 12 <= len(rfc) <= 13:
            raise LongitudError("Error: 'RfcContribuyente' no cumple con la longitud min 12 o max 13.")

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
                raise CaracterPermisionarioError(
                    f"Error: El caracter '{caracter}' no cumple con el patron {MODALITY_PERMISSION_REGEX}"
                    )
            if not 14 <= len(num_permission) <= 24:
                raise LongitudError(
                    "Error: 'NumPermiso' no cumple con la longitud min 14 o max 24."
                )
            if keys_prescence:
                raise CaracterPermisionarioError(
                    f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                    )

        if caracter == CaracterTypeEnum.CONTRATISTA.value and keys_prescence:
            num_contract = self.json_report.get("NumContratoOAsignacion")

            if not 14 <= len(num_contract) <= 24:
                raise LongitudError(
                    "Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                )
            if keys_prescence:
                raise CaracterContratistaError(
                    f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                )

        if caracter == CaracterTypeEnum.ASIGNATARIO.value and keys_prescence:
            num_asignation = self.json_report.get("NumContratoOAsignacion")

            if not 14 <= len(num_asignation) <= 24:
                raise LongitudError(
                    "Error: 'NumContratoOAsignacion' no cumple con la longitud min 14 o max 24."
                )
            if keys_prescence:
                raise CaracterAsignatarioError(
                    f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                )

        if caracter == CaracterTypeEnum.USUARIO.value and keys_prescence:
            alm_gas = self.json_report.get("InstalacionAlmacenGasNatural")

            if not 16 <= len(alm_gas) <= 250:
                raise LongitudError(
                    "Error: 'InstalacionAlmacenGasNatural' no cumple con la longitud min 14 o max 24."
                )
            if keys_prescence:
                raise CaracterUsuarioError(
                    f"Error: El caracter '{caracter}' no puede tener las claves {useless_caracter_keys} en el JSON."
                )

    @wrapper_handler
    def _validate_clave_instalacion(self) -> None:
        clave_instalacion = self.json_report.get("ClaveInstalacion")

        if not 8 <= len(clave_instalacion) <= 30:
            raise LongitudError(
                "Error: 'ClaveInstalacion' no cumple con la longitud min 8 o max 30."
            )

    @wrapper_handler
    def _validate_descripcion_instalacion(self) -> None:
        desc_instllation = self.json_report.get("DescripcionInstalacion")

        if not 5 <= len(desc_instllation) <= 250:
            raise LongitudError(
                "Error: 'DescripcionInstalacion' no cumple con la longitud min 5 o max 250."
            )

    @wrapper_handler
    def _validate_geolocalizacion(self) -> None:
        geolocalizacion = self.json_report.get("Geolocalizacion")[0]
        geo_lat = geolocalizacion.get("GeolocalizacionLatitud")
        geo_lon = geolocalizacion.get("GeolocalizacionLongitud")

        if abs(geo_lat) > 90:
            raise ValorMinMaxError("Error: 'GeolocalizacionLatitud' no está en el rango min -90 o max 90.")
        if abs(geo_lon) > 180:
            raise ValorMinMaxError("Error: 'GeolocalizacionLongitud' no está en el rango min -180 o max 180.")


    @wrapper_handler
    def _validate_numero_pozos(self) -> None:
        if "NumeroPozos" not in self.json_report:
            raise KeyError(
                "Error: 'NumeroPozos' no fue encontrada."
                )

    @wrapper_handler
    def _validate_numero_tanques(self) -> None:
        if "NumeroTanques" not in self.json_report:
            raise KeyError(
                "Error: 'NumeroTanques' no fue encontrada."
                )

    @wrapper_handler
    def _validate_ductos_io(self) -> None:
        if "NumeroDuctosEntradaSalida" not in self.json_report:
            raise KeyError(
                "Error: 'NumeroDuctosEntradaSalida' no fue encontrada."
                )

    @wrapper_handler
    def _validate_ductos_distribucion(self) -> None:
        if "NumeroDuctosTransporteDistribucion" not in self.json_report:
            raise KeyError(
                "Error: 'NumeroDuctosTransporteDistribucion' no fue encontrada."
                )

    @wrapper_handler
    def _validate_num_dispensarios(self) -> None:
        if "NumeroDispensarios" not in self.json_report:
            raise KeyError(
                "Error: 'NumeroDispensarios' no fue encontrada."
                )

    # TODO adaptar para el JSON Diario
    @wrapper_handler
    def _validate_report_date(self) -> None:
        date = self.json_report.get("FechaYHoraReporteMes")

        if not re.match(UTC_FORMAT_REGEX, date):
            raise TypeError(
                "Error: 'FechaYHoraReporteMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
            )

    @wrapper_handler
    def _validate_rfc_proveedores(self) -> None:
        if rfc := self.json_report.get("RfcProveedores"):
            if len(rfc) < 12:
                raise LongitudError(
                    "Error: 'RfcProveedores' no cumple con la longitud min 1."
                    )

    @wrapper_handler
    def _validate_products(self) -> None:
        products = self.json_report.get("Producto")
        caracter = self.json_report.get("Caracter")
        product_obj = ProductValidator(products=products, caracter=caracter)
        product_obj.validate_products()

    @wrapper_handler
    def _validate_monthly_log(self) -> None:
        if (month_log := self.json_report.get("BitacoraMensual")) is None:
            return
        log_obj = MonthlyLogValidator(month_log=month_log)
        log_obj.validate_log()
