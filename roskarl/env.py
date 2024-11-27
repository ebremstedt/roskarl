import os
from typing import Optional, Type
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from croniter import croniter


def env_var(
    name: str,
    type_: Optional[Type] = str,
    separator: Optional[str] = ",",
    cron: bool = False,
    tz: bool = False,
) -> Optional[str | list | bool | int | float]:
    """Get environment variable

    Parameters:
        var (str): the var to get
        type_ (Type): the kind of value you expect to retrieve from var
        separator (str):  if getting list, which separator to use

    Returns:
        value of env var
    """
    allowed_types = [int, str, list, bool, float]
    if type_ not in allowed_types:
        raise ValueError(
            f"Type {type_} is not allowed. Use one of {', '.join(allowed_types)}"
        )

    value = os.environ.get(name)
    if not value:
        print(f"{name} is either not set or set to None.")
        return None

    if type_ == str:
        if cron:
            if not croniter.is_valid(expression=value):
                raise ValueError(f"Value is not a valid cron expression.")
        if tz:
            try:
                ZoneInfo(value)
            except ZoneInfoNotFoundError as e:
                raise ValueError(f"Timezone string was not valid. {e}")
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
        return int(value)

    if type_ == float:
        return float(value)
