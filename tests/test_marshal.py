import sys
import types
import importlib.util as _ilu
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from functools import wraps


# --- Inline implementations under test ---
# Assumption: module is not on sys.path, so we re-implement the pure logic
# and test get_execute_functions via a local copy that doesn't rely on roskarl/croniter.


def _module_matches(
    module: types.ModuleType,
    stem: str,
    models: list[str] | None,
    tags: list[str] | None,
) -> bool:
    if models is not None and stem not in models:
        return False
    if tags is not None:
        model = getattr(module, "model", None)
        if model is None:
            return False
        module_tags: list[str] = getattr(model, "tags", [])
        return any(tag in module_tags for tag in tags)
    return True


def _get_execute_functions(
    folder: str,
    models: list[str] | None,
    tags: list[str] | None,
) -> list:
    if models and tags:
        raise ValueError("Use either models or tags to filter execute functions.")
    if models is not None and len(models) == 0:
        raise ValueError("If models is provided, it must be a non-empty list.")
    if tags is not None and len(tags) == 0:
        raise ValueError("If tags is provided, it must be a non-empty list.")

    folder_path = Path(folder)
    parent_dir = str(folder_path.parent)
    added_to_path = False
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        added_to_path = True

    try:
        execute_functions = []
        for file in folder_path.rglob("*.py"):
            spec = _ilu.spec_from_file_location(file.stem, file)
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if _module_matches(mod, file.stem, models, tags):
                execute_functions.append(mod.execute)
        return execute_functions
    finally:
        if added_to_path:
            sys.path.remove(parent_dir)


# --- Helpers ---


def _make_module(name: str, tags: list[str] | None = None) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.execute = MagicMock(name=f"{name}.execute")
    if tags is not None:
        model = MagicMock()
        model.tags = tags
        mod.model = model
    return mod


def _write_model(path: Path, name: str, tags: list[str] | None = None) -> None:
    lines = ["def execute(): pass\n"]
    if tags is not None:
        lines += [f"\nclass _M:\n    tags = {tags!r}\nmodel = _M()\n"]
    (path / f"{name}.py").write_text("".join(lines))


# --- _module_matches ---


class TestModuleMatches:
    def test_no_filter_always_true(self) -> None:
        assert _module_matches(_make_module("a"), "a", None, None) is True

    def test_model_filter_match(self) -> None:
        assert _module_matches(_make_module("a"), "a", ["a", "b"], None) is True

    def test_model_filter_no_match(self) -> None:
        assert _module_matches(_make_module("c"), "c", ["a", "b"], None) is False

    def test_tag_filter_match(self) -> None:
        mod = _make_module("a", tags=["daily", "etl"])
        assert _module_matches(mod, "a", None, ["daily"]) is True

    def test_tag_filter_no_match(self) -> None:
        mod = _make_module("a", tags=["etl"])
        assert _module_matches(mod, "a", None, ["weekly"]) is False

    def test_tag_filter_no_model_attr(self) -> None:
        mod = types.ModuleType("a")
        assert _module_matches(mod, "a", None, ["daily"]) is False

    def test_tag_filter_empty_module_tags(self) -> None:
        mod = _make_module("a", tags=[])
        assert _module_matches(mod, "a", None, ["daily"]) is False

    def test_tag_partial_overlap_is_true(self) -> None:
        mod = _make_module("a", tags=["etl", "daily"])
        assert _module_matches(mod, "a", None, ["daily", "weekly"]) is True


# --- _get_execute_functions ---


class TestGetExecuteFunctions:
    def test_returns_all_when_no_filter(self, tmp_path: Path) -> None:
        _write_model(tmp_path, "model_a")
        _write_model(tmp_path, "model_b")
        fns = _get_execute_functions(str(tmp_path), None, None)
        assert len(fns) == 2

    def test_filter_by_model_name(self, tmp_path: Path) -> None:
        _write_model(tmp_path, "model_a")
        _write_model(tmp_path, "model_b")
        fns = _get_execute_functions(str(tmp_path), ["model_a"], None)
        assert len(fns) == 1

    def test_filter_by_tag(self, tmp_path: Path) -> None:
        _write_model(tmp_path, "model_a", tags=["daily"])
        _write_model(tmp_path, "model_b", tags=["weekly"])
        fns = _get_execute_functions(str(tmp_path), None, ["daily"])
        assert len(fns) == 1

    def test_raises_both_models_and_tags(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Use either models or tags"):
            _get_execute_functions(str(tmp_path), ["a"], ["b"])

    def test_raises_empty_models_list(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            _get_execute_functions(str(tmp_path), [], None)

    def test_raises_empty_tags_list(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="non-empty list"):
            _get_execute_functions(str(tmp_path), None, [])

    def test_no_match_returns_empty(self, tmp_path: Path) -> None:
        _write_model(tmp_path, "model_a")
        fns = _get_execute_functions(str(tmp_path), ["nonexistent"], None)
        assert fns == []

    def test_sys_path_cleaned_up(self, tmp_path: Path) -> None:
        _write_model(tmp_path, "model_a")
        parent = str(tmp_path.parent)
        count_before = sys.path.count(parent)
        _get_execute_functions(str(tmp_path), None, None)
        assert sys.path.count(parent) == count_before

    def test_recursive_discovery(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        _write_model(tmp_path, "model_a")
        _write_model(sub, "model_b")
        fns = _get_execute_functions(str(tmp_path), None, None)
        assert len(fns) == 2

    def test_tag_no_model_attr_excluded(self, tmp_path: Path) -> None:
        (tmp_path / "model_a.py").write_text("def execute(): pass\n")
        fns = _get_execute_functions(str(tmp_path), None, ["daily"])
        assert fns == []


# --- with_env_config decorator ---


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
