import roskarl
from roskarl.env import DSN
from roskarl.cron import IntervalExpression


class TestInit:
    def test_all_symbols_importable(self):
        for name in roskarl.__all__:
            assert hasattr(roskarl, name), f"{name} in __all__ but not importable"

    def test_all_symbols_in_all(self):
        expected = [
            "env_var_bool",
            "env_var_cron",
            "env_var_interval_expression",
            "env_var_float",
            "env_var_int",
            "env_var_list",
            "env_var",
            "env_var_tz",
            "env_var_dsn",
            "env_var_rfc3339_datetime",
            "env_var_iso8601_datetime",
            "DSN",
            "IntervalExpression",
        ]
        for name in expected:
            assert name in roskarl.__all__, f"{name} missing from __all__"

    def test_types_are_correct(self):
        assert isinstance(roskarl.IntervalExpression, type(IntervalExpression))
        assert isinstance(roskarl.DSN, type(DSN))
