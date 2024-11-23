import os
from typing import Optional, Type


def env_var(
    name: str,
    type_: Optional[Type] = str,
    separator: Optional[str] = ",",
) -> str | list | bool | int:
    """Get environment variable

    Parameters:
        var (str): the var to get
        type_ (Type): the kind of value you expect to retrieve from var
        separator (str):  if getting list, which separator to use

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        raise KeyError(f"Missing required environment variable for '{name}'.")

    allowed_types = [int, str, list, bool]
    if type_ not in allowed_types:
        raise ValueError(
            f"Type {type_} is not allowed. Use one of {', '.join(allowed_types)}"
        )

    if type_ == str:
        return value

    if type_ == list:
        try:
            return [item.strip() for item in value.split(separator)]
        except Exception as e:
            raise ValueError(f"Error parsing list from env var '{name}': {e}")

    if type_ == bool:
        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False

        raise ValueError(
            f"Bool must be set to true or false (case insensitive), not: '{value}'"
        )

    if type_ == int:
        if value.isnumeric():
            return int(value)

        raise ValueError(f"Int must be set to a valid integer, not: '{value}'")
