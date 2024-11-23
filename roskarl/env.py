import os
from enum import Enum, auto


class EnvVarType(Enum):
    STRING_VAR = auto()
    LIST_VAR = auto()
    BOOL_VAR = auto()
    INT_VAR = auto()


def get_env_var(
    var: str,
    env_var_type: EnvVarType = EnvVarType.STRING_VAR,
    list_separator: str = ",",
) -> str | list | bool | int:
    """Get environment variable

    Parameters:
        var: the var to get
        env_var_type (EnvVarType): the kind of value you expect to retrieve from var
        list_separator: if getting list, which separator to use

    Returns:
        value of env var
    """
    env_var = os.environ.get(var)
    if not env_var:
        raise KeyError(f"Missing required environment variable for '{var}'.")

    if env_var_type == EnvVarType.STRING_VAR:
        return env_var

    if env_var_type == EnvVarType.LIST_VAR:
        try:
            return [item.strip() for item in var.split(list_separator)]
        except Exception as e:
            raise ValueError(f"Error parsing list from env var '{var}': {e}")

    if env_var_type == EnvVarType.BOOL_VAR:
        if env_var.upper() == "TRUE":
            return True
        if env_var.upper() == "False":
            return False

        raise ValueError(f"Bool must be set to true or false '{env_var}': {e}")

    if env_var_type == EnvVarType.INT_VAR:
        if env_var.isnumeric():
            return int(env_var)

        raise ValueError(f"Int must be set to a valid integer '{env_var}': {e}")
