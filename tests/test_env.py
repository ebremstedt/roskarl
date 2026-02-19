import os
import unittest
from datetime import datetime, timezone

from roskarl import (
    env_var,
    env_var_cron,
    env_var_tz,
    env_var_list,
    env_var_bool,
    env_var_int,
    env_var_float,
    env_var_iso8601_datetime,
    env_var_rfc3339_datetime,
    env_var_dsn,
    DSN,
)


class TestEnvVarUtils(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    # env_var
    def test_env_var_str_set(self):
        os.environ["TEST_STR"] = "hello"
        self.assertEqual(env_var("TEST_STR"), "hello")

    def test_env_var_not_set_returns_none(self):
        self.assertIsNone(env_var("TEST_STR"))

    def test_env_var_not_set_returns_default(self):
        self.assertEqual(env_var("TEST_STR", default="fallback"), "fallback")

    # env_var_cron
    def test_env_var_cron_valid(self):
        os.environ["TEST_CRON"] = "0 0 * * *"
        self.assertEqual(env_var_cron("TEST_CRON"), "0 0 * * *")

    def test_env_var_cron_invalid(self):
        os.environ["TEST_CRON"] = "invalid cron"
        with self.assertRaises(ValueError) as context:
            env_var_cron("TEST_CRON")
        self.assertIn("Value is not a valid cron expression.", str(context.exception))

    def test_env_var_cron_not_set_returns_none(self):
        self.assertIsNone(env_var_cron("TEST_CRON"))

    def test_env_var_cron_not_set_returns_default(self):
        self.assertEqual(env_var_cron("TEST_CRON", default="0 * * * *"), "0 * * * *")

    # env_var_tz
    def test_env_var_tz_valid(self):
        os.environ["TEST_TZ"] = "America/New_York"
        self.assertEqual(env_var_tz("TEST_TZ"), "America/New_York")

    def test_env_var_tz_invalid(self):
        os.environ["TEST_TZ"] = "Invalid/Timezone"
        with self.assertRaises(ValueError) as context:
            env_var_tz("TEST_TZ")
        self.assertIn("Timezone string was not valid", str(context.exception))

    def test_env_var_tz_not_set_returns_none(self):
        self.assertIsNone(env_var_tz("TEST_TZ"))

    def test_env_var_tz_not_set_returns_default(self):
        self.assertEqual(env_var_tz("TEST_TZ", default="UTC"), "UTC")

    # env_var_list
    def test_env_var_list_default_separator(self):
        os.environ["TEST_LIST"] = "a, b, c"
        self.assertEqual(env_var_list("TEST_LIST"), ["a", "b", "c"])

    def test_env_var_list_custom_separator(self):
        os.environ["TEST_LIST"] = "a;b;c"
        self.assertEqual(env_var_list("TEST_LIST", separator=";"), ["a", "b", "c"])

    def test_env_var_list_not_set_returns_none(self):
        self.assertIsNone(env_var_list("TEST_LIST"))

    def test_env_var_list_not_set_returns_default(self):
        self.assertEqual(env_var_list("TEST_LIST", default=["x", "y"]), ["x", "y"])

    def test_env_var_list_single_item(self):
        os.environ["TEST_LIST"] = "only"
        self.assertEqual(env_var_list("TEST_LIST"), ["only"])

    # env_var_bool
    def test_env_var_bool_true(self):
        os.environ["TEST_BOOL"] = "TRUE"
        self.assertTrue(env_var_bool("TEST_BOOL"))
        os.environ["TEST_BOOL"] = "true"
        self.assertTrue(env_var_bool("TEST_BOOL"))

    def test_env_var_bool_false(self):
        os.environ["TEST_BOOL"] = "FALSE"
        self.assertFalse(env_var_bool("TEST_BOOL"))
        os.environ["TEST_BOOL"] = "false"
        self.assertFalse(env_var_bool("TEST_BOOL"))

    def test_env_var_bool_invalid(self):
        os.environ["TEST_BOOL"] = "not-a-bool"
        with self.assertRaises(ValueError) as context:
            env_var_bool("TEST_BOOL")
        self.assertIn("Bool must be set to true or false", str(context.exception))

    def test_env_var_bool_not_set_returns_none(self):
        self.assertIsNone(env_var_bool("TEST_BOOL"))

    def test_env_var_bool_not_set_returns_default(self):
        self.assertTrue(env_var_bool("TEST_BOOL", default=True))

    # env_var_int
    def test_env_var_int(self):
        os.environ["TEST_INT"] = "42"
        self.assertEqual(env_var_int("TEST_INT"), 42)

    def test_env_var_int_invalid(self):
        os.environ["TEST_INT"] = "not-an-int"
        with self.assertRaises(ValueError):
            env_var_int("TEST_INT")

    def test_env_var_int_not_set_returns_none(self):
        self.assertIsNone(env_var_int("TEST_INT"))

    def test_env_var_int_not_set_returns_default(self):
        self.assertEqual(env_var_int("TEST_INT", default=99), 99)

    def test_env_var_int_negative(self):
        os.environ["TEST_INT"] = "-10"
        self.assertEqual(env_var_int("TEST_INT"), -10)

    # env_var_float
    def test_env_var_float(self):
        os.environ["TEST_FLOAT"] = "3.14"
        self.assertEqual(env_var_float("TEST_FLOAT"), 3.14)

    def test_env_var_float_invalid(self):
        os.environ["TEST_FLOAT"] = "not-a-float"
        with self.assertRaises(ValueError):
            env_var_float("TEST_FLOAT")

    def test_env_var_float_not_set_returns_none(self):
        self.assertIsNone(env_var_float("TEST_FLOAT"))

    def test_env_var_float_not_set_returns_default(self):
        self.assertEqual(env_var_float("TEST_FLOAT", default=1.5), 1.5)

    def test_env_var_float_negative(self):
        os.environ["TEST_FLOAT"] = "-2.71"
        self.assertEqual(env_var_float("TEST_FLOAT"), -2.71)

    # env_var_iso8601_datetime
    def test_env_var_iso8601_datetime_valid_with_tz(self):
        os.environ["TEST_DT"] = "2026-01-01T00:00:00+00:00"
        result = env_var_iso8601_datetime("TEST_DT")
        self.assertEqual(result, datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_env_var_iso8601_datetime_valid_without_tz(self):
        os.environ["TEST_DT"] = "2026-01-01T00:00:00"
        result = env_var_iso8601_datetime("TEST_DT")
        self.assertEqual(result, datetime(2026, 1, 1))

    def test_env_var_iso8601_datetime_invalid(self):
        os.environ["TEST_DT"] = "not-a-datetime"
        with self.assertRaises(ValueError) as context:
            env_var_iso8601_datetime("TEST_DT")
        self.assertIn("is not a valid ISO8601 datetime string", str(context.exception))

    def test_env_var_iso8601_datetime_not_set_returns_none(self):
        self.assertIsNone(env_var_iso8601_datetime("TEST_DT"))

    def test_env_var_iso8601_datetime_not_set_returns_default(self):
        default = datetime(2025, 1, 1)
        self.assertEqual(env_var_iso8601_datetime("TEST_DT", default=default), default)

    # env_var_rfc3339_datetime
    def test_env_var_rfc3339_datetime_valid(self):
        os.environ["TEST_DT"] = "2026-01-01T00:00:00+00:00"
        result = env_var_rfc3339_datetime("TEST_DT")
        self.assertEqual(result, datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_env_var_rfc3339_datetime_invalid(self):
        os.environ["TEST_DT"] = "not-a-datetime"
        with self.assertRaises(ValueError) as context:
            env_var_rfc3339_datetime("TEST_DT")
        self.assertIn("is not a valid RFC3339 datetime string", str(context.exception))

    def test_env_var_rfc3339_datetime_missing_tz(self):
        os.environ["TEST_DT"] = "2026-01-01T00:00:00"
        with self.assertRaises(ValueError) as context:
            env_var_rfc3339_datetime("TEST_DT")
        self.assertIn("missing timezone info", str(context.exception))

    def test_env_var_rfc3339_datetime_not_set_returns_none(self):
        self.assertIsNone(env_var_rfc3339_datetime("TEST_DT"))

    def test_env_var_rfc3339_datetime_not_set_returns_default(self):
        default = datetime(2025, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(env_var_rfc3339_datetime("TEST_DT", default=default), default)

    # env_var_dsn
    def test_env_var_dsn_valid_full(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432/mydb"
        result = env_var_dsn("TEST_DSN")
        self.assertIsInstance(result, DSN)
        self.assertEqual(result.protocol, "postgresql")
        self.assertEqual(result.username, "user")
        self.assertEqual(result.password, "password")
        self.assertEqual(result.hostname, "localhost")
        self.assertEqual(result.port, 5432)
        self.assertEqual(result.database, "mydb")

    def test_env_var_dsn_valid_no_port(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost/mydb"
        result = env_var_dsn("TEST_DSN")
        self.assertIsNone(result.port)

    def test_env_var_dsn_valid_no_database(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432"
        result = env_var_dsn("TEST_DSN")
        self.assertIsNone(result.database)

    def test_env_var_dsn_connection_string(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432/mydb"
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(
            result.connection_string, "postgresql://user:password@localhost:5432/mydb"
        )

    def test_env_var_dsn_str_masks_password(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432/mydb"
        result = env_var_dsn("TEST_DSN")
        self.assertIn("****", str(result))
        self.assertNotIn("password", str(result))

    def test_env_var_dsn_invalid(self):
        os.environ["TEST_DSN"] = "not-a-dsn"
        with self.assertRaises(ValueError):
            env_var_dsn("TEST_DSN")

    def test_env_var_dsn_not_set_returns_none(self):
        self.assertIsNone(env_var_dsn("TEST_DSN"))

    def test_env_var_dsn_not_set_returns_default(self):
        default = DSN(
            protocol="postgresql", username="u", password="p", hostname="localhost"
        )
        self.assertEqual(env_var_dsn("TEST_DSN", default=default), default)

    def test_env_var_dsn_url_encoded_credentials(self):
        os.environ["TEST_DSN"] = (
            "postgresql://user%40name:p%40ssword@localhost:5432/mydb"
        )
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(result.username, "user@name")
        self.assertEqual(result.password, "p@ssword")


if __name__ == "__main__":
    unittest.main()
