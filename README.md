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
    env_var_custom,
    env_var_duration,
    env_var_enum,
    env_var_interval_expression,
    env_var_interval_expression_extended,
    env_var_float,
    env_var_int,
    env_var_iso8601_datetime,
    env_var_list,
    env_var_log_level,
    env_var_path,
    env_var_rfc3339_datetime,
    env_var_secret,
    env_var_tz,
    env_var_url,
    env_var_dsn,
    DSN,
    Secret,
)
```

All functions return `None` if the variable is not set. An optional `default` parameter can be provided to return a fallback value instead.

Pass `required=True` to raise instead of returning `None` — type checkers will narrow the return type accordingly (e.g. `str` instead of `str | None`), so no `assert` is needed at callsites.

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
### cron (returns **`str`** if value is a valid cron expression)
```python
value = env_var_cron(name="CRON_VAR")
```

### interval expression (returns **`str`** if value is a valid offset-free 5-field cron expression)
```python
value = env_var_interval_expression(name="INTERVAL_VAR")
```

### interval expression extended (returns **`str`** if value is a valid offset-free 6-field cron expression)
```python
value = env_var_interval_expression_extended(name="INTERVAL_EXTENDED_VAR")
```

### datetime (ISO8601) (returns **`datetime`** if value is a valid ISO8601 datetime string — timezone is optional)
```python
value = env_var_iso8601_datetime(name="DATETIME_VAR")
```

### datetime (RFC3339) (returns **`datetime`** if value is a valid [RFC3339](https://www.rfc-editor.org/rfc/rfc3339) datetime string — timezone is required)
```python
value = env_var_rfc3339_datetime(name="DATETIME_VAR")
```

### url (returns **`str`** if value has a scheme + netloc, e.g. `https://example.com`)
```python
value = env_var_url(name="API_URL")
```

### secret (returns **`Secret`** — wraps the value so it can't accidentally be logged)
`repr()` and `str()` return `***`. Call `.reveal()` at the point of use.
```python
key = env_var_secret(name="API_KEY", required=True)
print(key)            # ***
stripe.api_key = key.reveal()
```

### path (returns **`pathlib.Path`**)
Pass `must_exist=True` to fail fast if the path is not present on disk.
```python
value = env_var_path(name="CONFIG_PATH", must_exist=True)
```

### enum (returns an instance of your `Enum` subclass)
Matches against each member's `.value`. Raises `ValueError` if no match.
```python
from enum import Enum
class Mode(Enum):
    LIVE = "live"
    DRY_RUN = "dry-run"

value = env_var_enum(name="MODE", enum_class=Mode, required=True)
```

### duration (returns **`timedelta`**)
Parses compound duration strings using suffixes `ms`, `s`, `m`, `h`, `d`. Spaces between parts are tolerated.
```python
value = env_var_duration(name="REQUEST_TIMEOUT", default=timedelta(seconds=30))
# accepts: "30s", "5m", "1h30m", "500ms", "7d", "1h 30m"
```

### log level (returns **`int`** matching Python's `logging` levels)
Accepts `DEBUG`, `INFO`, `WARNING`/`WARN`, `ERROR`, `CRITICAL`/`FATAL` (case-insensitive).
```python
import logging
level = env_var_log_level(name="LOG_LEVEL", default=logging.INFO)
logging.basicConfig(level=level)
```

### custom (returns whatever your parser returns)
Escape hatch for types without a dedicated helper — pass any `Callable[[str], T]`.
```python
from uuid import UUID
value = env_var_custom(name="UUID_VAR", parser=UUID, required=True)  # type: UUID
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

## Testing
Tests use `pytest`. Run the full suite:
```sh
pytest tests/
```

## Release

See [RELEASE.md](RELEASE.md) for instructions on how to publish a new version.

