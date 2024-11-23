# Roskarl

Is a **tiny** module for environment variables.

## How to install

```sh
pip install roskarl
```

## Example usage

```python
from roskarl import env_var
```

### str
```python
value = env_var(var="STR_VAR")
```
returns **`str`**

### bool
```python
value = env_var(var="BOOL_VAR", type_=bool)
```
returns **`bool`** if environment variable value uppercase is `TRUE` or `FALSE`

### list
```python
value = env_var(var="LIST_VAR", type_=list, separator="|")
```
returns **`list`** if value is splittable by separator

### int
```python
value = env_var(var="INT_VAR", type_=int)
```
returns **`int`** if value is numeric
