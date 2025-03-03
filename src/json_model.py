import re 
from constants import caracteres

class JsonRoot():
    """Json class for Month and Daily structure."""

    month_root = {
        "sVersion": "",
        "RfcContribuyente": "",
        "RfcRepresentanteLegal": "",
        "RfcProveedor": "",
        # "RfcProveedores": "",
        "Caracter": "",
        "ModalidadPermiso": "",
        "NumPermiso": "",
        "NumContratoOAsignacion": "",
        "InstalacionAlmacenGasNatural": "",
        "ClaveInstalacion": "",
        "DescripcionInstalacion": "",
        # "Geolocalizacion": "",
        "NumeroPozos": "",
        "NumeroTanques": "",
        "NumeroDuctosEntradaSalida": "",
        "NumeroDuctosTransporteDistribucion": "",
        "NumeroDispensarios": "",
        "FechaYHoraReporteMes": "",
        "Producto": "",
        "BitacoraMensual": ""
        }

    daily_root = {
        "Version": "",
        "RfcContribuyente": "",
        "RfcRepresentanteLegal": "",
        "RfcProveedor": "",
        "RfcProveedores": "",
        "Caracter": "",
        "ModalidadPermiso": "",
        "NumPermiso": "",
        "NumContratoOAsignacion": "",
        "InstalacionAlmacenGasNatural": "",
        "ClaveInstalacion": "",
        "DescripcionInstalacion": "",
        "Geolocalizacion": "",
        "NumeroPozos": "",
        "NumeroTanques": "",
        "NumeroDuctosEntradaSalida": "",
        "NumeroDuctosTransporteDistribucion": "",
        "NumeroDispensarios": "",
        "FechaYHoraReporteMes": "",
        "Producto": "",
        }

    @classmethod
    def set_caracter_structure(cls, caracter: str) -> None:
        # print(cls.month_root, "BEFO")
        # cls.month_root["caracter"] = caracter
        caracter_keys = caracteres.copy().pop(caracter)
        useless_keys = [value for values in caracteres.values() for value in values]
        useless_keys = list(set(useless_keys) - set(caracter_keys))
        for useless_key in useless_keys:
            cls.month_root.pop(useless_key, None)

    @classmethod
    def set_rfc_proveedores(cls, rfc: str) -> None:
        cls.month_root["RfcProveedores"] = rfc

    @classmethod
    def set_geolocalization(cls, geo_dict: dict) -> None:
        cls.month_root["Geolocalizacion"] = geo_dict

    @classmethod
    def set_json(cls, json_data) -> None:
        try:
            if all(key in json_data for key in cls.month_root):
                for key, value in json_data.items():
                    cls.month_root[key] = value
            else:
                missing_keys = set(cls.month_root) - set(json_data)
                raise KeyError(f"La(s) clave(s) {missing_keys} no se encuentra(n) en el JSON proporcionado.")
        except Exception as exc:
            raise KeyError(f"Error: al crear JSON {str(exc)}") from exc
