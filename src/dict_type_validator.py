from src.custom_exceptions import TipadoError


class DictionaryTypeValidator:
    """Class for validate values type in dictionaries."""

    @classmethod
    def validate_dict_type(cls, dict_to_validate: dict, dict_type: dict[str, type]) -> bool:
        """Validate type values in dictionary based on base dict typing."""
        for key, value in dict_to_validate.items():
            if key not in dict_type:
                continue
            if not isinstance(value, dict_type[key]):
                key_type = str(dict_type[key])
                expected_type = dict_type[key]
                type_extracted = key_type.split("'")[1]

                if hasattr(expected_type, 'min_val') and hasattr(expected_type, 'max_val'):
                    try:
                        value = expected_type(value)
                        return
                    except (TypeError, ValueError) as e:
                        return {
                            "type_err": TipadoError,
                            "err_message": f"Error: Clave {key} no usa la definición {expected_type.__name__}{e}"
                        }
                if "." in type_extracted:
                    print("TYP EXPECTED HAY UN PUNTO VER SI ESTE I SIRVE A FUTURO.")
                    type_extracted = type_extracted.split(".")[-1]
                return {
                    "type_err": TipadoError,
                    "err_message": f"Error: Clave {key} no es de tipo {type_extracted}"
                    }
