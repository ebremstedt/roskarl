import os
from roskarl.env import env_var
from unittest import TestCase


class TestGetEnvVar(TestCase):
    def test_get_env_var_string(self):
        env_var_value = "hello"
        env_var_name = "x"

        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name)

        assert env_var_value == real_value

    def test_get_int_var_valid_value(self):
        env_var_value = "5"
        env_var_name = "x"
        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name, type_=int)

        assert type(real_value) == type(529835)

    def test_get_int_var_invalid_value(self):
        env_var_value = "5aioaiwdm"
        env_var_name = "x"
        env_type_ = int
        os.environ[env_var_name] = env_var_value

        with self.assertRaises(ValueError):
            env_var(name=env_var_name, type_=env_type_)

    def test_get_bool_var_valid_value_true(self):
        env_var_value = "true"
        env_var_name = "x"
        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name, type_=bool)

        assert real_value == True

    def test_get_bool_var_valid_value_false_chaos_case(self):
        env_var_value = "FaLsE"
        env_var_name = "x"
        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name, type_=bool)

        assert real_value == False

    def test_get_bool_var_valid_value_invalid_value(self):
        env_var_value = "do ducks wear jackets"
        env_var_name = "x"
        env_type_ = bool
        os.environ[env_var_name] = env_var_value

        with self.assertRaises(ValueError):
            env_var(name=env_var_name, type_=env_type_)

    def test_get_list_var(self):
        env_var_value = "A,B,C,D"
        env_var_name = "proper_list_yo"
        env_type_ = list
        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name, type_=env_type_)

        assert real_value == ["A", "B", "C", "D"]

    def test_get_list_var_with_separator(self):
        env_var_value = "A|B|C|D"
        env_var_name = "x"
        env_type_ = list
        separator = "|"
        os.environ[env_var_name] = env_var_value

        real_value = env_var(name=env_var_name, type_=env_type_, separator=separator)

        assert real_value == ["A", "B", "C", "D"]
