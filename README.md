# Roskarl

Roskarl is a tiny module for environment variables.

## How to install

```sh
pip install roskarl
```

## Example usage

Single variable:

```python
from roskarl import get_env_var
since = get_env_var(var="SINCE")
until = get_env_var(var="UNTIL", optional=True)
```

List of strings
```python
tables_list = get_env_var(var="TABLES")
tables = get_list_of_strings(input=tables_list)
```