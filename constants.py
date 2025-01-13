

caracteres = {
    "contratista": ["NumContratoOAsignacion"],
    "asignatario": ["NumContratoOAsignacion"],
    "permisionario": ["ModalidadPermiso", "NumPermiso"],
    "usuario": ["InstalacionAlmacenGasNatural"]
}

VERSION_REGEX = r"[0-9]+\.[0-9]+$"
MODALITY_PERMISSION_REGEX = r"^PER([1-9]|[1-4][0-9]|5[0-6])$"
UTC_FORMAT_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$"
