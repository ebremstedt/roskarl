# Roskarl

Is a **tiny** module for environment variables.

## Requires

Python 3.9.5

## How to install

```sh
pip install roskarl
```

## Example usage

```python
from roskarl.env import (
    env_var_bool,
    env_var_cron,
    env_var_float,
    env_var_int,
    env_var_list,
    env_var,
    env_var_tz,
    env_var_dsn,
    DSN
)
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

### tz
```python
value = env_var_tz(name="TZ_VAR")
```

### list
```python
value = env_var_list(name="LIST_VAR", separator="|")
```
returns **`list`** if value is splittable by separator

### int
```python
value = env_var_int(name="INT_VAR")
```
returns **`int`** if value is numeric

### float
```python
value = env_var_float(name="INT_VAR")
```
returns **`float`** if value is float

### cron
```python
value = env_var_cron(name="CRON_EXPRESSION_VAR")
```

### DSN

Note: if you use special characters in the password, these must be URL-encoded

```python
from urllib.parse import quote
password = 'My$ecret!Pass@2024'
encoded = quote(password, safe='')
print(encoded)  # My%24ecret%21Pass%402024 <--- use this
```

```python
value = env_var_dsn(name="DSN_VAR", type)
```
returns **`DSN`** object if value is like a dsn

needs to be formatted like this:
```
postgresql://username:password@hostname:5432/database_name
```
