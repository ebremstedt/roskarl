import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Any, Literal, overload
from dataclasses import dataclass, field
import re
from urllib.parse import unquote, quote
from datetime import datetime
from roskarl.notify import print_unset


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    return value


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as e:
        raise ValueError(f"Timezone string was not valid. {e}")
    return value


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    try:
        return [item.strip() for item in value.split(separator)]
    except Exception as e:
        raise ValueError(f"Error parsing list from env var '{name}': {e}")


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    if value.upper() == "TRUE":
        return True
    if value.upper() == "FALSE":
        return False
    raise ValueError(
        f"Bool must be set to true or false (case insensitive), not: '{value}'"
    )


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    try:
        return int(value)
    except ValueError:
        raise


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    try:
        return float(value)
    except ValueError:
        raise


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"'{name}' is not a valid ISO8601 datetime string: '{value}'. "
            "Expected format: 2026-01-01T00:00:00 or 2026-01-01T00:00:00+00:00"
        )


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
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
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

    def build_db2_string(self, ssl_cert_path: str | None = None) -> str:
        if self.port is None:
            raise ValueError("port is required for DB2 connection string")
        if self.database is None:
            raise ValueError("database is required for DB2 connection string")
        base = (
            f"DATABASE={self.database};"
            f"HOSTNAME={self.hostname};"
            f"PORT={self.port};"
            f"PROTOCOL=TCPIP;"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        if ssl_cert_path:
            base += f"Security=SSL;SSLServerCertificate={ssl_cert_path};"
        return base

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
