import pytest
from functools import wraps


class TestWithEnvConfig:
    def _make_decorator(self, fake_env: object):
        def with_env_config(func):
            @wraps(func)
            def wrapper() -> None:
                func(fake_env)

            return wrapper

        return with_env_config

    def test_calls_func_with_env(self) -> None:
        fake_env = object()
        received = []

        decorator = self._make_decorator(fake_env)

        @decorator
        def my_func(env: object) -> None:
            received.append(env)

        my_func()
        assert received == [fake_env]

    def test_preserves_function_name(self) -> None:
        decorator = self._make_decorator(None)

        @decorator
        def my_special_func(env: object) -> None:
            pass

        assert my_special_func.__name__ == "my_special_func"

    def test_wrapper_takes_no_args(self) -> None:
        decorator = self._make_decorator(None)

        @decorator
        def my_func(env: object) -> None:
            pass

        with pytest.raises(TypeError):
            my_func("unexpected_arg")  # type: ignore[call-arg]
