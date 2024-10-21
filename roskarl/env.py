import os
from typing import List, Optional


def get_env_var(var: str, optional: bool = False) -> str:
    env_var = os.environ.get(var)
    if optional:
        return env_var
    if not env_var:
        raise KeyError(f"Missing required environment variable for '{var}'.")

    return env_var


def get_list_of_strings(input: Optional[str], separator: str) -> List[str]:
    if input is None:
        raise ValueError(f"The environment variable '{input}' is not set.")

    try:
        return [item.strip() for item in input.split(separator)]
    except Exception as e:
        raise ValueError(f"Error parsing the environment variable '{input}': {e}")
