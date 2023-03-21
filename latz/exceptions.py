"""
Our exception hierarchy:

* LatzError
    - SearchBackendError
    - ConfigError
"""
from __future__ import annotations


class LatzError(Exception):
    """Base exception for all latz errors"""


class SearchBackendError(LatzError):
    """
    Exception used for raising while encountering issues during image API operations
    """

    def __init__(self, message, original: Exception | None = None):
        self.message = message
        self.original = original


class ConfigError(LatzError):
    pass
