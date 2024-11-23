import os
from typing import Optional
from enum import Enum, auto


class EnvVarType(Enum):
    STRING_VAR = auto()
    LIST_VAR = auto()
    BOOL_VAR = auto()


def get_env_var(
    var: str,
    env_var_type: EnvVarType = EnvVarType.STRING_VAR,
    optional: bool = False,
    list_separator: str = ",",
) -> str | list | bool:
    env_var = os.environ.get(var)
    if optional:
        return env_var
    if not env_var:
        raise KeyError(f"Missing required environment variable for '{var}'.")

    if env_var_type == EnvVarType.STRING_VAR:
        return env_var

    if env_var_type == EnvVarType.LIST_VAR:
        try:
            return [item.strip() for item in var.split(list_separator)]
        except Exception as e:
            raise ValueError(
                f"Error parsing list from env var '{var}': {e}"
            )

    if env_var_type == EnvVarType.BOOL_VAR:
        if not var:
            return False
        if var.upper() == "TRUE":
            return True
