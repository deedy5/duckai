from __future__ import annotations

from typing import Any

from .exceptions import DuckAIException

try:
    HAS_ORJSON = True
    import orjson
except ImportError:
    HAS_ORJSON = False
    import json


def json_dumps(obj: Any) -> str:
    try:
        return (
            orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode()
            if HAS_ORJSON
            else json.dumps(obj, ensure_ascii=False, indent=2)
        )
    except Exception as ex:
        raise DuckAIException(f"{type(ex).__name__}: {ex}") from ex


def json_loads(obj: str | bytes) -> Any:
    try:
        return orjson.loads(obj) if HAS_ORJSON else json.loads(obj)
    except Exception as ex:
        raise DuckAIException(f"{type(ex).__name__}: {ex}") from ex


def _expand_proxy_tb_alias(proxy: str | None) -> str | None:
    """Expand "tb" to a full proxy URL if applicable."""
    return "socks5://127.0.0.1:9150" if proxy == "tb" else proxy
