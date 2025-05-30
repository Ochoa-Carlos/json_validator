

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
event_type = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21]
component_alarm = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

VERSION_REGEX = r"[0-9]+\.[0-9]+$"
RFC_CONTR_REGEX = r"^([A-ZÑ]|\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
MODALITY_PERMISSION_REGEX = r"^PER([1-9]|[1-4][0-9]|5[0-6])$"
UTC_FORMAT_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$"
SUBPRODUCTO_REGEX = r"^SP([1-9]|[1-3][0-9]|4[0-8])$"
CONDENSEDGAS_REGEX = r"^GNC(0[1-9]|10)$"
RFC_PERSONA_FISICA = r"^([A-ZÑ]|\&){4}[0-9]{2}(0[1-9]|1[0-2])([12][0 -9]|0[1-9]|3[01])[A-Z0-9]{3}$"
FILE_NAME_REGEX = r"^M_([A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12})_[A-Z0-9Ñ&]{12,13}_[A-Z0-9Ñ&]{12}_(\d{4}-\d{2}-\d{2})_(ACA|AUP|ALM|ACO|BSP|BDE|CMN|COM|CON|DEN|DIS|EMA|ESN|EDS|ESA|EXO|EXP|EXT|GSH|LON|RPO|PTA|PDD|PGN|RCN|REF|RGN|SIS|SFO|SDA|TDA|TDD|TRA|TDP|USP|ACL|ASN|MNA|TRE)-\d{4}_(EXT|REF|PGN|CON|DEN|LON|RGN|TRA|ALM|AGA|USP|DIS|CMN|EXO)_JSON$"
