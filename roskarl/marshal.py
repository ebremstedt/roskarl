from dataclasses import dataclass, field
from datetime import datetime
import importlib
from pathlib import Path
import types
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
import importlib.util
import sys
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


def _module_matches(
    module: types.ModuleType,
    stem: str,
    models: list[str] | None,
    tags: list[str] | None,
) -> bool:
    if models is not None and stem not in models:
        return False
    if tags is not None:
        model = getattr(module, "model", None)
        if model is None:
            return False
        module_tags: list[str] = getattr(model, "tags", [])
        return any(tag in module_tags for tag in tags)
    return True


def get_execute_functions(
    folder: str = "src/models",
    models: list[str] | None = None,
    tags: list[str] | None = None,
) -> list[Callable]:
    """
    Discover and return execute functions from Python modules in a folder recursively.

    Args:
        folder: Path to the folder containing model modules.
        models: Optional list of model names to filter by.
        tags: Optional list of tags to filter by.
            If neither models nor tags are provided, all models are returned.

    Returns:
        List of callable execute functions from matched modules.

    Raises:
        ValueError: If both models and tags are provided, or either is an empty list.
    """
    if models and tags:
        raise ValueError("Use either models or tags to filter execute functions.")
    if models and len(models) == 0:
        raise ValueError("If models is provided, it must be a non-empty list.")
    if tags and len(tags) == 0:
        raise ValueError("If tags is provided, it must be a non-empty list.")

    if tags:
        print(f"Filtering execute functions to those with tags: {tags}")
    if models:
        print(f"Filtering execute functions to those with models: {models}")

    folder_path = Path(folder)
    parent_dir = str(folder_path.parent)
    added_to_path = False
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        added_to_path = True

    try:
        execute_functions = []
        model_names = []
        for file in folder_path.rglob("*.py"):
            module_spec = importlib.util.spec_from_file_location(
                name=file.stem, location=file
            )
            module = importlib.util.module_from_spec(spec=module_spec)
            module_spec.loader.exec_module(module)
            if _module_matches(module, file.stem, models, tags):
                execute_functions.append(module.execute)
                model_names.append(file.stem)
        if not tags and not models:
            print(f"No filter used yielded models: {model_names}")
        return execute_functions
    finally:
        if added_to_path:
            sys.path.remove(parent_dir)
