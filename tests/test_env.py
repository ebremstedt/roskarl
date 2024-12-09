import os
import unittest

from roskarl import (
    env_var,
    env_var_cron,
    env_var_tz,
    env_var_list,
    env_var_bool,
    env_var_int,
    env_var_float
)


class TestEnvVarUtils(unittest.TestCase):
    def setUp(self):
        self.original_environ = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_env_var_str_set(self):
        os.environ['TEST_STR'] = 'hello'
        self.assertEqual(env_var('TEST_STR'), 'hello')

    def test_env_var_cron_valid(self):
        os.environ['TEST_CRON'] = '0 0 * * *'
        self.assertEqual(env_var_cron('TEST_CRON'), '0 0 * * *')

    def test_env_var_cron_invalid(self):
        os.environ['TEST_CRON'] = 'invalid cron'
        with self.assertRaises(ValueError) as context:
            env_var_cron('TEST_CRON')
        self.assertIn('Value is not a valid cron expression.', str(context.exception))

    def test_env_var_tz_valid(self):
        os.environ['TEST_TZ'] = 'America/New_York'
        self.assertEqual(env_var_tz('TEST_TZ'), 'America/New_York')

    def test_env_var_tz_invalid(self):
        os.environ['TEST_TZ'] = 'Invalid/Timezone'
        with self.assertRaises(ValueError) as context:
            env_var_tz('TEST_TZ')
        self.assertIn('Timezone string was not valid', str(context.exception))

    def test_env_var_list_default_separator(self):
        os.environ['TEST_LIST'] = 'a, b, c'
        self.assertEqual(env_var_list('TEST_LIST'), ['a', 'b', 'c'])

    def test_env_var_list_custom_separator(self):
        os.environ['TEST_LIST'] = 'a;b;c'
        self.assertEqual(env_var_list('TEST_LIST', separator=';'), ['a', 'b', 'c'])

    def test_env_var_bool_true(self):
        os.environ['TEST_BOOL'] = 'TRUE'
        self.assertTrue(env_var_bool('TEST_BOOL'))
        os.environ['TEST_BOOL'] = 'true'
        self.assertTrue(env_var_bool('TEST_BOOL'))

    def test_env_var_bool_false(self):
        os.environ['TEST_BOOL'] = 'FALSE'
        self.assertFalse(env_var_bool('TEST_BOOL'))
        os.environ['TEST_BOOL'] = 'false'
        self.assertFalse(env_var_bool('TEST_BOOL'))

    def test_env_var_bool_invalid(self):
        os.environ['TEST_BOOL'] = 'not-a-bool'
        with self.assertRaises(ValueError) as context:
            env_var_bool('TEST_BOOL')
        self.assertIn("Bool must be set to true or false", str(context.exception))

    def test_env_var_int(self):
        os.environ['TEST_INT'] = '42'
        self.assertEqual(env_var_int('TEST_INT'), 42)

    def test_env_var_int_invalid(self):
        os.environ['TEST_INT'] = 'not-an-int'
        with self.assertRaises(ValueError):
            env_var_int('TEST_INT')

    def test_env_var_float(self):
        os.environ['TEST_FLOAT'] = '3.14'
        self.assertEqual(env_var_float('TEST_FLOAT'), 3.14)

    def test_env_var_float_invalid(self):
        os.environ['TEST_FLOAT'] = 'not-a-float'
        with self.assertRaises(ValueError):
            env_var_float('TEST_FLOAT')


if __name__ == '__main__':
    unittest.main()
