[← README](../README.md)

# Cron

## `env_var_cron`

Accepts any valid 5-field cron expression.

## `env_var_cron_batch`

Rejects expressions with offsets — intended for expressing **batch frequency** rather than a specific point in time. Valid fields per position: `*`, `0`, or `*/N`.

| Expression    | Valid | Reason                       |
|---------------|-------|------------------------------|
| `0 */6 * * *` | yes   | every 6 hours                |
| `0 0 1 * *`   | yes   | every month (see note below) |
| `0 2 * * *`   | no    | offset hour (`2`)            |
| `5 * * * *`   | no    | offset minute (`5`)          |

### Shortcuts

Aliases can be passed directly as the env var value or as the `default` argument — they are resolved before validation.

| Alias        | Expression    |
|--------------|---------------|
| `@minutely`  | `* * * * *`   |
| `@hourly`    | `0 * * * *`   |
| `@daily`     | `0 0 * * *`   |
| `@weekly`    | `0 0 * * 0`   |
| `@monthly`   | `0 0 1 * *`   |

```python
from roskarl.cron import CRON_BATCH_SHORTCUTS
```

## `env_var_cron_batch_extended`

Same as `env_var_cron_batch` but expects a **6-field** expression (`second minute hour day month weekday`), enabling sub-minute granularity.

### Shortcuts

Aliases can be passed directly as the env var value or as the `default` argument — they are resolved before validation.

| Alias        | Expression      |
|--------------|-----------------|
| `@secondly`  | `* * * * * *`   |
| `@minutely`  | `0 * * * * *`   |
| `@hourly`    | `0 0 * * * *`   |
| `@daily`     | `0 0 0 * * *`   |
| `@weekly`    | `0 0 0 * * 0`   |
| `@monthly`   | `0 0 0 1 * *`   |

```python
from roskarl.cron import CRON_BATCH_EXTENDED_SHORTCUTS
```

## Note on monthly

`@monthly` uses `1` in the day-of-month field, which is accepted even though it looks like an offset. Cron days are **1-indexed** — there is no day `0` — so `1` is the natural interval boundary, equivalent to `0` in the hour or minute field. Any value greater than `1` in the day-of-month field is still rejected.
