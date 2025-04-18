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

The DuckAI classes is used to retrieve chat results from DuckDuckGo.com.
```python3
class DuckAI:
    """duckai class to get search results from duckduckgo.com

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
duckai = DuckAI(proxy="tb", timeout=20)  # "tb" is an alias for "socks5://127.0.0.1:9150"
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
```
***Example***
```python
results = DuckAI().chat("summarize Daniel Defoe's The Consolidator", model='claude-3-haiku')

# There is also `chat_yield` generator which yields chunks while a response is being processed:
for x in DuckAI().chat_yield("How Do Airplanes Fly", model='llama-3.3-70b'):
    print(x)
```

[Go To TOP](#TOP)

## Disclaimer

This library is not affiliated with DuckDuckGo and is for educational purposes only. It is not intended for commercial use or any purpose that violates DuckDuckGo's Terms of Service. By using this library, you acknowledge that you will not use it in a way that infringes on DuckDuckGo's terms. The official DuckDuckGo website can be found at https://duckduckgo.com.
