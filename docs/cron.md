[← README](../README.md)

# Cron

## `env_var_cron`

Accepts any valid 5-field cron expression.

## `env_var_interval_expression`

Rejects expressions with offsets — intended for expressing **interval frequency** rather than a specific point in time. Valid fields per position: `*`, `0`, or `*/N`.

| Expression    | Valid | Reason                       |
|---------------|-------|------------------------------|
| `0 */6 * * *` | yes   | every 6 hours                |
| `0 0 1 * *`   | yes   | every month (see note below) |
| `0 2 * * *`   | no    | offset hour (`2`)            |
| `5 * * * *`   | no    | offset minute (`5`)          |

### Shortcuts

Aliases can be passed directly as the env var value or as the `default` argument — they are resolved before validation.

| Alias                     | Expression    |
|---------------------------|---------------|
| `@minutely` / `@minute`   | `* * * * *`   |
| `@hourly` / `@hour`       | `0 * * * *`   |
| `@daily` / `@day`         | `0 0 * * *`   |
| `@weekly` / `@week`       | `0 0 * * 0`   |
| `@monthly` / `@month`     | `0 0 1 * *`   |

```python
from roskarl.cron import INTERVAL_EXPRESSION_SHORTCUTS
```

## `env_var_interval_expression_extended`

Same as `env_var_interval_expression` but expects a **6-field** expression (`second minute hour day month weekday`), enabling sub-minute granularity.

### Shortcuts

Aliases can be passed directly as the env var value or as the `default` argument — they are resolved before validation.

| Alias                     | Expression      |
|---------------------------|-----------------|
| `@secondly` / `@second`   | `* * * * * *`   |
| `@minutely` / `@minute`   | `0 * * * * *`   |
| `@hourly` / `@hour`       | `0 0 * * * *`   |
| `@daily` / `@day`         | `0 0 0 * * *`   |
| `@weekly` / `@week`       | `0 0 0 * * 0`   |
| `@monthly` / `@month`     | `0 0 0 1 * *`   |

```python
from roskarl.cron import INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS
```

## Note on monthly

`@monthly` uses `1` in the day-of-month field, which is accepted even though it looks like an offset. Cron days are **1-indexed** — there is no day `0` — so `1` is the natural interval boundary, equivalent to `0` in the hour or minute field. Any value greater than `1` in the day-of-month field is still rejected.
