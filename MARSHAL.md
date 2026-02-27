# Marshal

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
| `MODELS` | `list[str]` | Model names |
| `TAGS` | `list[str]` | Filter tags |
| `DEBUG` | `bool` | Debug run or not? |
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
from roskarl.marshal import with_env_config, EnvConfig

@with_env_config
def run(env: EnvConfig) -> None:
    run_pipeline(
        models=env.models,
        tags=env.tags,
        since=env.backfill.since,
        until=env.backfill.until,
    )

run()
```

### `get_execute_functions`

Loads `execute` functions from Python model files in a given folder, with optional filtering by model name or tag.

Raises `ValueError` if both `models` and `tags` are provided simultaneously.
```python
from roskarl.marshal import get_execute_functions

functions = get_execute_functions(folder="src/models", models=["orders", "customers"])
functions = get_execute_functions(folder="src/models", tags=["finance"])
```