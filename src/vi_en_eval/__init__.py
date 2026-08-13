"""Vietnamese-English LLM evaluation toolkit."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("vi-en-llm-evaluation-toolkit")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
