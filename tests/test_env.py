import os
import unittest
from unittest.mock import patch

import pytest

from roskarl import (
    env_var,
    env_var_cron,
    env_var_dsn,
    env_var_tz,
    env_var_list,
    env_var_bool,
    env_var_int,
    env_var_float,
)


class TestEnvVarUtils(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_env_var_str_set(self):
        os.environ["TEST_STR"] = "hello"
        self.assertEqual(env_var("TEST_STR"), "hello")

    def test_env_var_cron_valid(self):
        os.environ["TEST_CRON"] = "0 0 * * *"
        self.assertEqual(env_var_cron("TEST_CRON"), "0 0 * * *")

    def test_env_var_cron_invalid(self):
        os.environ["TEST_CRON"] = "invalid cron"
        with self.assertRaises(ValueError) as context:
            env_var_cron("TEST_CRON")
        self.assertIn("Value is not a valid cron expression.", str(context.exception))

    def test_env_var_tz_valid(self):
        os.environ["TEST_TZ"] = "America/New_York"
        self.assertEqual(env_var_tz("TEST_TZ"), "America/New_York")

    def test_env_var_tz_invalid(self):
        os.environ["TEST_TZ"] = "Invalid/Timezone"
        with self.assertRaises(ValueError) as context:
            env_var_tz("TEST_TZ")
        self.assertIn("Timezone string was not valid", str(context.exception))

    def test_env_var_list_default_separator(self):
        os.environ["TEST_LIST"] = "a, b, c"
        self.assertEqual(env_var_list("TEST_LIST"), ["a", "b", "c"])

    def test_env_var_list_custom_separator(self):
        os.environ["TEST_LIST"] = "a;b;c"
        self.assertEqual(env_var_list("TEST_LIST", separator=";"), ["a", "b", "c"])

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

    def test_env_var_int(self):
        os.environ["TEST_INT"] = "42"
        self.assertEqual(env_var_int("TEST_INT"), 42)

    def test_env_var_int_invalid(self):
        os.environ["TEST_INT"] = "not-an-int"
        with self.assertRaises(ValueError):
            env_var_int("TEST_INT")

    def test_env_var_float(self):
        os.environ["TEST_FLOAT"] = "3.14"
        self.assertEqual(env_var_float("TEST_FLOAT"), 3.14)

    def test_env_var_float_invalid(self):
        os.environ["TEST_FLOAT"] = "not-a-float"
        with self.assertRaises(ValueError):
            env_var_float("TEST_FLOAT")

    def test_env_var_dsn_basic(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:password@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.protocol == "mssql"
            assert result.username == "user"
            assert result.password == "password"
            assert result.hostname == "localhost"
            assert result.port == 1433
            assert result.database == "testdb"

    def test_env_var_dsn_no_port(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "postgresql://user:password@localhost/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.port is None

    def test_env_var_dsn_no_database(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mysql://user:password@localhost:3306"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.database is None

    def test_env_var_dsn_missing_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            result = env_var_dsn("MISSING_DSN")
            assert result is None

    def test_env_var_dsn_quote_in_password(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:%22password@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == '"password'

    def test_env_var_dsn_at_symbol_in_password(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:pass%40word@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass@word"

    def test_env_var_dsn_colon_in_password(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:pass%3Aword@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass:word"

    def test_env_var_dsn_colon_in_username(self):
        with patch.dict(
            os.environ,
            {"TEST_DSN": "mssql://user%3Aname:password@localhost:1433/testdb"},
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.username == "user:name"

    def test_env_var_dsn_complex_password(self):
        with patch.dict(
            os.environ,
            {
                "TEST_DSN": "mssql://user:%22%25%23%2B%5E%28T81%2AV3yo%40@localhost:1433/testdb"
            },
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == '"%#+^(T81*V3yo@'

    def test_env_var_dsn_space_in_credentials(self):
        with patch.dict(
            os.environ,
            {"TEST_DSN": "mssql://user%20name:pass%20word@localhost:1433/testdb"},
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.username == "user name"
            assert result.password == "pass word"

    def test_env_var_dsn_slash_in_password(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:pass%2Fword@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass/word"

    def test_env_var_dsn_backslash_in_password(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:pass%5Cword@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass\\word"

    def test_env_var_dsn_special_chars_in_password(self):
        with patch.dict(
            os.environ,
            {"TEST_DSN": "mssql://user:pass%26%3D%3F%21%24%7E@localhost:1433/testdb"},
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass&=?!$~"

    def test_env_var_dsn_brackets_in_password(self):
        with patch.dict(
            os.environ,
            {"TEST_DSN": "mssql://user:pass%5B%5D%7B%7D@localhost:1433/testdb"},
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass[]{}"

    def test_env_var_dsn_pipe_and_semicolon(self):
        with patch.dict(
            os.environ,
            {"TEST_DSN": "mssql://user:pass%7C%3Bword@localhost:1433/testdb"},
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "pass|;word"

    def test_env_var_dsn_invalid_protocol(self):
        with patch.dict(os.environ, {"TEST_DSN": "invalid_dsn_string"}):
            with pytest.raises(ValueError, match="Invalid DSN: Protocol not found"):
                env_var_dsn("TEST_DSN")

    def test_env_var_dsn_no_at_separator(self):
        with patch.dict(os.environ, {"TEST_DSN": "mssql://user:password"}):
            with pytest.raises(ValueError, match="Invalid DSN: No @ separator found"):
                env_var_dsn("TEST_DSN")

    def test_env_var_dsn_no_colon_in_credentials(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://userpassword@localhost:1433/testdb"}
        ):
            with pytest.raises(
                ValueError, match="Invalid DSN: No colon separator found in credentials"
            ):
                env_var_dsn("TEST_DSN")

    def test_env_var_dsn_invalid_port(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:password@localhost:invalid/testdb"}
        ):
            with pytest.raises(ValueError, match="Failed to parse DSN string"):
                env_var_dsn("TEST_DSN")

    def test_dsn_connection_string_generation(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:p%40ssword@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            assert result.password == "p@ssword"
            assert "p%40ssword" in result.connection_string

    def test_dsn_str_representation(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:password@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            str_repr = str(result)
            assert "password" not in str_repr
            assert "****" in str_repr
            assert "user" in str_repr

    def test_dsn_to_dict(self):
        with patch.dict(
            os.environ, {"TEST_DSN": "mssql://user:password@localhost:1433/testdb"}
        ):
            result = env_var_dsn("TEST_DSN")
            assert result is not None
            dict_repr = result.to_dict()
            assert dict_repr["protocol"] == "mssql"
            assert dict_repr["username"] == "user"
            assert dict_repr["password"] == "password"
            assert dict_repr["hostname"] == "localhost"
            assert dict_repr["port"] == 1433
            assert dict_repr["database"] == "testdb"


if __name__ == "__main__":
    unittest.main()
