from __future__ import annotations

import logging
import os
import warnings
from collections.abc import Iterator
from random import choice
from types import TracebackType
from typing import Any, Literal

import primp

from .exceptions import ConversationLimitException, DuckAIException, RatelimitException, TimeoutException
from .libs.utils_chat import HashBuilder
from .utils import (
    _expand_proxy_tb_alias,
    json_loads,
)

logger = logging.getLogger("duckai.DuckAI")


class DuckAI:
    """DuckAI class to get search results from duckduckgo.com."""

    _impersonates = (
        "chrome_100", "chrome_101", "chrome_104", "chrome_105", "chrome_106", "chrome_107",
        "chrome_108", "chrome_109", "chrome_114", "chrome_116", "chrome_117", "chrome_118",
        "chrome_119", "chrome_120", "chrome_123", "chrome_124", "chrome_126", "chrome_127",
        "chrome_128", "chrome_129", "chrome_130", "chrome_131", "chrome_133",
        "safari_ios_16.5", "safari_ios_17.2", "safari_ios_17.4.1", "safari_ios_18.1.1",
        "safari_15.3", "safari_15.5", "safari_15.6.1", "safari_16", "safari_16.5",
        "safari_17.0", "safari_17.2.1", "safari_17.4.1", "safari_17.5",
        "safari_18", "safari_18.2",
        "safari_ipad_18",
        "edge_101", "edge_122", "edge_127", "edge_131",
        "firefox_109", "firefox_117", "firefox_128", "firefox_133", "firefox_135",
    )  # fmt: skip
    _impersonates_os = ("android", "ios", "linux", "macos", "windows")
    _chat_models = {
        "gpt-4o-mini": "gpt-4o-mini",
        "llama-3.3-70b": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "o3-mini": "o3-mini",
        "mistral-small-3": "mistralai/Mistral-Small-24B-Instruct-2501",
    }
    _chat_xfe: str = ""
    _hashbuilder = HashBuilder()

    def __init__(
        self,
        proxy: str | None = None,
        timeout: int | None = 10,
        verify: bool = True,
    ) -> None:
        """Initialize the DuckAI object.

        Args:
            proxy (str, optional): proxy for the HTTP client, supports http/https/socks5 protocols.
                example: "http://user:pass@example.com:3128". Defaults to None.
            timeout (int, optional): Timeout value for the HTTP client. Defaults to 10.
            verify (bool): SSL verification when making the request. Defaults to True.
        """
        duckai_proxy: str | None = os.environ.get("DUCKAI_PROXY")
        self.proxy: str | None = duckai_proxy if duckai_proxy else _expand_proxy_tb_alias(proxy)
        self.timeout = timeout
        self.client = primp.Client(
            proxy=self.proxy,
            timeout=self.timeout,
            cookie_store=True,
            referer=True,
            impersonate=choice(self._impersonates),  # type: ignore
            impersonate_os=choice(self._impersonates_os),  # type: ignore
            follow_redirects=False,
            verify=verify,
        )
        self._chat_messages: list[dict[str, str]] = []
        self._chat_tokens_count = 0
        self._chat_vqd: str = ""
        self._chat_vqd_hash: str = ""
        self.sleep_timestamp = 0.0

    def __enter__(self) -> DuckAI:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        pass

    def _get_url(
        self,
        method: Literal["GET", "HEAD", "OPTIONS", "DELETE", "POST", "PUT", "PATCH"],
        url: str,
        params: dict[str, str] | None = None,
        content: bytes | None = None,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        json: Any = None,
        timeout: float | None = None,
    ) -> Any:
        try:
            resp = self.client.request(
                method,
                url,
                params=params,
                content=content,
                data=data,
                headers=headers,
                cookies=cookies,
                json=json,
                timeout=timeout or self.timeout,
            )
        except Exception as ex:
            if "time" in str(ex).lower():
                raise TimeoutException(f"{url} {type(ex).__name__}: {ex}") from ex
            raise DuckAIException(f"{url} {type(ex).__name__}: {ex}") from ex
        logger.debug(f"_get_url() {resp.url} {resp.status_code}")
        if resp.status_code == 200:
            return resp
        elif resp.status_code in (202, 301, 403, 400, 429, 418):
            raise RatelimitException(f"{resp.url} {resp.status_code} Ratelimit")
        raise DuckAIException(f"{resp.url} return None. {params=} {content=} {data=}")

    def chat_yield(self, keywords: str, model: str = "gpt-4o-mini", timeout: float = 30) -> Iterator[str]:
        """Initiates a chat session with DuckDuckGo AI.

        Args:
            keywords (str): The initial message or question to send to the AI.
            model (str): The model to use: "gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
                "o3-mini", "mistral-small-3". Defaults to "gpt-4o-mini".
            timeout (int): Timeout value for the HTTP client. Defaults to 20.

        Yields:
            str: Chunks of the response from the AI.
        """
        # x-fe-version
        if not DuckAI._chat_xfe:
            resp_content = self._get_url(
                method="GET",
                url="https://duckduckgo.com/?q=DuckDuckGo+AI+Chat&ia=chat&duckai=1",
            ).content
            try:
                xfe1 = resp_content.split(b'__DDG_BE_VERSION__="', maxsplit=1)[1].split(b'"', maxsplit=1)[0].decode()
                xfe2 = resp_content.split(b'__DDG_FE_CHAT_HASH__="', maxsplit=1)[1].split(b'"', maxsplit=1)[0].decode()
                DuckAI._chat_xfe = f"{xfe1}-{xfe2}"
            except Exception as ex:
                raise DuckAIException(f"chat_yield() Error to get _chat_xfe: {type(ex).__name__}: {ex}") from ex
        # vqd
        if not self._chat_vqd:
            resp = self._get_url(
                method="GET", url="https://duckduckgo.com/duckchat/v1/status", headers={"x-vqd-accept": "1"}
            )
            self._chat_vqd = resp.headers.get("x-vqd-4", "")
            self._chat_vqd_hash = resp.headers.get("x-vqd-hash-1", "")

        # x-vqd-hash-1
        self._chat_vqd_hash = self._hashbuilder.build_hash(self._chat_vqd_hash, self.client.headers)

        self._chat_messages.append({"role": "user", "content": keywords})
        self._chat_tokens_count += max(len(keywords) // 4, 1)  # approximate number of tokens
        if model not in self._chat_models:
            warnings.warn(f"{model=} is unavailable. Using 'gpt-4o-mini'", stacklevel=1)
            model = "gpt-4o-mini"
        json_data = {
            "model": self._chat_models[model],
            "messages": self._chat_messages,
        }
        resp = self._get_url(
            method="POST",
            url="https://duckduckgo.com/duckchat/v1/chat",
            headers={
                "x-fe-version": DuckAI._chat_xfe,
                "x-vqd-4": self._chat_vqd,
                "x-vqd-hash-1": self._chat_vqd_hash,
            },
            json=json_data,
            timeout=timeout,
        )
        self._chat_vqd = resp.headers.get("x-vqd-4", "")
        self._chat_vqd_hash = resp.headers.get("x-vqd-hash-1", "")
        chunks = []
        try:
            for chunk in resp.stream():
                lines = chunk.split(b"data:")
                for line in lines:
                    if line := line.strip():
                        if line == b"[DONE]":
                            break
                        if line == b"[DONE][LIMIT_CONVERSATION]":
                            raise ConversationLimitException("ERR_CONVERSATION_LIMIT")
                        x = json_loads(line)
                        if isinstance(x, dict):
                            if x.get("action") == "error":
                                err_message = x.get("type", "")
                                if x.get("status") == 429:
                                    raise (
                                        ConversationLimitException(err_message)
                                        if err_message == "ERR_CONVERSATION_LIMIT"
                                        else RatelimitException(err_message)
                                    )
                                raise DuckAIException(err_message)
                            elif message := x.get("message"):
                                chunks.append(message)
                                self._chat_tokens_count += 1
                                yield message
        except Exception as ex:
            raise DuckAIException(f"chat_yield() {type(ex).__name__}: {ex}") from ex

        result = "".join(chunks)
        self._chat_messages.append({"role": "assistant", "content": result})

    def chat(self, keywords: str, model: str = "gpt-4o-mini", timeout: int = 30) -> str:
        """Initiates a chat session with DuckDuckGo AI.

        Args:
            keywords (str): The initial message or question to send to the AI.
            model (str): The model to use: "gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
                "o3-mini", "mistral-small-3". Defaults to "gpt-4o-mini".
            timeout (int): Timeout value for the HTTP client. Defaults to 30.

        Returns:
            str: The response from the AI.
        """
        answer_generator = self.chat_yield(keywords, model, timeout)
        return "".join(answer_generator)
