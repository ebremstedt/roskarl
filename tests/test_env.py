import logging
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from uuid import UUID
from roskarl import (
    env_var,
    env_var_cron,
    env_var_custom,
    env_var_dsn,
    env_var_duration,
    env_var_enum,
    env_var_log_level,
    env_var_path,
    env_var_secret,
    env_var_tz,
    env_var_url,
    env_var_list,
    env_var_bool,
    env_var_int,
    env_var_float,
    env_var_iso8601_datetime,
    env_var_rfc3339_datetime,
    env_var_dsn,
    DSN,
    Secret,
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

    def test_env_var_tz_invalid_default_raises(self):
        with self.assertRaises(ValueError):
            env_var_tz("TEST_TZ", default="Invalid/Timezone")

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
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertIsInstance(result, DSN)
        self.assertEqual(result.protocol, "postgresql")
        self.assertEqual(result.username, "user")
        self.assertEqual(result.password, "password")
        self.assertEqual(result.hostname, "localhost")
        self.assertEqual(result.port, 5432)
        self.assertEqual(result.database, "mydb")

    def test_env_var_dsn_valid_no_port(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost/mydb"
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertIsNone(result.port)

    def test_env_var_dsn_valid_no_database(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432"
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertIsNone(result.database)

    def test_env_var_dsn_connection_string(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432/mydb"
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertEqual(
            result.connection_string, "postgresql://user:password@localhost:5432/mydb"
        )

    def test_env_var_dsn_str_masks_password(self):
        os.environ["TEST_DSN"] = "postgresql://user:password@localhost:5432/mydb"
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertIn("****", str(result))
        self.assertNotIn("password", str(result))

    def test_env_var_dsn_invalid(self):
        os.environ["TEST_DSN"] = "not-a-dsn"
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        with self.assertRaises(ValueError):
            env_var_dsn("TEST_DSN", default=dsn)

    def test_env_var_dsn_not_set_raises(self):
        os.environ.pop("TEST_DSN", None)
        with self.assertRaises(ValueError):
            env_var_dsn("TEST_DSN")

    def test_env_var_dsn_not_set_returns_default(self):
        default = DSN(
            protocol="postgresql", username="u", password="p", hostname="localhost"
        )
        self.assertEqual(env_var_dsn("TEST_DSN", default=default), default)

    def test_env_var_dsn_url_encoded_credentials(self):
        os.environ["TEST_DSN"] = (
            "postgresql://user%40name:p%40ssword@localhost:5432/mydb"
        )
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="password",
            hostname="localhost",
            port=5432,
            database="wee",
        )
        result = env_var_dsn("TEST_DSN", default=dsn)
        self.assertEqual(result.username, "user@name")
        self.assertEqual(result.password, "p@ssword")

    def test_dsn_libpq_string(self):
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="pass",
            hostname="localhost",
            port=5432,
            database="mydb",
        )
        self.assertEqual(
            dsn.libpq_string,
            "host=localhost user=user password=pass port=5432 dbname=mydb",
        )

    def test_dsn_libpq_string_no_port(self):
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="pass",
            hostname="localhost",
            database="mydb",
        )
        self.assertEqual(
            dsn.libpq_string,
            "host=localhost user=user password=pass dbname=mydb",
        )

    def test_dsn_libpq_string_no_database(self):
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="pass",
            hostname="localhost",
            port=5432,
        )
        self.assertEqual(
            dsn.libpq_string,
            "host=localhost user=user password=pass port=5432",
        )

    def test_dsn_libpq_string_no_port_no_database(self):
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="pass",
            hostname="localhost",
        )
        self.assertEqual(
            dsn.libpq_string,
            "host=localhost user=user password=pass",
        )

    def test_dsn_build_mssql_string(self):
        dsn = DSN(
            protocol="mssql",
            username="sa",
            password="pw",
            hostname="db.example.com",
            port=1433,
            database="mydb",
        )
        self.assertEqual(
            dsn.build_mssql_string(),
            "DRIVER={ODBC Driver 18 for SQL Server};SERVER=db.example.com,1433;DATABASE=mydb;UID=sa;PWD=pw;Encrypt=yes;TrustServerCertificate=yes",
        )

    def test_dsn_build_mssql_string_no_encrypt(self):
        dsn = DSN(
            protocol="mssql",
            username="sa",
            password="pw",
            hostname="db.example.com",
            port=1433,
            database="mydb",
        )
        self.assertEqual(
            dsn.build_mssql_string(encrypt=False, trust_server_certificate=False),
            "DRIVER={ODBC Driver 18 for SQL Server};SERVER=db.example.com,1433;DATABASE=mydb;UID=sa;PWD=pw;Encrypt=no;TrustServerCertificate=no",
        )

    def test_dsn_build_mssql_string_custom_driver(self):
        dsn = DSN(
            protocol="mssql",
            username="sa",
            password="pw",
            hostname="db.example.com",
            port=1433,
            database="mydb",
        )
        self.assertEqual(
            dsn.build_mssql_string(driver="ODBC Driver 17 for SQL Server"),
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db.example.com,1433;DATABASE=mydb;UID=sa;PWD=pw;Encrypt=yes;TrustServerCertificate=yes",
        )

    def test_dsn_build_mssql_string_requires_port(self):
        dsn = DSN(
            protocol="mssql",
            username="sa",
            password="pw",
            hostname="db.example.com",
            database="mydb",
        )
        with self.assertRaises(ValueError):
            dsn.build_mssql_string()

    def test_dsn_build_mssql_string_requires_database(self):
        dsn = DSN(
            protocol="mssql",
            username="sa",
            password="pw",
            hostname="db.example.com",
            port=1433,
        )
        with self.assertRaises(ValueError):
            dsn.build_mssql_string()

    def test_dsn_to_dict(self):
        dsn = DSN(
            protocol="postgresql",
            username="user",
            password="pass",
            hostname="localhost",
            port=5432,
            database="mydb",
        )
        self.assertEqual(
            dsn.to_dict(),
            {
                "protocol": "postgresql",
                "username": "user",
                "password": "pass",
                "hostname": "localhost",
                "port": 5432,
                "database": "mydb",
            },
        )


