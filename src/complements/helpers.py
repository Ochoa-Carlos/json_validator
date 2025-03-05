from typing import TypeVar

from src.complements import (CDLRGNComplement, ComercializationComplement,
                             ComplementBuilder, DistributionComplement,
                             ExpenditureComplement, StorageComplement)
from src.utils.logger import logger

ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


logging = logger()


def complement_builder(complement_data: dict, complement_type: str) -> ComplementType:
    try:
        complement_map = {
            "Almacenamiento": StorageComplement,
            "Comercializacion": ComercializationComplement,
            "Distribucion": DistributionComplement,
            "Expendio": ExpenditureComplement,
            "CDLRGN": CDLRGNComplement,
        }

        complement_class = complement_map.get(complement_type)
        return complement_class(complement_dict=complement_data, complement_type=complement_type)
    except Exception as exc:
        logging.warning(f"Error al crear el complemento: {exc}")
