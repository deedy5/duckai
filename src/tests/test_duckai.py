import time
import pytest

from duckai import DuckAI

CHAT_MODELS = list(DuckAI._chat_models)


@pytest.fixture(autouse=True)
def pause_between_tests() -> None:
    time.sleep(2)


def test_context_manager() -> None:
    with DuckAI() as duckai:
        results = duckai.chat("cars")
        assert len(results) >= 1


@pytest.mark.parametrize("model", CHAT_MODELS)
def test_chat(model: str) -> None:
    results = DuckAI().chat("cat", model=model)
    assert  len(results) >= 1
