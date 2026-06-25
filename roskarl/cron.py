from typing import Annotated, Literal, overload
from icron import croniter
from roskarl.env import env_var_custom


def _field_kind(field: str, *, ones_allowed: bool) -> str:
    """Classify one cron field for interval-expression validation:

    'open'   — '*': no constraint on this field.
    'closed' — '*/N' (a step), or the field's natural zero boundary: '0', or
               '1' for the 1-indexed day-of-month / month fields (which have no
               zero). Constrains the field but still aligns to the period start.
    'offset' — anything else (a specific point, e.g. '2' or '2/2') — anchors to
               a moment rather than expressing a frequency.
    """
    if field == "*":
        return "open"
    if field.startswith("*/"):
        return "closed"
    if field == "0" or (ones_allowed and field == "1"):
        return "closed"
    return "offset"


def has_offset(expr: str) -> bool:
    """
    Returns True if the cron expression anchors to a specific point in time
    rather than expressing a zero-aligned interval frequency.

    An expression is offset-free when both hold:

    1. Per field: every field is '*', '*/N', or its natural zero boundary — '0'
       for the 0-indexed second/minute/hour/weekday fields, and '1' for the
       1-indexed day-of-month and month fields (which have no zero). That '1'
       boundary is what makes '@monthly' (0 0 1 * *) and '@yearly' (0 0 1 1 *)
       valid; '0' is the boundary on second/minute/hour.

    2. Contiguous from the finest field up: in the second→month hierarchy, once a
       field is fully open ('*'), every coarser field must be open too. You can't
       pin a coarse field while a finer one is wild — e.g. '0 0 * 1 *' ("every
       day, but only in January") is not an interval. Day-of-week is an orthogonal
       axis (it carries the weekly alignment) and is exempt from the hierarchy.
    """
    fields = expr.split()
    # second minute hour dom month dow (6-field) | minute hour dom month dow (5)
    dom_index = 3 if len(fields) == 6 else 2
    month_index = dom_index + 1

    # 1) every field must be a zero-aligned boundary, a step, or open.
    for i, field in enumerate(fields):
        ones_allowed = i in (dom_index, month_index)
        if _field_kind(field, ones_allowed=ones_allowed) == "offset":
            return True

    # 2) the constrained fields must be contiguous from the finest up — once a
    #    field opens up, nothing coarser (through month) may be pinned/stepped.
    #    Day-of-week (the last field) is excluded: it's a separate axis.
    seen_open = False
    for i in range(month_index + 1):
        if fields[i] == "*":
            seen_open = True
        elif seen_open:
            return True
    return False


IntervalExpression = Annotated[str, "5-field cron expression with no offset fields"]
"""
A subset of 5-field cron expressions that only express a zero-aligned interval frequency,
not a specific point in time. Each field must be '*', '*/N', or its natural zero boundary
('0', or '1' for the 1-indexed day-of-month and month fields, which have no zero). The
constrained fields must also be contiguous from the finest up: once a field is '*', every
coarser field must be too (day-of-week is exempt — it carries the weekly alignment).

The '1' boundary on day-of-month and month is what enables '@monthly' (0 0 1 * *) and
'@yearly' (0 0 1 1 *); '0' is the boundary on minute/hour.

Valid:   '* * * * *', '0 * * * *', '0 */2 * * *', '0 */6 */2 * *', '0 0 1 * *', '0 0 1 1 *'
Invalid: '0 2 * * *', '0 2/2 * * *', '5 * * * *', '0 */2 2 * *', '0 0 * 1 *'
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
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
}

IntervalExpressionExtended = Annotated[
    str, "6-field cron expression with no offset fields"
]
"""
A subset of 6-field cron expressions (second minute hour day month weekday) that only express
a zero-aligned interval frequency. Same rules as IntervalExpression with an added seconds field
for sub-minute granularity: each field is '*', '*/N', or its zero boundary ('0', or '1' for the
1-indexed day-of-month / month fields), and the constrained fields are contiguous from seconds up
(day-of-week exempt).

The '1' boundary on day-of-month and month is what enables '@monthly' (0 0 0 1 * *) and
'@yearly' (0 0 0 1 1 *).

Valid:   '* * * * * *', '0 * * * * *', '0 0 * * * *', '0 0 0 * * 0', '0 0 0 1 * *', '0 0 0 1 1 *'
Invalid: '5 * * * * *', '0 2 * * * *', '0 0 0 * 1 *'
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
    "@yearly": "0 0 0 1 1 *",
    "@annually": "0 0 0 1 1 *",
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

    def parse(value: str) -> str:
        if not croniter.is_valid(expression=value):
            raise ValueError(
                f"Environment variable '{name}' is not a valid cron expression."
            )
        return value

    if default is not None:
        default = parse(default)

    return env_var_custom(name, parse, default, should_print_unset, required)


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

    def parse(value: str) -> IntervalExpression:
        resolved = INTERVAL_EXPRESSION_SHORTCUTS.get(value.lower(), value)
        if not croniter.is_valid(expression=resolved):
            raise ValueError(
                f"Environment variable '{name}' is not a valid cron expression."
            )
        if has_offset(resolved):
            raise ValueError(
                f"Environment variable '{name}' has a cron offset: '{resolved}'"
            )
        return resolved

    if default is not None:
        default = parse(default)

    return env_var_custom(name, parse, default, should_print_unset, required)


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

    def parse(value: str) -> IntervalExpressionExtended:
        resolved = INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS.get(value.lower(), value)
        if len(resolved.split()) != 6:
            raise ValueError(
                f"Environment variable '{name}' must be a 6-field cron expression."
            )
        if not croniter.is_valid(expression=resolved):
            raise ValueError(
                f"Environment variable '{name}' is not a valid cron expression."
            )
        if has_offset(resolved):
            raise ValueError(
                f"Environment variable '{name}' has a cron offset: '{resolved}'"
            )
        return resolved

    if default is not None:
        default = parse(default)

    return env_var_custom(name, parse, default, should_print_unset, required)
