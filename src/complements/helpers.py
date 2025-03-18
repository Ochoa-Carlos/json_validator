from typing import TypeVar

from src.complements import (CDLRGNComplement, ComercializationComplement,
                             ComplementBuilder, DistributionComplement,
                             ExpenditureComplement, StorageComplement,
                             TransportComplement)
from src.utils.logger import logger

ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


logging = logger()


def complement_builder(complement_data: dict, complement_type: str) -> ComplementType:
    """Complement builder objects."""
    try:
        complement_map = {
            "Almacenamiento": StorageComplement,
            "Comercializacion": ComercializationComplement,
            "CDLRGN": CDLRGNComplement,
            "Distribucion": DistributionComplement,
            "Expendio": ExpenditureComplement,
            "Transporte": TransportComplement,
        }

        complement_class = complement_map.get(complement_type)
        return complement_class(complement_dict=complement_data, complement_type=complement_type)
    except Exception as exc:
        logging.warning(f"Error al crear el complemento: {exc}")
