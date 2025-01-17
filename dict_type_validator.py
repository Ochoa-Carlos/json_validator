

class DictionaryTypeValidator:
    """Class for validate values type in dictionaries."""

    @classmethod
    def validate_dict_type(cls, dict_to_validate: dict, dict_type: dict[str, type]) -> bool:
        """Validate type values in dictionary based on base dict typing."""
        for key, value in dict_to_validate.items():
            if key not in dict_type:
                continue
            if not isinstance(value, dict_type[key]):
                raise TypeError(
                    f"Error: Clave {key} no es de tipo {dict_type[key]}"
                    )
