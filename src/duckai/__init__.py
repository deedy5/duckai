"""duckai.

AI chat using the DuckDuckGo.com search engine.
"""

import logging

from .duckai import DuckAI

__all__ = ["DuckAI", "cli"]


# A do-nothing logging handler
# https://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("duckai").addHandler(logging.NullHandler())