class TestRequiredRaisesWhenUnset(unittest.TestCase):
    """Locks in the behavior the `required=True` overloads exist for."""

    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_env_var(self):
        with self.assertRaises(ValueError):
            env_var("MISSING", required=True)

    def test_env_var_tz(self):
        with self.assertRaises(ValueError):
            env_var_tz("MISSING", required=True)

    def test_env_var_list(self):
        with self.assertRaises(ValueError):
            env_var_list("MISSING", required=True)

    def test_env_var_bool(self):
        with self.assertRaises(ValueError):
            env_var_bool("MISSING", required=True)

    def test_env_var_int(self):
        with self.assertRaises(ValueError):
            env_var_int("MISSING", required=True)

    def test_env_var_float(self):
        with self.assertRaises(ValueError):
            env_var_float("MISSING", required=True)

    def test_env_var_iso8601_datetime(self):
        with self.assertRaises(ValueError):
            env_var_iso8601_datetime("MISSING", required=True)

    def test_env_var_rfc3339_datetime(self):
        with self.assertRaises(ValueError):
            env_var_rfc3339_datetime("MISSING", required=True)

    def test_default_wins_over_required(self):
        self.assertEqual(env_var("MISSING", default="x", required=True), "x")

    def test_empty_string_is_treated_as_unset(self):
        os.environ["EMPTY"] = ""
        self.assertIsNone(env_var("EMPTY", should_print_unset=False))
        with self.assertRaises(ValueError):
            env_var("EMPTY", required=True)


