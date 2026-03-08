import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from icron import croniter
from typing import Any
from dataclasses import dataclass, field
import re
from urllib.parse import unquote, quote
from datetime import datetime


def print_unset(name: str) -> None:
    print(f"{name} not set or set to None.")


def env_var(
    name: str, default: str | None = None, should_print_unset: bool = True
) -> str | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    return value


def env_var_cron(
    name: str, default: str | None = None, should_print_unset: bool = True
) -> str | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    if not croniter.is_valid(expression=value):
        raise ValueError("Value is not a valid cron expression.")
    return value


def env_var_tz(
    name: str, default: str | None = None, should_print_unset: bool = True
) -> str | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as e:
        raise ValueError(f"Timezone string was not valid. {e}")
    return value


def env_var_list(
    name: str,
    separator: str = ",",
    default: list[str] | None = None,
    should_print_unset: bool = True,
) -> list[str] | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    try:
        return [item.strip() for item in value.split(separator)]
    except Exception as e:
        raise ValueError(f"Error parsing list from env var '{name}': {e}")


def env_var_bool(
    name: str, default: bool | None = None, should_print_unset: bool = True
) -> bool | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    if value.upper() == "TRUE":
        return True
    if value.upper() == "FALSE":
        return False
    raise ValueError(
        f"Bool must be set to true or false (case insensitive), not: '{value}'"
    )


def env_var_int(
    name: str, default: int | None = None, should_print_unset: bool = True
) -> int | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    try:
        return int(value)
    except ValueError:
        raise


def env_var_float(
    name: str, default: float | None = None, should_print_unset: bool = True
) -> float | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    try:
        return float(value)
    except ValueError:
        raise


def env_var_iso8601_datetime(
    name: str, default: datetime | None = None, should_print_unset: bool = True
) -> datetime | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(
            f"'{name}' is not a valid ISO8601 datetime string: '{value}'. "
            "Expected format: 2026-01-01T00:00:00 or 2026-01-01T00:00:00+00:00"
        )


def env_var_rfc3339_datetime(
    name: str, default: datetime | None = None, should_print_unset: bool = True
) -> datetime | None:
    value = os.environ.get(name)
    if not value:
        if should_print_unset:
            print_unset(name)
        return default
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
    protocol: str
    username: str
    password: str
    hostname: str
    port: int | None = None
    database: str | None = None
    connection_string: str = field(init=False, repr=False)
    libpq_string: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        port_str = f":{self.port}" if self.port is not None else ""
        db_str = f"/{self.database}" if self.database is not None else ""
        quoted_username = quote(self.username, safe="")
        quoted_password = quote(self.password, safe="")
        self.connection_string = f"{self.protocol}://{quoted_username}:{quoted_password}@{self.hostname}{port_str}{db_str}"
        parts = [
            f"host={self.hostname}",
            f"user={self.username}",
            f"password={self.password}",
        ]
        if self.port is not None:
            parts.append(f"port={self.port}")
        if self.database is not None:
            parts.append(f"dbname={self.database}")
        self.libpq_string = " ".join(parts)

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
