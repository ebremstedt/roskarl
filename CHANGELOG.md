# Changelog

## 3.1.26 — 2026-05-19

### Breaking changes

- Renamed `BatchExpression` → `IntervalExpression`
- Renamed `BatchExpressionExtended` → `IntervalExpressionExtended`
- Renamed `env_var_batch_expression` → `env_var_interval_expression`
- Renamed `env_var_batch_expression_extended` → `env_var_interval_expression_extended`
- Renamed `BATCH_EXPRESSION_SHORTCUTS` → `INTERVAL_EXPRESSION_SHORTCUTS`
- Renamed `BATCH_EXPRESSION_EXTENDED_SHORTCUTS` → `INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS`

### New functions

- **`env_var_custom(name, parser, ...)`** — escape hatch for any `Callable[[str], T]` (UUID, Decimal, dataclasses, etc.). All other typed helpers now delegate to it.
- **`env_var_url`** — validates scheme + network location.
- **`env_var_secret`** — returns a `Secret` wrapper that masks itself in `repr()`/`str()`; call `.reveal()` at the point of use.
- **`env_var_path`** — returns `pathlib.Path`. Optional `must_exist=True` rejects missing paths (env value *and* default).
- **`env_var_enum(name, enum_class, ...)`** — validates against an `Enum` class by `.value`.
- **`env_var_log_level`** — returns the numeric `logging` level for `DEBUG`/`INFO`/`WARNING` (or `WARN`)/`ERROR`/`CRITICAL` (or `FATAL`), case-insensitive.
- **`env_var_duration`** — parses `"30s"`, `"5m"`, `"1h30m"`, `"500ms"`, `"7d"` → `timedelta`. Spaces tolerated.

### New types

- **`Secret`** — string wrapper. `repr()` → `Secret('***')`, `str()` → `***`. Raw value only available via `.reveal()`.

### New shortcut aliases

- `INTERVAL_EXPRESSION_SHORTCUTS` and `INTERVAL_EXPRESSION_EXTENDED_SHORTCUTS` now accept short forms alongside the `*ly` versions: `@minute`/`@minutely`, `@hour`/`@hourly`, `@day`/`@daily`, `@week`/`@weekly`, `@month`/`@monthly`. The extended dict additionally accepts `@second`/`@secondly`.

### Behavior changes

- **Defaults are now validated through the parser** for every function whose default type is broader than the validated contract: `env_var_tz`, `env_var_cron`, `env_var_interval_expression`, `env_var_interval_expression_extended`, `env_var_url`, and `env_var_path` (when `must_exist=True`). A misconfigured default now raises at startup rather than silently slipping through when the env var happens to be unset.

### Internal

- Centralized the unset/default/required/print plumbing in `env_var_custom`. All typed helpers shrunk to a one-line `return env_var_custom(name, parse, ...)` with a parser closure. ~60 lines of duplicate code removed across env.py and cron.py.
- Removed `roskarl/notify.py`. `print_unset` is now defined in `roskarl/env.py` (still publicly importable).

### Tests

- 190 tests pass (up from 106 at the start of these changes). New coverage:
  - `required=True` raises an error when unset, for every typed helper.
  - Empty-string-treated-as-unset.
  - `DSN.libpq_string`, `DSN.build_mssql_string`, `DSN.to_dict`.
  - Invalid-default raises for `tz`, `cron`, `interval_expression`, `interval_expression_extended`.
  - Full test classes for the seven new helpers (`url`, `secret`, `path`, `enum`, `log_level`, `duration`, `custom`).
