from typing import Annotated
import os
from roskarl.notify import print_unset
from icron import croniter


def _field_has_offset(field: str) -> bool:
    return field != "*" and field != "0" and not field.startswith("*/")


def has_offset(expr: str) -> bool:
    """
    Returns True if any field in the cron expression has an offset.
    A field has an offset if it is not '*', '0', or '*/N'.
    """
    return any(_field_has_offset(f) for f in expr.split())


CronBatch = Annotated[str, "5-field cron expression with no offset fields"]
"""
A subset of 5-field cron expressions that only allows interval-based scheduling with no offset.
Valid fields are limited to '*', '0', or '*/N', ensuring the schedule aligns to zero (e.g. '0 */2 * * *').
Intended to express batch frequency, not a specific point in time.

Valid:   '* * * * *', '0 * * * *', '0 */2 * * *', '0 */6 */2 * *'
Invalid: '0 2 * * *', '0 2/2 * * *', '5 * * * *', '0 */2 2 * *'
"""

CRON_BATCH_SHORTCUTS: dict[str, CronBatch] = {
    "@minutely": "* * * * *",
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
}

CronBatchExtended = Annotated[str, "6-field cron expression with no offset fields"]
"""
A subset of 6-field cron expressions (second minute hour day month weekday) that only
allows interval-based scheduling with no offset. Extends CronBatch with a seconds field,
enabling sub-minute granularity.

Valid:   '* * * * * *', '0 * * * * *', '0 0 * * * *', '0 0 0 * * 0'
Invalid: '5 * * * * *', '0 2 * * * *'
"""

CRON_BATCH_EXTENDED_SHORTCUTS: dict[str, CronBatchExtended] = {
    "@secondly": "* * * * * *",
    "@minutely": "0 * * * * *",
    "@hourly": "0 0 * * * *",
    "@daily": "0 0 0 * * *",
    "@weekly": "0 0 0 * * 0",
}


def env_var_cron(
    name: str,
    default: str | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> str | None:
    """
    Reads a cron expression from an environment variable.

    Raises ValueError if the value is not a valid 5-field cron expression, or if
    required is True and the variable is not set.
    """
    value = os.environ.get(name)
    if not value:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Environment variable '{name}' is not set")
        if should_print_unset:
            print_unset(name)
        return None
    if not croniter.is_valid(expression=value):
        raise ValueError(
            f"Environment variable '{name}' is not a valid cron expression."
        )
    return value


def env_var_cron_batch(
    name: str,
    default: CronBatch | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> CronBatch | None:
    """
    Reads a CronBatch expression from an environment variable.

    Same as env_var_cron but additionally enforces no offset on any field,
    making it suitable for expressing batch frequency rather than a specific point in time.

    Raises ValueError if the value is not a valid cron expression, has an offset on any
    field, or if required is True and the variable is not set.
    """
    value = env_var_cron(
        name=name,
        default=default,
        should_print_unset=should_print_unset,
        required=required,
    )
    if value is not None and has_offset(value):
        raise ValueError(f"Environment variable '{name}' has a cron offset: '{value}'")
    return value


def env_var_cron_batch_extended(
    name: str,
    default: CronBatchExtended | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> CronBatchExtended | None:
    """
    Reads a CronBatchExtended expression from an environment variable.

    Same as env_var_cron_batch but expects a 6-field expression
    (second minute hour day month weekday), enabling sub-minute granularity.

    Raises ValueError if the value is not a valid 6-field cron expression, has an offset
    on any field, or if required is True and the variable is not set.
    """
    value = os.environ.get(name)
    if not value:
        if default is not None:
            value = default
        elif required:
            raise ValueError(f"Environment variable '{name}' is not set")
        else:
            if should_print_unset:
                print_unset(name)
            return None
    if len(value.split()) != 6:
        raise ValueError(
            f"Environment variable '{name}' must be a 6-field cron expression."
        )
    if not croniter.is_valid(expression=value):
        raise ValueError(
            f"Environment variable '{name}' is not a valid cron expression."
        )
    if has_offset(value):
        raise ValueError(f"Environment variable '{name}' has a cron offset: '{value}'")
    return value
