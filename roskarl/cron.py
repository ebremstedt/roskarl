from typing import Annotated, Literal, overload
import os
from roskarl.notify import print_unset
from icron import croniter


def _field_has_offset(field: str, allow_one: bool = False) -> bool:
    if allow_one and field == "1":
        return False
    return field != "*" and field != "0" and not field.startswith("*/")


def has_offset(expr: str) -> bool:
    """
    Returns True if any field in the cron expression has an offset.
    A field has an offset if it is not '*', '0', or '*/N'.

    Exception: the day-of-month field also allows '1'. Days are 1-indexed in cron,
    so '1' is the natural interval boundary for month-aligned schedules — analogous
    to '0' in the hour or minute field. This makes '@monthly' (0 0 1 * *) valid.
    """
    fields = expr.split()
    dom_index = 2 if len(fields) == 5 else 3
    return any(
        _field_has_offset(f, allow_one=(i == dom_index)) for i, f in enumerate(fields)
    )


IntervalExpression = Annotated[str, "5-field cron expression with no offset fields"]
"""
A subset of 5-field cron expressions that only allows interval-based scheduling with no offset.
Valid fields are limited to '*', '0', or '*/N', ensuring the schedule aligns to zero (e.g. '0 */2 * * *').
Intended to express interval frequency, not a specific point in time.

The day-of-month field additionally allows '1'. Since cron days are 1-indexed (there is no day 0),
'1' is the natural interval boundary — equivalent to '0' in hour/minute — and is what enables '@monthly'.

Valid:   '* * * * *', '0 * * * *', '0 */2 * * *', '0 */6 */2 * *', '0 0 1 * *'
Invalid: '0 2 * * *', '0 2/2 * * *', '5 * * * *', '0 */2 2 * *'
"""

INTERVAL_EXPRESSION_SHORTCUTS: dict[str, IntervalExpression] = {
    "@minutely": "* * * * *",
    "@minute": "* * * * *",
    "@hourly": "0 * * * *",
    "@hour": "0 * * * *",
    "@daily": "0 0 * * *",
    "@day": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@week": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@month": "0 0 1 * *",
}

IntervalExpressionExtended = Annotated[
    str, "6-field cron expression with no offset fields"
]
"""
A subset of 6-field cron expressions (second minute hour day month weekday) that only
allows interval-based scheduling with no offset. Extends IntervalExpression with a seconds field,
enabling sub-minute granularity.

The day-of-month field additionally allows '1'. Since cron days are 1-indexed (there is no day 0),
'1' is the natural interval boundary — equivalent to '0' in hour/minute — and is what enables '@monthly'.

Valid:   '* * * * * *', '0 * * * * *', '0 0 * * * *', '0 0 0 * * 0', '0 0 0 1 * *'
Invalid: '5 * * * * *', '0 2 * * * *'
"""

INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS: dict[str, IntervalExpressionExtended] = {
    "@secondly": "* * * * * *",
    "@second": "* * * * * *",
    "@minutely": "0 * * * * *",
    "@minute": "0 * * * * *",
    "@hourly": "0 0 * * * *",
    "@hour": "0 0 * * * *",
    "@daily": "0 0 0 * * *",
    "@day": "0 0 0 * * *",
    "@weekly": "0 0 0 * * 0",
    "@week": "0 0 0 * * 0",
    "@monthly": "0 0 0 1 * *",
    "@month": "0 0 0 1 * *",
}


@overload
def env_var_cron(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> str: ...


@overload
def env_var_cron(
    name: str,
    default: str | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> str | None: ...


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


@overload
def env_var_interval_expression(
    name: str,
    default: IntervalExpression | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> IntervalExpression: ...


@overload
def env_var_interval_expression(
    name: str,
    default: IntervalExpression | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> IntervalExpression | None: ...


def env_var_interval_expression(
    name: str,
    default: IntervalExpression | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> IntervalExpression | None:
    """
    Reads an IntervalExpression from an environment variable.

    Same as env_var_cron but additionally enforces no offset on any field,
    making it suitable for expressing interval frequency rather than a specific point in time.
    Accepts shortcut aliases from INTERVAL_EXPRESSION_SHORTCUTS (e.g. '@monthly').

    Raises ValueError if the value is not a valid cron expression, has an offset on any
    field, or if required is True and the variable is not set.
    """
    raw = os.environ.get(name)
    value = INTERVAL_EXPRESSION_SHORTCUTS.get(raw.lower(), raw) if raw else None
    if default is not None:
        default = INTERVAL_EXPRESSION_SHORTCUTS.get(default.lower(), default)
    if value is None:
        if default is not None:
            if has_offset(default):
                raise ValueError(
                    f"Environment variable '{name}' has a cron offset: '{default}'"
                )
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
    if has_offset(value):
        raise ValueError(f"Environment variable '{name}' has a cron offset: '{value}'")
    return value


@overload
def env_var_interval_expression_extended(
    name: str,
    default: IntervalExpressionExtended | None = ...,
    should_print_unset: bool = ...,
    *,
    required: Literal[True],
) -> IntervalExpressionExtended: ...


@overload
def env_var_interval_expression_extended(
    name: str,
    default: IntervalExpressionExtended | None = ...,
    should_print_unset: bool = ...,
    required: bool = ...,
) -> IntervalExpressionExtended | None: ...


def env_var_interval_expression_extended(
    name: str,
    default: IntervalExpressionExtended | None = None,
    should_print_unset: bool = True,
    required: bool = False,
) -> IntervalExpressionExtended | None:
    """
    Reads an IntervalExpressionExtended from an environment variable.

    Same as env_var_interval_expression but expects a 6-field expression
    (second minute hour day month weekday), enabling sub-minute granularity.

    Raises ValueError if the value is not a valid 6-field cron expression, has an offset
    on any field, or if required is True and the variable is not set.
    """
    raw = os.environ.get(name)
    value = (
        INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS.get(raw.lower(), raw) if raw else None
    )
    if default is not None:
        default = INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS.get(default.lower(), default)
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