class TestEnvVarCustom(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_parses_with_callable(self):
        os.environ["MY_UUID"] = "12345678-1234-5678-1234-567812345678"
        result = env_var_custom("MY_UUID", UUID)
        self.assertEqual(result, UUID("12345678-1234-5678-1234-567812345678"))

    def test_parser_not_called_when_unset(self):
        def boom(_: str):
            raise AssertionError("parser should not be called when unset")

        self.assertIsNone(env_var_custom("MISSING", boom, should_print_unset=False))

    def test_parser_not_called_when_empty(self):
        os.environ["EMPTY"] = ""

        def boom(_: str):
            raise AssertionError("parser should not be called for empty value")

        self.assertIsNone(env_var_custom("EMPTY", boom, should_print_unset=False))

    def test_returns_default_when_unset(self):
        sentinel = UUID("00000000-0000-0000-0000-000000000000")
        self.assertEqual(env_var_custom("MISSING", UUID, default=sentinel), sentinel)

    def test_required_raises_when_unset(self):
        with self.assertRaises(ValueError):
            env_var_custom("MISSING", UUID, required=True)

    def test_parser_error_propagates(self):
        os.environ["BAD"] = "not-a-uuid"
        with self.assertRaises(ValueError):
            env_var_custom("BAD", UUID)


class TestEnvVarUrl(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_valid_https(self):
        os.environ["U"] = "https://example.com/path"
        self.assertEqual(env_var_url("U"), "https://example.com/path")

    def test_valid_non_http_scheme(self):
        os.environ["U"] = "postgresql://user:pass@host:5432/db"
        self.assertEqual(env_var_url("U"), "postgresql://user:pass@host:5432/db")

    def test_missing_scheme_raises(self):
        os.environ["U"] = "example.com/path"
        with self.assertRaises(ValueError):
            env_var_url("U")

    def test_missing_netloc_raises(self):
        os.environ["U"] = "https://"
        with self.assertRaises(ValueError):
            env_var_url("U")

    def test_invalid_default_raises(self):
        with self.assertRaises(ValueError):
            env_var_url("U", default="not-a-url")

    def test_returns_default_when_unset(self):
        self.assertEqual(
            env_var_url("U", default="https://fallback.test"),
            "https://fallback.test",
        )


class TestEnvVarSecret(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_returns_secret_wrapper(self):
        os.environ["S"] = "super-secret"
        result = env_var_secret("S")
        self.assertIsInstance(result, Secret)
        self.assertEqual(result.reveal(), "super-secret")

    def test_repr_is_masked(self):
        secret = Secret("hunter2")
        self.assertNotIn("hunter2", repr(secret))
        self.assertNotIn("hunter2", str(secret))
        self.assertNotIn("hunter2", f"{secret}")
        self.assertNotIn("hunter2", f"value={secret}")

    def test_eq(self):
        self.assertEqual(Secret("a"), Secret("a"))
        self.assertNotEqual(Secret("a"), Secret("b"))
        self.assertNotEqual(Secret("a"), "a")

    def test_hashable(self):
        self.assertEqual(hash(Secret("a")), hash(Secret("a")))

    def test_default_used_when_unset(self):
        fallback = Secret("fallback")
        self.assertEqual(env_var_secret("S", default=fallback), fallback)


class TestEnvVarPath(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_returns_path(self):
        os.environ["P"] = "/tmp/foo"
        result = env_var_path("P")
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path("/tmp/foo"))

    def test_must_exist_passes_for_existing(self):
        with tempfile.NamedTemporaryFile() as f:
            os.environ["P"] = f.name
            self.assertEqual(env_var_path("P", must_exist=True), Path(f.name))

    def test_must_exist_raises_for_missing(self):
        os.environ["P"] = "/definitely/does/not/exist/xyz123"
        with self.assertRaises(ValueError):
            env_var_path("P", must_exist=True)

    def test_must_exist_validates_default(self):
        with self.assertRaises(ValueError):
            env_var_path(
                "P", default=Path("/definitely/does/not/exist/xyz123"), must_exist=True
            )


class _Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestEnvVarEnum(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_valid_member(self):
        os.environ["C"] = "red"
        self.assertEqual(env_var_enum("C", _Color), _Color.RED)

    def test_invalid_member_raises(self):
        os.environ["C"] = "purple"
        with self.assertRaises(ValueError):
            env_var_enum("C", _Color)

    def test_default_used_when_unset(self):
        self.assertEqual(env_var_enum("C", _Color, default=_Color.BLUE), _Color.BLUE)


class TestEnvVarLogLevel(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_info(self):
        os.environ["L"] = "INFO"
        self.assertEqual(env_var_log_level("L"), logging.INFO)

    def test_case_insensitive(self):
        os.environ["L"] = "debug"
        self.assertEqual(env_var_log_level("L"), logging.DEBUG)

    def test_warn_alias(self):
        os.environ["L"] = "WARN"
        self.assertEqual(env_var_log_level("L"), logging.WARNING)

    def test_fatal_alias(self):
        os.environ["L"] = "FATAL"
        self.assertEqual(env_var_log_level("L"), logging.CRITICAL)

    def test_invalid_raises(self):
        os.environ["L"] = "VERBOSE"
        with self.assertRaises(ValueError):
            env_var_log_level("L")

    def test_default_used_when_unset(self):
        self.assertEqual(env_var_log_level("L", default=logging.INFO), logging.INFO)


class TestEnvVarDuration(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()
        os.environ.clear()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_seconds(self):
        os.environ["D"] = "30s"
        self.assertEqual(env_var_duration("D"), timedelta(seconds=30))

    def test_minutes(self):
        os.environ["D"] = "5m"
        self.assertEqual(env_var_duration("D"), timedelta(minutes=5))

    def test_hours(self):
        os.environ["D"] = "2h"
        self.assertEqual(env_var_duration("D"), timedelta(hours=2))

    def test_days(self):
        os.environ["D"] = "7d"
        self.assertEqual(env_var_duration("D"), timedelta(days=7))

    def test_milliseconds(self):
        os.environ["D"] = "500ms"
        self.assertEqual(env_var_duration("D"), timedelta(milliseconds=500))

    def test_compound(self):
        os.environ["D"] = "1h30m"
        self.assertEqual(env_var_duration("D"), timedelta(hours=1, minutes=30))

    def test_compound_with_ms(self):
        os.environ["D"] = "2h45m30s500ms"
        self.assertEqual(
            env_var_duration("D"),
            timedelta(hours=2, minutes=45, seconds=30, milliseconds=500),
        )

    def test_tolerates_spaces(self):
        os.environ["D"] = "1h 30m"
        self.assertEqual(env_var_duration("D"), timedelta(hours=1, minutes=30))

    def test_bare_number_raises(self):
        os.environ["D"] = "30"
        with self.assertRaises(ValueError):
            env_var_duration("D")

    def test_unknown_unit_raises(self):
        os.environ["D"] = "30x"
        with self.assertRaises(ValueError):
            env_var_duration("D")

    def test_trailing_garbage_raises(self):
        os.environ["D"] = "30s garbage"
        with self.assertRaises(ValueError):
            env_var_duration("D")

    def test_default_used_when_unset(self):
        fallback = timedelta(minutes=10)
        self.assertEqual(env_var_duration("D", default=fallback), fallback)


class TestDSNDatabaseNameWithSpaces(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_percent_encoded_space(self):
        os.environ["TEST_DSN"] = "mssql://user:pass@host:1433/SDWH%20RIS%20Datamodel"
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(result.database, "SDWH RIS Datamodel")

    def test_literal_space_in_database(self):
        os.environ["TEST_DSN"] = "mssql://user:pass@host:1433/SDWH RIS Datamodel"
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(result.database, "SDWH RIS Datamodel")

    def test_multiple_spaces_percent_encoded(self):
        os.environ["TEST_DSN"] = "mssql://user:pass@host:1433/My%20Database%20Name"
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(result.database, "My Database Name")

    def test_no_space_database_unaffected(self):
        os.environ["TEST_DSN"] = "mssql://user:pass@host:1433/SimpleDB"
        result = env_var_dsn("TEST_DSN")
        self.assertEqual(result.database, "SimpleDB")

    def test_mssql_string_with_spaced_database(self):
        os.environ["TEST_DSN"] = "mssql://sa:pw@db.example.com:1433/SDWH%20RIS%20Datamodel"
        result = env_var_dsn("TEST_DSN")
        mssql = result.build_mssql_string()
        self.assertIn("DATABASE=SDWH RIS Datamodel", mssql)

    def test_connection_string_contains_decoded_database(self):
        os.environ["TEST_DSN"] = "mssql://user:pass@host:1433/SDWH%20RIS%20Datamodel"
        result = env_var_dsn("TEST_DSN")
        self.assertIn("SDWH RIS Datamodel", result.connection_string)


if __name__ == "__main__":
    unittest.main()
