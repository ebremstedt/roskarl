import pytest
from unittest.mock import patch
from roskarl.cron import has_offset, env_var_cron, env_var_cron_batch


class TestHasOffset:
    def test_every_minute(self):
        assert has_offset("* * * * *") is False

    def test_every_hour(self):
        assert has_offset("0 * * * *") is False

    def test_every_2_hours(self):
        assert has_offset("0 */2 * * *") is False

    def test_every_6_hours_every_2_days(self):
        assert has_offset("0 */6 */2 * *") is False

    def test_offset_hour(self):
        assert has_offset("0 2 * * *") is True

    def test_offset_hour_step(self):
        assert has_offset("0 2/2 * * *") is True

    def test_offset_minute(self):
        assert has_offset("5 * * * *") is True

    def test_offset_dom(self):
        assert has_offset("0 */2 2 * *") is True


class TestEnvVarCron:
    def test_valid_cron(self):
        with patch.dict("os.environ", {"MY_CRON": "0 * * * *"}):
            assert env_var_cron("MY_CRON") == "0 * * * *"

    def test_invalid_cron(self):
        with patch.dict("os.environ", {"MY_CRON": "not_a_cron"}):
            with pytest.raises(ValueError, match="not a valid cron expression"):
                env_var_cron("MY_CRON")

    def test_default_returned_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            assert env_var_cron("MY_CRON", default="0 * * * *") == "0 * * * *"

    def test_required_raises_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="is not set"):
                env_var_cron("MY_CRON", required=True)

    def test_returns_none_when_unset_not_required(self):
        with patch.dict("os.environ", {}, clear=True):
            assert env_var_cron("MY_CRON", should_print_unset=False) is None


class TestEnvVarCronBatch:
    def test_valid_no_offset(self):
        with patch.dict("os.environ", {"MY_CRON": "0 */2 * * *"}):
            assert env_var_cron_batch("MY_CRON") == "0 */2 * * *"

    def test_raises_on_offset(self):
        with patch.dict("os.environ", {"MY_CRON": "0 2 * * *"}):
            with pytest.raises(ValueError, match="has a cron offset"):
                env_var_cron_batch("MY_CRON")

    def test_raises_on_offset_step(self):
        with patch.dict("os.environ", {"MY_CRON": "0 2/2 * * *"}):
            with pytest.raises(ValueError, match="has a cron offset"):
                env_var_cron_batch("MY_CRON")

    def test_valid_default(self):
        with patch.dict("os.environ", {}, clear=True):
            assert (
                env_var_cron_batch(
                    "MY_CRON", default="0 */6 * * *", should_print_unset=False
                )
                == "0 */6 * * *"
            )

    def test_invalid_default_offset(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="has a cron offset"):
                env_var_cron_batch(
                    "MY_CRON", default="0 2 * * *", should_print_unset=False
                )

    def test_required_raises_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="is not set"):
                env_var_cron_batch("MY_CRON", required=True)

    def test_returns_none_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            assert env_var_cron_batch("MY_CRON", should_print_unset=False) is None
