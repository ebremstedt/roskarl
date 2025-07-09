import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from croniter import croniter
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import re
from urllib.parse import unquote, quote


def print_if_not_set(name: str):
    print(f"{name} is either not set or set to None.")


def env_var(name: str) -> Optional[str]:
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


def env_var_cron(name: str) -> Optional[str]:
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


def env_var_tz(name: str) -> Optional[str]:
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


def env_var_list(name: str, separator: str = ",") -> Optional[List[str]]:
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


def env_var_bool(name: str) -> Optional[bool]:
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


def env_var_int(name: str) -> Optional[int]:
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


def env_var_float(name: str) -> Optional[float]:
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


@dataclass
class DSN:
    protocol: str
    username: str
    password: str
    hostname: str
    port: Optional[int] = None
    database: Optional[str] = None
    connection_string: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""

        quoted_username = quote(self.username, safe="")
        quoted_password = quote(self.password, safe="")

        self.connection_string = f"{self.protocol}://{quoted_username}:{quoted_password}@{self.hostname}{port_str}{db_str}"

    def __str__(self) -> str:
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        return (
            f"{self.protocol}://{self.username}:****@{self.hostname}{port_str}{db_str}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol": self.protocol,
            "username": self.username,
            "password": self.password,
            "hostname": self.hostname,
            "port": self.port,
            "database": self.database,
        }


def env_var_dsn(name: str) -> Optional[DSN]:
    value = os.environ.get(name)
    if not value:
        print_if_not_set(name=name)
        return None

    try:
        protocol_match = re.match(r"^([^:]+)://", value)
        if not protocol_match:
            raise ValueError("Invalid DSN: Protocol not found")

        protocol = protocol_match.group(1)
        remaining = value[len(protocol_match.group(0)) :]

        # Parse using regex to handle URL-encoded @ symbols
        auth_host_match = re.match(r"^(.+?)@([^@]+)$", remaining)
        if not auth_host_match:
            raise ValueError("Invalid DSN: No @ separator found")

        credentials = auth_host_match.group(1)
        host_part = auth_host_match.group(2)

        # Find the first unencoded colon for username:password separator
        colon_pos = None
        i = 0
        while i < len(credentials):
            if credentials[i] == ":":
                # Check if this colon is URL-encoded (%3A)
                if i >= 3 and credentials[i - 3 : i] == "%3A":
                    i += 1
                    continue
                else:
                    colon_pos = i
                    break
            i += 1

        if colon_pos is None:
            raise ValueError("Invalid DSN: No colon separator found in credentials")

        username = unquote(credentials[:colon_pos])
        password = unquote(credentials[colon_pos + 1 :])

        database_parts = host_part.split("/", 1)
        host_and_port = database_parts[0]
        database = database_parts[1] if len(database_parts) > 1 else None

        if ":" in host_and_port:
            hostname, port_str = host_and_port.rsplit(":", 1)
            port = int(port_str)
        else:
            hostname = host_and_port
            port = None

        return DSN(
            protocol=protocol,
            username=username,
            password=password,
            hostname=hostname,
            port=port,
            database=database,
        )

    except ValueError as e:
        raise ValueError(f"Failed to parse DSN string: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse DSN string: Unexpected error - {str(e)}")
