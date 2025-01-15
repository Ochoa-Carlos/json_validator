

caracteres = {
    "contratista": ["NumContratoOAsignacion"],
    "asignatario": ["NumContratoOAsignacion"],
    "permisionario": ["ModalidadPermiso", "WNumPermiso"],
    "usuario": ["InstalacionAlmacenGasNatural"]
}


products_keys = {
    "PR03": "",
    "PR07": "",
    "PR08": "",
    "PR09": "",
    "PR10": "",
    "PR11": "",
    "PR12": "",
    "PR13": "",
    "PR14": "",
    "PR15": "",
    "PR16": "",
    "PR17": "",
    "PR18": "",
    "PR19": ""
}

subproducts_keys = ["PR03", "PR07", "PR08", "PR09", "PR11", "PR13", "PR15", "PR16", "PR17", "PR18", "PR19"]
petroleo_caracteres = ["contratista", "asignatario"]
cal_value_caracteres = ["contratista", "asignatario"]

VERSION_REGEX = r"[0-9]+\.[0-9]+$"
MODALITY_PERMISSION_REGEX = r"^PER([1-9]|[1-4][0-9]|5[0-6])$"
UTC_FORMAT_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$"
SUBPRODUCTO_REGEX = r"^SP([1-9]|[1-3][0-9]|4[0-8])$"
