![Python >= 3.9](https://img.shields.io/badge/python->=3.9-red.svg) [![](https://badge.fury.io/py/duckai.svg)](https://pypi.org/project/duckai)
# duckai<a name="TOP"></a>

AI chat using the DuckDuckGo.com search engine.

‼️ Chat ratelimit: `1 request per 15 seconds`

*Supported OS*:

    🐧 Linux: amd64
    🪟 Windows: amd64
    🍏 macOS: amd64, arm64

## Table of Contents
* [Install](#install)
* [CLI version](#cli-version)
* [DuckAI class](#duckai-class)
* [Proxy](#proxy)
* [Exceptions](#exceptions)
* [1. chat() - AI chat](#1-chat---ai-chat)
* [2. chat_yield() - AI chat generator](#2-chat_yield---ai-chat-generator)
* [Disclaimer](#disclaimer)

## Install

```python
pip install -U duckai
```

## CLI version

```python3
duckai --help
```
CLI examples:
```python3
duckai chat
```
‼️ Press `Esc`, then `Enter`, or `Alt+Enter` to send a message.‼️

[Go To TOP](#TOP)


## DuckAI class

The DuckAI class is used to retrieve chat results from DuckDuckGo.com and preserves the context of the conversation by sending the contents of all previous requests and responses with each new call to the `chat` or `chat_yield` function.
```python3
class DuckAI:
    """Class to chat with DuckDuckGo AI

    Args:
        proxy (str, optional): proxy for the HTTP client, supports http/https/socks5 protocols.
            example: "http://user:pass@example.com:3128". Defaults to None.
        timeout (int, optional): Timeout value for the HTTP client. Defaults to 10.
        verify (bool): SSL verification when making the request. Defaults to True.
    """
```

Here is an example of initializing the DuckAI class.
```python3
from duckai import DuckAI

results = DuckAI().chat("python programming")
print(results)
```

[Go To TOP](#TOP)

## Proxy

Package supports http/https/socks proxies. Example: `http://user:pass@example.com:3128`.
Use a rotating proxy. Otherwise, use a new proxy with each DuckAI class initialization.

*1. The easiest way. Launch the Tor Browser*
```python3
duckai = DuckAI(proxy="socks5://127.0.0.1:9150", timeout=20)
results = duckai.chat("something you need", model="mistral-small-3")
```
*2. Use any proxy server* (*example with [iproyal rotating residential proxies](https://iproyal.com?r=residential_proxies)*)
```python3
duckai = DuckAI(proxy="socks5h://user:password@geo.iproyal.com:32325", timeout=20)
results = duckai.chat("something you need", model="mistral-small-3")
```
*3. The proxy can also be set using the `DUCKAI_PROXY` environment variable.*
```python3
export DUCKAI_PROXY="socks5h://user:password@geo.iproyal.com:32325"
```

[Go To TOP](#TOP)

## Exceptions

```python
from duckai.exceptions import (
    ConversationLimitException,
    DuckAIException,
    RatelimitException,
    TimeoutException,
)
```

Exceptions:
- `DuckAIException`: Base exception for duckai errors.
- `RatelimitException`: Inherits from DuckAIException, raised for exceeding API request rate limits.
- `TimeoutException`: Inherits from DuckAIException, raised for API request timeouts.
- `ConversationLimitException`: Inherits from DuckAIException, raised for conversation limit during API requests to AI endpoint.

[Go To TOP](#TOP)

## 1. chat() - AI chat

```python
def chat(keywords: str, model: str = "gpt-4o-mini", timeout: int = 30) -> str:
    """Chat with DuckDuckGo AI.

    Args:
        keywords (str): The initial message or question to send to the AI.
        model (str): The model to use: "gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
            "o3-mini", "mistral-small-3". Defaults to "gpt-4o-mini".
        timeout (int): Timeout value for the HTTP client. Defaults to 30.

    Returns:
        str: The response from the AI.
    """
```
***Example***
```python
from duckai import DuckAI

duckai = DuckAI()
results = duckai.chat("summarize Daniel Defoe's The Consolidator", model='claude-3-haiku')
```

## 2. chat_yield() - AI chat generator

Generator which yields chunks while a response is being processed

```python
def chat_yield(self, keywords: str, model: str = "gpt-4o-mini", timeout: float = 30) -> Iterator[str]:
    """Chat with DuckDuckGo AI generator.

    Args:
        keywords (str): The initial message or question to send to the AI.
        model (str): The model to use: "gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
            "o3-mini", "mistral-small-3". Defaults to "gpt-4o-mini".
        timeout (int): Timeout value for the HTTP client. Defaults to 20.

    Yields:
        str: Chunks of the response from the AI.
    """
```
***Example***
```python
from duckai import DuckAI

duckai = DuckAI()
for x in duckai.chat_yield("How Do Airplanes Fly", model='llama-3.3-70b'):
    print(x)
```

[Go To TOP](#TOP)

## Disclaimer

This library is not affiliated with DuckDuckGo and is for educational purposes only. It is not intended for commercial use or any purpose that violates DuckDuckGo's Terms of Service. By using this library, you acknowledge that you will not use it in a way that infringes on DuckDuckGo's terms. The official DuckDuckGo website can be found at https://duckduckgo.com.
