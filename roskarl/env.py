import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from croniter import croniter
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from urllib.parse import quote


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
    """
    Data Source Name (DSN) for database connections.

    This class represents a structured database connection string, providing
    methods to safely display, serialize, and access connection components.

    Attributes:
        protocol (str): The database protocol (e.g., 'postgresql', 'mysql')
        username (str): The database username
        password (str): The database password (handled securely in string representation)
        hostname (str): The database server hostname or IP address
        port (Optional[int]): The database server port (optional)
        database (Optional[str]): The database name (optional)
        connection_string (Optional[str]): The complete connection string, automatically
            generated in __post_init__

    Examples:
        >>> dsn = DSN('postgresql', 'user', 'password', 'localhost', 5432, 'mydb')
        >>> str(dsn)
        'postgresql://user:****@localhost:5432/mydb'
        >>> dsn.connection_string
        'postgresql://user:password@localhost:5432/mydb'
    """
    protocol: str
    username: str
    password: str
    hostname: str
    port: Optional[int] = None
    database: Optional[str] = None
    connection_string: Optional[str] = None

    def __post_init__(self):
        """Generate the full connection string after initialization."""
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""

        quoted_username = quote(self.username)
        quoted_password = quote(self.password)

        self.connection_string = f"{self.protocol}://{quoted_username}:{quoted_password}@{self.hostname}{port_str}{db_str}"

    def __str__(self) -> str:
        """
        Return a string representation with the password masked.

        Returns:
            str: DSN string with password replaced by '****'
        """
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        return f"{self.protocol}://{self.username}:****@{self.hostname}{port_str}{db_str}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DSN to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary containing all DSN components
        """
        return {
            'protocol': self.protocol,
            'username': self.username,
            'password': self.password,
            'hostname': self.hostname,
            'port': self.port,
            'database': self.database
        }

    def get_safe_connection_string(self) -> str:
        """
        Return a connection string with the password masked.

        Similar to __str__ but explicitly named for clarity when needed.

        Returns:
            str: Connection string with password masked
        """
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        return f"{self.protocol}://{self.username}:****@{self.hostname}{port_str}{db_str}"