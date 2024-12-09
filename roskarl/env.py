import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from croniter import croniter


def print_if_not_set(name: str):
    print(f"{name} is either not set or set to None.")


def env_var(name: str) -> str | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    return value


def env_var_cron(name: str) -> str | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    if not croniter.is_valid(expression=value):
        raise ValueError("Value is not a valid cron expression.")

    return value


def env_var_tz(name: str) -> str | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as e:
        raise ValueError(f"Timezone string was not valid. {e}")

    return value


def env_var_list(name: str, separator: str = ",") -> list | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var
        separator (str):  if getting list, which separator to use

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    try:
        return [item.strip() for item in value.split(separator)]
    except Exception as e:
        raise ValueError(f"Error parsing list from env var '{name}': {e}")


def env_var_bool(name: str) -> bool | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    if value.upper() == "TRUE":
        return True
    if value.upper() == "FALSE":
        return False
    raise ValueError(
        f"Bool must be set to true or false (case insensitive), not: '{value}'"
    )


def env_var_int(name: str) -> int | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    return int(value)


def env_var_float(name: str) -> float | None:
    """Get environment variable

    Parameters:
        name (str): the name of the env var

    Returns:
        value of env var
    """
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    return float(value)
