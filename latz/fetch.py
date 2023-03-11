"""
Module which holds everything related to making networking requests for this application.
"""

import httpx


def get_fetch_client() -> httpx.Client:
    """
    Returns a httpx.Client object to use for making network requests.

    Note: this is currently pretty sparse but includes room to grow and allows us
    to add settings we wish to apply to all network requests for this particular
    application in the future.
    """
    return httpx.Client()
