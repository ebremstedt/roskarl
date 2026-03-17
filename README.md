# Roskarl

Is a **tiny** module for environment variables

## Requires

Python 3.11.0+

## How to install
```sh
uv pip install roskarl
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

### str (returns **`str`**)
```python
value = env_var(name="STR_VAR", default="fallback")
```

### bool (returns **`bool`** — accepts `true` or `false` (case insensitive))
```python
value = env_var_bool(name="BOOL_VAR")
```

### tz (returns **`str`** if value is a valid IANA timezone (e.g. `Europe/Stockholm`))
```python
value = env_var_tz(name="TZ_VAR")
```

### list (returns **`list[str]`** if value is splittable by separator)
```python
value = env_var_list(name="LIST_VAR", separator="|")
```

### int (returns **`int`** if value is numeric)
```python
value = env_var_int(name="INT_VAR")
```

### float (returns **`float`** if value is a float)
```python
value = env_var_float(name="FLOAT_VAR")
```
### cron — [full docs](docs/cron.md) (returns **`str`** if value is a valid cron expression)
```python
value = env_var_cron(name="CRON_EXPRESSION_VAR")
```

### datetime (ISO8601) (returns **`datetime`** if value is a valid ISO8601 datetime string — timezone is optional)
```python
value = env_var_iso8601_datetime(name="DATETIME_VAR")
```

### datetime (RFC3339) (returns **`datetime`** if value is a valid [RFC3339](https://www.rfc-editor.org/rfc/rfc3339) datetime string — timezone is required)
```python
value = env_var_rfc3339_datetime(name="DATETIME_VAR")
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
