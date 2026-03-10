from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from roskarl import (
    env_var_bool,
    env_var_cron,
    env_var,
    env_var_iso8601_datetime,
)
from icron import croniter
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


@dataclass
class EnvConfig:
    name: str
    tags: str | None
    cron: CronConfig
    backfill: BackfillConfig
    debug: bool = field(default=False)

    def __str__(self) -> str:
        return f"EnvConfig(name={self.name}, tags={self.tags}, cron={self.cron}, backfill={self.backfill}, debug={self.debug})"

    def debugprint(self, msg: str) -> None:
        if self.debug:
            ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{ts} {msg}")

    def __post_init__(self) -> None:
        print(f"name:             {self.name}")
        print(f"tags:             {self.tags}")
        print(f"debug:            {self.debug}")
        if self.cron.enabled:
            print(f"cron.expression:  {self.cron.expression}")
            print(f"cron.since:       {self.cron.since}")
            print(f"cron.until:       {self.cron.until}")
        if self.backfill.enabled:
            print(f"backfill.since:   {self.backfill.since}")
            print(f"backfill.until:   {self.backfill.until}")


def _resolve_cron_interval(expression: str) -> tuple[datetime, datetime]:
    now = datetime.now(tz=timezone.utc)
    cron = croniter(expression, now - timedelta(days=2))
    ticks = []
    while True:
        tick = cron.get_next(datetime)
        if tick >= now:
            break
        ticks.append(tick)
    since = ticks[-2]
    until = ticks[-1]
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
        name=env_var(name="PIPELINE_ENVIRONMENT", required=True),
        tags=env_var(name="TAGS", required=True),
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
        ),
        debug=env_var_bool(name="DEBUG") or False,
    )


def with_env_config(func: Callable[[EnvConfig], None]) -> Callable[[], None]:
    @wraps(func)
    def wrapper() -> None:
        env = load_env_config()
        func(env)

    return wrapper
