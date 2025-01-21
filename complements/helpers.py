from typing import TypeVar
from complements import StorageComplement, ComplementBuilder, ComercializationComplement, DistributionComplement


ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


def complement_builder(complement_data: dict, complement_type: str) -> ComplementType:
    print("INSTANCIANDO COMPLEMETNO")
    complement_map = {
        "Almacenamiento": StorageComplement,
        "Comercializacion": ComercializationComplement,
        "Distribucion": DistributionComplement,
    }

    complement_class = complement_map.get(complement_type)
    return complement_class(complement_dict=complement_data, complement_type=complement_type)
