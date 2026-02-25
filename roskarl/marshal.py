from dataclasses import dataclass, field
from datetime import datetime
from roskarl import (
    env_var_bool,
    env_var_cron,
    env_var_int,
    env_var_iso8601_datetime,
    env_var_list,
)
from croniter import croniter
from functools import wraps
from typing import Callable


@dataclass
class CronConfig:
    enabled: bool
    expression: str | None
    since: datetime | None
    until: datetime | None


@dataclass
class BackfillConfig:
    enabled: bool
    since: datetime | None
    until: datetime | None
    batch_size: int | None


@dataclass
class EnvConfig:
    models: list[str] | None
    tags: list[str] | None
    cron: CronConfig
    backfill: BackfillConfig
    debug: bool = field(default=False)


def _resolve_cron_interval(expression: str) -> tuple[datetime, datetime]:
    now = datetime.now()
    cron = croniter(expression, now)
    until = cron.get_prev(datetime)
    since = cron.get_prev(datetime)
    return since, until


def load_env_config() -> EnvConfig:
    cron_enabled = env_var_bool(name="CRON_ENABLED") or False
    backfill_enabled = env_var_bool(name="BACKFILL_ENABLED") or False

    if cron_enabled and backfill_enabled:
        raise ValueError("CRON_ENABLED and BACKFILL_ENABLED cannot both be true")

    cron_expression = env_var_cron(name="CRON_EXPRESSION") if cron_enabled else None
    cron_since, cron_until = (
        _resolve_cron_interval(cron_expression) if cron_expression else (None, None)
    )

    return EnvConfig(
        models=env_var_list(name="MODELS"),
        tags=env_var_list(name="TAGS"),
        cron=CronConfig(
            enabled=cron_enabled,
            expression=cron_expression,
            since=cron_since,
            until=cron_until,
        ),
        backfill=BackfillConfig(
            enabled=backfill_enabled,
            since=env_var_iso8601_datetime(name="BACKFILL_SINCE")
            if backfill_enabled
            else None,
            until=env_var_iso8601_datetime(name="BACKFILL_UNTIL")
            if backfill_enabled
            else None,
            batch_size=env_var_int(name="BACKFILL_BATCH_SIZE")
            if backfill_enabled
            else None,
        ),
        debug=env_var_bool(name="DEBUG") or False,
    )


def with_env_config(func: Callable[[EnvConfig], None]) -> Callable[[], None]:
    @wraps(func)
    def wrapper() -> None:
        env = load_env_config()
        func(env)

    return wrapper
