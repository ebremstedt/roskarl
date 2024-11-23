import os
from roskarl.env import get_env_var, EnvVarType
from unittest import mock, TestCase

# def test_get_string_var():
#     env_var = "MY_VAR=Hello World"
#     with mock.patch.dict(os.environ, {"MY_VAR": env_var}):
#         assert get_env_var("MY_VAR") == "Hello World"

# def test_get_list_var():
#     env_var = "LIST_VAR=A,B,C,D"
#     with mock.patch.dict(os.environ, {"LIST_VAR": env_var}):
#         assert get_env_var("LIST_VAR", env_var_type=EnvVarType.LIST_VAR) == ["A", "B", "C", "D"]

# def test_get_list_var_with_separator():
#     env_var = "LIST_VAR=A|B|C|D"
#     with mock.patch.dict(os.environ, {"LIST_VAR": env_var}):
#         assert get_env_var("LIST_VAR", list_separator="|") == ["A", "B","C", "D"]

# def test_get_list_var_with_invalid_separator():
#     env_var = "LIST_VAR=A,B,C,D"
#     with mock.patch.dict(os.environ, {"LIST_VAR": env_var}):
#         try:
#             get_env_var("LIST_VAR", list_separator="|")
#             assert False
#         except ValueError as e:
#             assert str(e) == "Error parsing list from env var 'LIST_VAR': can't split string by '|'"

# def test_get_bool_var():
#     env_var = "BOOL_VAR=true"
#     with mock.patch.dict(os.environ, {"BOOL_VAR": env_var}):
#         assert get_env_var("BOOL_VAR", env_var_type=EnvVarType.BOOL_VAR) is True

# def test_get_bool_var_invalid_value():
#     env_var = "BOOL_VAR=bogus"
#     with mock.patch.dict(os.environ, {"BOOL_VAR": env_var}):
#         try:
#             get_env_var("BOOL_VAR", env_var_type=EnvVarType.BOOL_VAR)
#             assert False
#         except ValueError as e:
#             assert str(e) == "Bool must be set to true or false 'bogus'"

# def test_get_int_var():
#     env_var = "INT_VAR=123"
#     with mock.patch.dict(os.environ, {"INT_VAR": env_var}):
#         assert get_env_var("INT_VAR", env_var_type=EnvVarType.INT_VAR) == 123

# def test_get_int_var_invalid_value():
#     env_var = "INT_VAR=bogus"
#     with mock.patch.dict(os.environ, {"INT_VAR": env_var}):
#         try:
#             get_env_var("INT_VAR", env_var_type=EnvVarType.INT_VAR)
#             assert False
#         except ValueError as e:
#             assert str(e) == "Int must be set to a valid integer 'bogus'"

# def test_get_env_var_missing_value():
#     with mock.patch.dict(os.environ, {}):
#         try:
#             get_env_var("NON_EXISTENT_VAR")
#             assert False
#         except KeyError as e:
#             assert str(e) == "Missing required environment variable for 'NON_EXISTENT_VAR.'"

class TestGetEnvVar(TestCase):
    def test_get_env_var_string(self):
        env_var_value = "hello"
        env_var_name = "x"
        os.environ[env_var_name] = env_var_value

        real_value = get_env_var(var=env_var_name)

        assert env_var_value == real_value


    def test_get_env_var_empty(self):
        env_var_name = "this_var_isnt_set_at_all"

        with self.assertRaises(KeyError):
            get_env_var(var=env_var_name)