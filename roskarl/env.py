import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Literal, TypeVar, overload
from urllib.parse import quote, unquote, urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def print_unset(name: str) -> None:
    print(f"{name} not set or set to None.")


@overload
def env_var_custom(
    name: str,
    parser: Callable[[str], T],
    default: T | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> T: ...


@overload
def env_var_custom(
    name: str,
    parser: Callable[[str], T],
    default: T | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> T | None: ...


def env_var_custom(
    name: str,
    parser: Callable[[str], T],
    default: T | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> T | None:
    """Reads an environment variable and parses it with a caller-supplied function."""
    value = os.environ.get(name)
    if value:
        return parser(value)
    if default is not None:
        return default
    if required:
        raise ValueError(f"Environment variable '{name}' is not set")
    if should_print_unset:
        print_unset(name)
    return None


@overload
def env_var(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> str: ...


@overload
def env_var(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> str | None: ...


def env_var(
    name: str,
    default: str | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> str | None:
    return env_var_custom(name, str, default, should_print_unset, required)


@overload
def env_var_tz(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> str: ...


@overload
def env_var_tz(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> str | None: ...


def env_var_tz(
    name: str,
    default: str | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> str | None:
    def parse(value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as e:
            raise ValueError(f"Timezone string was not valid. {e}")
        return value

    if default is not None:
        default = parse(default)

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_list(
    name: str,
    separator: str = ...,
    default: list[str] | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> list[str]: ...


@overload
def env_var_list(
    name: str,
    separator: str = ...,
    default: list[str] | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> list[str] | None: ...


def env_var_list(
    name: str,
    separator: str = ",",
    default: list[str] | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> list[str] | None:
    def parse(value: str) -> list[str]:
        try:
            return [item.strip() for item in value.split(separator)]
        except Exception as e:
            raise ValueError(f"Error parsing list from env var '{name}': {e}")

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_bool(
    name: str,
    default: bool | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> bool: ...


@overload
def env_var_bool(
    name: str,
    default: bool | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> bool | None: ...


def env_var_bool(
    name: str,
    default: bool | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> bool | None:
    def parse(value: str) -> bool:
        if value.upper() == "TRUE":
            return True
        if value.upper() == "FALSE":
            return False
        raise ValueError(
            f"Bool must be set to true or false (case insensitive), not: '{value}'"
        )

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_int(
    name: str,
    default: int | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> int: ...


@overload
def env_var_int(
    name: str,
    default: int | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> int | None: ...


def env_var_int(
    name: str,
    default: int | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> int | None:
    return env_var_custom(name, int, default, should_print_unset, required)


@overload
def env_var_float(
    name: str,
    default: float | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> float: ...


@overload
def env_var_float(
    name: str,
    default: float | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> float | None: ...


def env_var_float(
    name: str,
    default: float | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> float | None:
    return env_var_custom(name, float, default, should_print_unset, required)


@overload
def env_var_iso8601_datetime(
    name: str,
    default: datetime | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> datetime: ...


@overload
def env_var_iso8601_datetime(
    name: str,
    default: datetime | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> datetime | None: ...


def env_var_iso8601_datetime(
    name: str,
    default: datetime | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> datetime | None:
    def parse(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"'{name}' is not a valid ISO8601 datetime string: '{value}'. "
                "Expected format: 2026-01-01T00:00:00 or 2026-01-01T00:00:00+00:00"
            )

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_rfc3339_datetime(
    name: str,
    default: datetime | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> datetime: ...


@overload
def env_var_rfc3339_datetime(
    name: str,
    default: datetime | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> datetime | None: ...


def env_var_rfc3339_datetime(
    name: str,
    default: datetime | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> datetime | None:
    def parse(value: str) -> datetime:
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"'{name}' is not a valid RFC3339 datetime string: '{value}'. "
                "Expected format: 2026-01-01T00:00:00+00:00"
            )
        if dt.tzinfo is None:
            raise ValueError(
                f"'{name}' is missing timezone info, RFC3339 requires it: '{value}'. "
                "Expected format: 2026-01-01T00:00:00+00:00"
            )
        return dt

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_url(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> str: ...


@overload
def env_var_url(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> str | None: ...


def env_var_url(
    name: str,
    default: str | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> str | None:
    """
    Reads a URL from an environment variable.

    Validates that the value has a scheme (e.g. http, https, postgresql) and
    a network location. Returns the URL string as-is.
    """

    def parse(value: str) -> str:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"'{name}' is not a valid URL: '{value}'")
        return value

    if default is not None:
        default = parse(default)

    return env_var_custom(name, parse, default, should_print_unset, required)


class Secret:
    """
    A string-like value that masks itself in repr/str to avoid accidental
    leakage to logs, tracebacks, or error-reporting tools (Sentry, etc.).

    Call .reveal() at the point of use to access the raw value.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "Secret('***')"

    def __str__(self) -> str:
        return "***"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Secret):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


@overload
def env_var_secret(
    name: str,
    default: Secret | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> Secret: ...


@overload
def env_var_secret(
    name: str,
    default: Secret | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> Secret | None: ...


def env_var_secret(
    name: str,
    default: Secret | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> Secret | None:
    """
    Reads a secret from an environment variable and wraps it in a Secret
    so it can't be accidentally logged or printed.
    """
    return env_var_custom(name, Secret, default, should_print_unset, required)


@overload
def env_var_path(
    name: str,
    default: Path | None = ...,
    should_print_unset: bool = ...,
    must_exist: bool = ...,
    *,
    required: Literal[True],
) -> Path: ...


@overload
def env_var_path(
    name: str,
    default: Path | None = ...,
    should_print_unset: bool = ...,
    must_exist: bool = ...,
    required: bool = ...,
) -> Path | None: ...


def env_var_path(
    name: str,
    default: Path | None = None,
    should_print_unset: bool = True,
    must_exist: bool = False,
    required: bool = False,
) -> Path | None:
    """
    Reads a filesystem path from an environment variable.

    If must_exist=True, raises ValueError if the path does not exist on disk
    (applied to both env value and default).
    """

    def parse(value: str) -> Path:
        p = Path(value)
        if must_exist and not p.exists():
            raise ValueError(f"'{name}' path does not exist: '{p}'")
        return p

    if default is not None and must_exist and not default.exists():
        raise ValueError(f"'{name}' default path does not exist: '{default}'")

    return env_var_custom(name, parse, default, should_print_unset, required)


@overload
def env_var_enum(
    name: str,
    enum_class: type[EnumT],
    default: EnumT | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> EnumT: ...


@overload
def env_var_enum(
    name: str,
    enum_class: type[EnumT],
    default: EnumT | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> EnumT | None: ...


def env_var_enum(
    name: str,
    enum_class: type[EnumT],
    default: EnumT | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> EnumT | None:
    """
    Reads an enum-valued environment variable.

    Matches the value against the .value attribute of each member of enum_class.
    Raises ValueError if no member matches.
    """

    def parse(value: str) -> EnumT:
        try:
            return enum_class(value)
        except ValueError:
            valid = [e.value for e in enum_class]
            raise ValueError(f"'{name}' must be one of {valid}, got '{value}'")

    return env_var_custom(name, parse, default, should_print_unset, required)


_LOG_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.CRITICAL,
}


@overload
def env_var_log_level(
    name: str,
    default: int | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> int: ...


@overload
def env_var_log_level(
    name: str,
    default: int | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> int | None: ...


def env_var_log_level(
    name: str,
    default: int | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> int | None:
    """
    Reads a logging level name from an environment variable and returns the
    numeric level (e.g. 'INFO' -> 20).

    Accepts DEBUG, INFO, WARNING (or WARN), ERROR, CRITICAL (or FATAL).
    Matching is case-insensitive.
    """

    def parse(value: str) -> int:
        level = _LOG_LEVELS.get(value.upper())
        if level is None:
            raise ValueError(
                f"'{name}' must be one of {list(_LOG_LEVELS)}, got '{value}'"
            )
        return level

    return env_var_custom(name, parse, default, should_print_unset, required)


_DURATION_RE = re.compile(r"^(?:\d+(?:ms|s|m|h|d))+$")
_DURATION_PART = re.compile(r"(\d+)(ms|s|m|h|d)")
_DURATION_UNITS = {
    "ms": "milliseconds",
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
}


@overload
def env_var_duration(
    name: str,
    default: timedelta | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> timedelta: ...


@overload
def env_var_duration(
    name: str,
    default: timedelta | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> timedelta | None: ...


def env_var_duration(
    name: str,
    default: timedelta | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> timedelta | None:
    """
    Reads a duration from an environment variable and returns a timedelta.

    Accepts compound durations using the suffixes: ms, s, m (minutes), h, d.
    Examples: '30s', '5m', '1h30m', '500ms', '7d'. Spaces between parts are
    tolerated ('1h 30m').
    """

    def parse(value: str) -> timedelta:
        cleaned = value.replace(" ", "")
        if not _DURATION_RE.fullmatch(cleaned):
            raise ValueError(
                f"'{name}' is not a valid duration: '{value}'. "
                "Expected format like '30s', '5m', '1h30m', '500ms'."
            )
        kwargs: dict[str, int] = {}
        for num, unit in _DURATION_PART.findall(cleaned):
            key = _DURATION_UNITS[unit]
            kwargs[key] = kwargs.get(key, 0) + int(num)
        return timedelta(**kwargs)

    return env_var_custom(name, parse, default, should_print_unset, required)


@dataclass
class DSN:
    """
    Represents a parsed Data Source Name (DSN) connection string.

    Attributes:
        protocol: Database protocol (e.g. postgresql, mssql)
        username: Database user
        password: Database password
        hostname: Database host
        port: Database port
        database: Database name
        connection_string: Auto-built URI connection string (e.g. postgresql://user:pass@host:port/db)
        libpq_string: Auto-built libpq connection string (e.g. host=... user=... password=...)

    Example:
        dsn = DSN(protocol="postgresql", username="user", password="pass", hostname="localhost", port=5432, database="mydb")
        dsn.connection_string  # postgresql://user:pass@localhost:5432/mydb
        dsn.build_mssql_string()  # DRIVER={ODBC Driver 18 for SQL Server};SERVER=...
    """

    protocol: str
    username: str
    password: str
    hostname: str
    port: int | None = None
    database: str | None = None
    connection_string: str = field(init=False, repr=False)
    libpq_string: str = field(init=False, repr=False)

    def _build_connection_string(self) -> str:
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        quoted_username = quote(self.username, safe="")
        quoted_password = quote(self.password, safe="")
        return f"{self.protocol}://{quoted_username}:{quoted_password}@{self.hostname}{port_str}{db_str}"

    def _build_libpq_string(self) -> str:
        parts = [
            f"host={self.hostname}",
            f"user={self.username}",
            f"password={self.password}",
        ]
        if self.port is not None:
            parts.append(f"port={self.port}")
        if self.database is not None:
            parts.append(f"dbname={self.database}")
        return " ".join(parts)

    def build_mssql_string(
        self,
        driver: str = "ODBC Driver 18 for SQL Server",
        encrypt: bool = True,
        trust_server_certificate: bool = True,
    ) -> str:
        """
        Builds an ODBC connection string for Microsoft SQL Server.

        Args:
            driver: ODBC driver name
            encrypt: Whether to encrypt the connection
            trust_server_certificate: Whether to trust the server certificate

        Returns:
            ODBC connection string e.g. DRIVER={ODBC Driver 18 for SQL Server};SERVER=host,1433;...

        Raises:
            ValueError: If port or database are None
        """
        if self.port is None:
            raise ValueError("port is required for MSSQL connection string")
        if self.database is None:
            raise ValueError("database is required for MSSQL connection string")
        yes_no = lambda b: "yes" if b else "no"
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.hostname},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Encrypt={yes_no(encrypt)};"
            f"TrustServerCertificate={yes_no(trust_server_certificate)}"
        )

    def __post_init__(self) -> None:
        self.connection_string = self._build_connection_string()
        self.libpq_string = self._build_libpq_string()

    def __str__(self) -> str:
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        return (
            f"{self.protocol}://{self.username}:****@{self.hostname}{port_str}{db_str}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "username": self.username,
            "password": self.password,
            "hostname": self.hostname,
            "port": self.port,
            "database": self.database,
        }


def env_var_dsn(name: str, default: DSN | None = None) -> DSN:
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{name}' is not set")
    try:
        protocol_match = re.match(r"^([^:]+)://", value)
        if not protocol_match:
            raise ValueError("Invalid DSN: Protocol not found")
        protocol = protocol_match.group(1)
        remaining = value[len(protocol_match.group(0)) :]
        auth_host_match = re.match(r"^(.+?)@([^@]+)$", remaining)
        if not auth_host_match:
            raise ValueError("Invalid DSN: No @ separator found")
        credentials = auth_host_match.group(1)
        host_part = auth_host_match.group(2)
        colon_pos = None
        i = 0
        while i < len(credentials):
            if credentials[i] == ":":
                if i >= 3 and credentials[i - 3 : i] == "%3A":
                    i += 1
                    continue
                else:
                    colon_pos = i
                    break
            i += 1
        if colon_pos is None:
            raise ValueError(
                "Invalid DSN: No colon separator found in connection string"
            )
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
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse DSN string: Unexpected error - {str(e)}")
