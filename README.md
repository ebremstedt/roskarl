# Roskarl

Is a **tiny** module for environment variables.

## Requires

Python 3.11.0+

## How to install
```sh
pip install roskarl
```

## Example usage
```python
from roskarl import (
    env_var,
    env_var_bool,
    env_var_cron,
    env_var_float,
    env_var_int,
    env_var_iso8601_datetime,
    env_var_list,
    env_var_rfc3339_datetime,
    env_var_tz,
    env_var_dsn,
    DSN
)
```

All functions return `None` if the variable is not set. An optional `default` parameter can be provided to return a fallback value instead.
```python
value = env_var(name="STR_VAR", default="fallback")
```

### str
```python
value = env_var(name="STR_VAR")
```
returns **`str`**

### bool
```python
value = env_var_bool(name="BOOL_VAR")
```
returns **`bool`** — accepts `true` or `false` (case insensitive)

### tz
```python
value = env_var_tz(name="TZ_VAR")
```
returns **`str`** if value is a valid IANA timezone (e.g. `Europe/Stockholm`)

### list
```python
value = env_var_list(name="LIST_VAR", separator="|")
```
returns **`list[str]`** if value is splittable by separator

### int
```python
value = env_var_int(name="INT_VAR")
```
returns **`int`** if value is numeric

### float
```python
value = env_var_float(name="FLOAT_VAR")
```
returns **`float`** if value is a float

### cron
```python
value = env_var_cron(name="CRON_EXPRESSION_VAR")
```
returns **`str`** if value is a valid cron expression

### datetime (ISO8601)
```python
value = env_var_iso8601_datetime(name="DATETIME_VAR")
```
returns **`datetime`** if value is a valid ISO8601 datetime string — timezone is optional
```
2026-01-01T00:00:00
2026-01-01T00:00:00+00:00
```

### datetime (RFC3339)
```python
value = env_var_rfc3339_datetime(name="DATETIME_VAR")
```
returns **`datetime`** if value is a valid [RFC3339](https://www.rfc-editor.org/rfc/rfc3339) datetime string — timezone is required
```
2026-01-01T00:00:00+00:00
```

### DSN

> **Note:** Special characters in passwords must be URL-encoded.

```python
from urllib.parse import quote
password = 'My$ecret!Pass@2024'
encoded = quote(password, safe='')
print(encoded)  # My%24ecret%21Pass%402024 <--- use this
```

```python
value = env_var_dsn(name="DSN_VAR")
```
returns **`DSN`** object if value is a valid DSN string, formatted as:
```
postgresql://username:password@hostname:5432/database_name
```

The `DSN` object exposes the following attributes:

| Attribute  | Type  | Example              |
|------------|-------|----------------------|
| `scheme`   | `str` | `postgresql`         |
| `host`     | `str` | `hostname`           |
| `port`     | `int` | `5432`               |
| `username` | `str` | `username`           |
| `password` | `str` | `password`           |
| `database` | `str` | `database_name`      |

---

## Marshal

Marshals environment variables into typed configuration objects. Requires `croniter`:
```sh
pip install croniter
```

```python
from roskarl.marshal import load_env_config

env = load_env_config()
```

Raises `ValueError` if both `CRON_ENABLED` and `BACKFILL_ENABLED` are `true`.

### Env vars

| Env var | Type | Description |
|---|---|---|
| `MODEL_NAME` | `str` | Model name |
| `CRON_ENABLED` | `bool` | Enable cron mode |
| `CRON_EXPRESSION` | `str` | Valid cron expression |
| `BACKFILL_ENABLED` | `bool` | Enable backfill mode |
| `BACKFILL_SINCE` | `datetime` | ISO8601 UTC datetime |
| `BACKFILL_UNTIL` | `datetime` | ISO8601 UTC datetime |
| `BACKFILL_BATCH_SIZE` | `int` | Batch size |

### CronConfig

`since` and `until` are derived from `CRON_EXPRESSION` based on the latest fully elapsed interval — e.g. `0 * * * *` at 14:35 → `since=13:00, until=14:00`.

### BackfillConfig

`since` and `until` read from env as ISO8601 UTC datetimes. `CRON_ENABLED` and `BACKFILL_ENABLED` are mutually exclusive.

### `with_env_config`

A decorator that calls `load_env_config()` and injects the result as the first argument. Useful for pipeline entrypoints.

```python
from roskarl.decorators import with_env_config
from roskarl.marshal import EnvConfig

@with_env_config
def run(env: EnvConfig) -> None:
    if env.backfill.enabled:
        run_backfill(
            model=env.model_name,
            since=env.backfill.since,
            until=env.backfill.until,
            batch_size=env.backfill.batch_size,
        )
    else:
        run_incremental(
            model=env.model_name,
            since=env.cron.since,
            until=env.cron.until,
        )

run()
```