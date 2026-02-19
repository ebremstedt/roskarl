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
from roskarl.env import (
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
```python
value = env_var_dsn(name="DSN_VAR")
```
returns **`DSN`** object if value is a valid DSN string

needs to be formatted like this:
```
postgresql://username:password@hostname:5432/database_name
```