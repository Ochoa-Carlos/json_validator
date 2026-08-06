from typing import Optional

from src.complements import (CDLRGNComplement, ComercializationComplement,
                             ComplementBuilder, DistributionComplement,
                             ExpenditureComplement, StorageComplement,
                             TransportComplement)
from src.utils.logger import logger

logging = logger()


def complement_builder(complement_data: list, complement_type: str) -> Optional[ComplementBuilder]:
    """Build the complement validator that matches the given TipoComplemento.\n
    :param complement_data: List of Complemento objects to validate.\n
    :param complement_type: TipoComplemento value declared in the report.\n
    """
    try:
        complement_map = {
            "Almacenamiento": StorageComplement,
            "Comercializacion": ComercializationComplement,
            "CDLR": CDLRGNComplement,
            "Distribucion": DistributionComplement,
            "Expendio": ExpenditureComplement,
            "Transporte": TransportComplement,
        }

        if (complement_class := complement_map.get(complement_type)) is None:
            logging.warning(f"TipoComplemento sin validador registrado: {complement_type}")
            return None

        return complement_class(complement_dict=complement_data, complement_type=complement_type)
    except Exception as exc:
        logging.warning(f"Error al crear el complemento: {exc}")
        return None
