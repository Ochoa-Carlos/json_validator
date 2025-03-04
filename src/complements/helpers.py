from typing import TypeVar

from src.complements import (CDLRGNComplement, ComercializationComplement,
                         ComplementBuilder, DistributionComplement,
                         StorageComplement)

ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


def complement_builder(complement_data: dict, complement_type: str) -> ComplementType:
    complement_map = {
        "Almacenamiento": StorageComplement,
        "Comercializacion": ComercializationComplement,
        "Distribucion": DistributionComplement,
        "CDLRGN": CDLRGNComplement
    }

    complement_class = complement_map.get(complement_type)
    return complement_class(complement_dict=complement_data, complement_type=complement_type)
