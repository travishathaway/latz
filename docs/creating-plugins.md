# Creating Plugins

[imgur-docs]: https://apidocs.imgur.com/
[poetry]: https://python-poetry.org/
[pydantic]: https://docs.pydantic.dev/
[pydantic-dynamic-models]: https://docs.pydantic.dev/usage/models/#dynamic-model-creation
[latz_imgur_main]: https://github.com/travishathaway/latz-imgur/blob/main/latz_imgur/main.py

This is a guide that will show you how to create your own latz image api plugins.
To illustrate how to do this, we will write a plugin for the Imgur image search API.

## Requirements

To follow along, you will need to create a Imgur account and register an application
via their web interface. Once complete, save the `client_id` as we will be using that
for this application. Head over to [their documentation][imgur-docs] for more information.

For managing dependencies and publishing to PyPI, we use the tool [poetry][poetry]. Please
install and configure this if you do not currently have it on your computer.

## Setting up our environment

Before writing a plugin for latz, we first need to create a directory for our project.
To do so, we run the following commands:

```bash
mkdir latz-imgur && cd latz-imgur
poetry init \
  --name=latz-imgur \
  --description="Imgur plugin for latz" \
  --author="Your name <your-email@example.com" \
  --python="^3.10" \
  --dependencies="latz" \
  --dependencies="pydantic" \
  --dependencies="httpx" \
  --no-interaction
```

This will create a `pyproject.toml` file for us that we can use to create our development
environment with following commands:

```bash
# Install project dependencies including "latz"
poetry install
# Start a shell where we have access to all of our project dependencies
poetry shell
```

## Create the plugin

At this point, you can open the folder (`latz-imgur` in our example) with your favorite
IDE or text editor. The first thing we need to do is create a Python module called `latz_imgur`
at the top of the directory structure. Be sure this folder contains an `__init__.py` file
so that it is recognized as a Python module 😉.

In that new Python module, we create a new file called `main.py`.  This file will contain all the
code necessary for our Imgur plugin. Below, we go through each section of this file. Feel free
to incrementally add to this file as your go along or download the full version
here: [latz_imgur/main.py][latz_imgur_main].

### Plugin configuration

Each new image search backend may require a different set of settings. Latz recognizes this and
therefore allows you to dynamically add any new settings you wish. For our application, we add
the required `access_key` setting that the Imgur API requires.

We define these extra settings as [pydantic][pydantic] models.

```python
from pydantic import BaseModel, Field

# Module level constant declaring the name of our plugin
PLUGIN_NAME = "imgur"


class ImgurBackendConfig(BaseModel):
    """
    Imgur requires the usage of an ``access_key`` when using their API.
    We expose these settings here so users of the CLI tool can use it.
    """

    access_key: str = Field(description="Access key for the Imgur API")


# Module level constant declaring all configuration settings for this plugin
CONFIG_FIELDS = {
    f"{PLUGIN_NAME}": (ImgurBackendConfig, {"access_key": ""})
}
```

<!-- TODO: link to this dynamic model code in the following admonition -->

!!! note
    Latz uses this `CONFIG_FIELDS` dictionary to dynamically generate its own `AppConfig`
    model at runtime. Check out [Dynamic model creation][pydantic-dynamic-models] in the
    [pydantic docs][pydantic] to learn more.

### Image search API

Now that our plugin is able to gather the configuration settings neccesary to run, we
need to write the actual search API code. Below, is our `ImgurImageAPI` in its entirety:

```python
import urllib.parse
from typing import Any

import httpx

from latz.image import ImageAPI, ImageSearchResult, ImageSearchResultSet


class ImgurImageAPI(ImageAPI):
    """
    Implementation of ImageAPI for use with the Imgur API:
        https://apidocs.imgur.com/
    """

    #: Base URL for the Imgur API
    base_url = "https://api.imgur.com/3/"

    #: Endpoint used for searching images
    search_endpoint = "gallery/search"

    def __init__(self, client_id: str, client: httpx.Client):
        """
        We use this initialization method to properly configure
        the ``httpx.Client`` object
        """
        self._client_id = client_id
        self._headers = {"Authorization": f"Client-ID {client_id}"}
        self._client = client
        self._client.headers = httpx.Headers(self._headers)

    @staticmethod
    def _get_image_search_result_record(
            record_image: dict[str, Any]
    ) -> ImageSearchResult:
        """
        Provided a sequence of record images, returns a tuple of
        ``ImageSearchResult`` objects
        """
        return ImageSearchResult(
            url=record_image.get("link"),
            width=record_image.get("width"),
            height=record_image.get("height")
        )

    def search(self, query: str) -> ImageSearchResultSet:
        """
        Find images based on a ``query`` and return an ``ImageSearchResultSet``
        """
        search_url = urllib.parse.urljoin(self.base_url, self.search_endpoint)

        resp = self._client.get(search_url, params={"q": query})
        resp.raise_for_status()

        json_data = resp.json()

        search_results = tuple(
            self._get_image_search_result_record(record_image)
            for record in json_data.get("data", tuple())
            for record_image in record.get("images", tuple())
        )

        return ImageSearchResultSet(
            search_results, len(json_data.get("data", tuple()))
        )
```

The first thing you need to understand about the code above is that our `ImgurImageAPI` object
is a subclass of `latz.image.ImageAPI` abstract base class. This means it will need to define
all the methods that this abstract base class requires. For this particular abstract base class
it is just the `search` method.
