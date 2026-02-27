import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from roskarl.marshal import (
    load_env_config,
    with_env_config,
    EnvConfig,
    get_execute_functions,
)


def test_defaults_all_disabled():
    with (
        patch("roskarl.marshal.env_var_bool", return_value=False),
        patch("roskarl.marshal.env_var_list", return_value=None),
    ):
        config = load_env_config()

    assert config.models is None
    assert config.tags is None
    assert config.cron.enabled is False
    assert config.cron.expression is None
    assert config.cron.since is None
    assert config.cron.until is None
    assert config.backfill.enabled is False
    assert config.backfill.since is None
    assert config.backfill.until is None
    assert config.backfill.batch_size is None


def test_cron_and_backfill_both_enabled_raises():
    with patch("roskarl.marshal.env_var_bool", return_value=True):
        with pytest.raises(
            ValueError, match="CRON_ENABLED and BACKFILL_ENABLED cannot both be true"
        ):
            load_env_config()


def test_cron_enabled_resolves_interval():
    mock_dt = datetime(2024, 1, 15, 12, 0, 0)

    def mock_bool(name):
        return name == "CRON_ENABLED"

    with (
        patch("roskarl.marshal.env_var_bool", side_effect=mock_bool),
        patch("roskarl.marshal.env_var_list", return_value=None),
        patch("roskarl.marshal.env_var_cron", return_value="0 3 * * *"),
        patch(
            "roskarl.marshal._resolve_cron_interval", return_value=(mock_dt, mock_dt)
        ) as mock_resolve,
    ):
        config = load_env_config()

    mock_resolve.assert_called_once_with("0 3 * * *")
    assert config.cron.enabled is True
    assert config.cron.expression == "0 3 * * *"
    assert config.cron.since == mock_dt
    assert config.cron.until == mock_dt


def test_cron_disabled_skips_expression():
    with (
        patch("roskarl.marshal.env_var_bool", return_value=False),
        patch("roskarl.marshal.env_var_list", return_value=None),
    ):
        config = load_env_config()

    assert config.cron.expression is None
    assert config.cron.since is None
    assert config.cron.until is None


def test_backfill_enabled_reads_fields():
    mock_dt = datetime(2024, 1, 1, 0, 0, 0)

    def mock_bool(name):
        return name == "BACKFILL_ENABLED"

    with (
        patch("roskarl.marshal.env_var_bool", side_effect=mock_bool),
        patch("roskarl.marshal.env_var_list", return_value=None),
        patch("roskarl.marshal.env_var_iso8601_datetime", return_value=mock_dt),
        patch("roskarl.marshal.env_var_int", return_value=7),
    ):
        config = load_env_config()

    assert config.backfill.enabled is True
    assert config.backfill.since == mock_dt
    assert config.backfill.until == mock_dt
    assert config.backfill.batch_size == 7


def test_backfill_disabled_skips_fields():
    with (
        patch("roskarl.marshal.env_var_bool", return_value=False),
        patch("roskarl.marshal.env_var_list", return_value=None),
    ):
        config = load_env_config()

    assert config.backfill.since is None
    assert config.backfill.until is None
    assert config.backfill.batch_size is None


def test_models_and_tags_populated():
    with (
        patch("roskarl.marshal.env_var_bool", return_value=False),
        patch(
            "roskarl.marshal.env_var_list",
            side_effect=lambda name: {
                "MODELS": ["orders", "customers"],
                "TAGS": ["finance", "critical"],
            }.get(name),
        ),
    ):
        config = load_env_config()

    assert config.models == ["orders", "customers"]
    assert config.tags == ["finance", "critical"]


def test_models_none_tags_set():
    with (
        patch("roskarl.marshal.env_var_bool", return_value=False),
        patch(
            "roskarl.marshal.env_var_list",
            side_effect=lambda name: {
                "TAGS": ["finance"],
            }.get(name),
        ),
    ):
        config = load_env_config()

    assert config.models is None
    assert config.tags == ["finance"]


def test_resolve_cron_interval_returns_two_datetimes():
    from roskarl.marshal import _resolve_cron_interval

    since, until = _resolve_cron_interval("0 3 * * *")
    assert isinstance(since, datetime)
    assert isinstance(until, datetime)
    assert since <= until


def test_with_env_config_decorator():
    mock_config = MagicMock()

    with patch("roskarl.marshal.load_env_config", return_value=mock_config):
        handler = MagicMock()
        wrapped = with_env_config(handler)
        wrapped()

    handler.assert_called_once_with(mock_config)


def test_with_env_config_preserves_name():
    def my_pipeline(env: EnvConfig) -> None:
        pass

    wrapped = with_env_config(my_pipeline)
    assert wrapped.__name__ == "my_pipeline"


def test_raises_when_both_models_and_tags_set():
    with pytest.raises(ValueError):
        get_execute_functions(models=["my_model"], tags=["finance"])


def test_returns_empty_when_no_files(tmp_path):
    result = get_execute_functions(folder=str(tmp_path))
    assert result == []


def test_loads_all_execute_functions(tmp_path):
    for name in ["model_a", "model_b"]:
        (tmp_path / f"{name}.py").write_text("def execute(): pass")

    result = get_execute_functions(folder=str(tmp_path))
    assert len(result) == 2


def test_filters_by_models(tmp_path):
    (tmp_path / "model_a.py").write_text("def execute(): pass")
    (tmp_path / "model_b.py").write_text("def execute(): pass")

    result = get_execute_functions(folder=str(tmp_path), models=["model_a"])
    assert len(result) == 1


def test_filters_by_tags(tmp_path):
    (tmp_path / "tagged.py").write_text("TAGS = ['finance']\ndef execute(): pass")
    (tmp_path / "untagged.py").write_text("def execute(): pass")

    result = get_execute_functions(folder=str(tmp_path), tags=["finance"])
    assert len(result) == 1


def test_tag_filter_no_match(tmp_path):
    (tmp_path / "model_a.py").write_text("TAGS = ['ops']\ndef execute(): pass")

    result = get_execute_functions(folder=str(tmp_path), tags=["finance"])
    assert result == []


def test_models_filter_no_match(tmp_path):
    (tmp_path / "model_a.py").write_text("def execute(): pass")

    result = get_execute_functions(folder=str(tmp_path), models=["model_b"])
    assert result == []


def test_returns_callable_execute_functions(tmp_path):
    (tmp_path / "model_a.py").write_text("def execute(): pass")

    result = get_execute_functions(folder=str(tmp_path))
    assert all(callable(f) for f in result)
