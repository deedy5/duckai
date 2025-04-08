from mypyc.build import mypycify
from setuptools import setup

ext_modules = mypycify(
    [
        "src/duckai/libs/utils_chat.py",
    ],
    debug_level="0",
)


setup(
    name="duckai",
    ext_modules=ext_modules,  # type: ignore
)
