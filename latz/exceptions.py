"""
Our exception hierarchy:

* LatzError
    - ImageAPIError
"""
from __future__ import annotations


class LatzError(Exception):
    """Base exception for all latz errors"""


class ImageAPIError(Exception):
    """
    Exception used for raising while encountering issues during image API operations
    """

    def __init__(self, message, original: Exception | None = None):
        self.message = message
        self.original = original


class ConfigError(Exception):
    pass
