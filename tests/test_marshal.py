import pytest
from datetime import datetime
from unittest.mock import patch
from roskarl.marshal import load_env_config


def test_default_all_disabled():
    with patch.dict("os.environ", {}, clear=True):
        env = load_env_config()
        assert env.cron.enabled is False
        assert env.backfill.enabled is False
        assert env.model_name is None
        assert env.cron.expression is None
        assert env.cron.since is None
        assert env.cron.until is None
        assert env.backfill.since is None
        assert env.backfill.until is None
        assert env.backfill.batch_size is None


def test_cron_enabled_resolves_interval():
    env_vars = {
        "CRON_ENABLED": "true",
        "CRON_EXPRESSION": "0 * * * *",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        env = load_env_config()
        assert env.cron.enabled is True
        assert env.cron.expression == "0 * * * *"
        assert isinstance(env.cron.since, datetime)
        assert isinstance(env.cron.until, datetime)
        assert env.cron.since < env.cron.until


def test_cron_interval_is_one_period_apart():
    env_vars = {
        "CRON_ENABLED": "true",
        "CRON_EXPRESSION": "0 * * * *",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        env = load_env_config()
        delta = env.cron.until - env.cron.since
        assert delta.total_seconds() == 3600


def test_backfill_enabled():
    env_vars = {
        "BACKFILL_ENABLED": "true",
        "BACKFILL_SINCE": "2026-01-01T00:00:00+00:00",
        "BACKFILL_UNTIL": "2026-02-01T00:00:00+00:00",
        "BACKFILL_BATCH_SIZE": "100",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        env = load_env_config()
        assert env.backfill.enabled is True
        assert isinstance(env.backfill.since, datetime)
        assert isinstance(env.backfill.until, datetime)
        assert env.backfill.batch_size == 100


def test_both_enabled_raises():
    env_vars = {
        "CRON_ENABLED": "true",
        "CRON_EXPRESSION": "0 * * * *",
        "BACKFILL_ENABLED": "true",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        with pytest.raises(
            ValueError, match="CRON_ENABLED and BACKFILL_ENABLED cannot both be true"
        ):
            load_env_config()


def test_model_name():
    with patch.dict("os.environ", {"MODEL_NAME": "my-model"}, clear=True):
        env = load_env_config()
        assert env.model_name == "my-model"


def test_cron_disabled_no_interval():
    with patch.dict("os.environ", {"CRON_ENABLED": "false"}, clear=True):
        env = load_env_config()
        assert env.cron.enabled is False
        assert env.cron.since is None
        assert env.cron.until is None


def test_backfill_disabled_no_dates():
    with patch.dict("os.environ", {"BACKFILL_ENABLED": "false"}, clear=True):
        env = load_env_config()
        assert env.backfill.enabled is False
        assert env.backfill.since is None
        assert env.backfill.until is None
        assert env.backfill.batch_size is None


def test_daily_cron_interval_is_24h():
    env_vars = {
        "CRON_ENABLED": "true",
        "CRON_EXPRESSION": "0 0 * * *",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        env = load_env_config()
        delta = env.cron.until - env.cron.since
        assert delta.total_seconds() == 86400
