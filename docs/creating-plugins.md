# Creating Plugins

[imgur-docs]: https://apidocs.imgur.com/
[poetry]: https://python-poetry.org/
[pydantic]: https://docs.pydantic.dev/
[httpx]: http://localhost
[latz-imgur]: https://github.com/travishathaway/latz-imgur
[pydantic-dynamic-models]: https://docs.pydantic.dev/usage/models/#dynamic-model-creation
[latz_imgur_main]: https://github.com/travishathaway/latz-imgur/blob/main/latz_imgur/main.py
[python-protocol]: https://docs.python.org/


This is a guide that will show you how to create your own latz image API plugin.
To illustrate how to do this, we will write a plugin for the Imgur image search API.
We be starting from just an empty directory and using [poetry][poetry] packaging tool
to show how you can easily upload your plugin to PyPI once we are finished.

Check out [latz-imgur on GitHub][latz-imgur] if you would like to skip ahead and browse
the final working example.

## Requirements

To follow along, you will need to create an Imgur account and register an application
via their web interface. Once complete, save the `client_id` you receive as we will be using
that for this application. Head over to [their documentation][imgur-docs] for more information.

For managing dependencies and publishing to PyPI, we use the tool [poetry][poetry]. Please
install and configure this if you do not currently have it on your computer.

## Setting up our environment

The first steps necessary are creating a directory for our project and adding a `pyproject.toml`
file. To do so, we run the following commands:

```bash
mkdir latz-imgur && cd latz-imgur

poetry init \
  --name=latz-imgur \
  --description="Imgur plugin for latz" \
  --author="Your name <your-email@example.com" \
  --python="^3.10" \
  --dependency="latz" \
  --dependency="pydantic" \
  --dependency="httpx" \
  --no-interaction
```

!!! note
    The extra dependencies we install are `latz`, `pydantic` and `httpx`. You will see exactly how we
    use all three of these dependencies below.

Now that we have a directory and a `pyproject.toml` file, we can use the following commands to initialize
our development environment:

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

In that new Python module, we create a file called `main.py`.  This file will contain all the
code necessary for our Imgur plugin. Below, we go through each section of this file. Feel free
to incrementally add to this file as your go along or download the full version
here: [latz_imgur/main.py][latz_imgur_main].

### Plugin configuration

Each new image API plugin may require a different set of settings. Latz recognizes this and
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
    We expose these settings here so users of the CLI tool can configure it
    themselves.
    """

    access_key: str = Field(description="Access key for the Imgur API")


# Module level constant declaring all configuration settings for this plugin
CONFIG_FIELDS = {
    PLUGIN_NAME: (ImgurBackendConfig, {"access_key": ""})
}
```

<!-- TODO: link to this dynamic model code in the following admonition -->

!!! note
    Latz uses this `CONFIG_FIELDS` dictionary to dynamically generate its own `AppConfig`
    model at runtime. Check out [Dynamic model creation][pydantic-dynamic-models] in the
    [pydantic docs][pydantic] to learn more.

### Image search API

Now that our plugin is able to gather the configuration settings necessary to run (i.e. the
"access_key" we get from Imgur), we are ready to write the actual search API code. Latz requires
us to first write a class a that implements the [protocol][python-protocol] class
[`ImageAPI`][latz.image.ImageAPI].
The only thing that this protocol requires us to do is define a `search` method which returns the
`ImageSearchResultSet` type. Furthermore, the `ImageSearchResultSet` type must be instantiated
with a sequence of `ImageSearchResult` .

Tying all of these requirements together, below is an example of what this class could look like:

!!! note
    Click on the tool tips in the code to learn more :thinking: :books:

```python title="latz_imgur/main.py"

import urllib.parse
from typing import Any

import httpx

from latz.image import ImageSearchResult, ImageSearchResultSet


#: Base URL for the Imgur API
BASE_URL = "https://api.imgur.com/3/"

#: Endpoint used for searching images
SEARCH_ENDPOINT = "gallery/search"

class ImgurImageAPI: # (1)
    """
    Implementation of ImageAPI for use with the Imgur API:
        https://apidocs.imgur.com/
    """

    def __init__(self, client: httpx.Client):
        """
        Attach a `httpx.Client` object to our API
        """
        self._client = client

    @staticmethod
    def _get_image_search_result_record(
            record_image: dict[str, Any]
    ) -> ImageSearchResult:  # (2)
        """
        Helper method used to create `ImageSearchResult` objects
        """
        return ImageSearchResult(
            url=record_image.get("link"),
            width=record_image.get("width"),
            height=record_image.get("height")
        )

    def search(self, query: str) -> ImageSearchResultSet: # (3)
        """
        Find images based on a `query` and return an `ImageSearchResultSet`
        """
        search_url = urllib.parse.urljoin(BASE_URL, SEARCH_ENDPOINT)

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

1. The API class defined here accepts a `httpx.Client` object so that it can query
   the Imgur API. To properly function as a latz plugin, this class must also define a
   `search` method (see below), which is specified by the latz [`ImageAPI`][latz.image.ImageAPI]
   protocol.
2. [`ImageSearchResult`][latz.image.ImageSearchResult] is a special type defined by latz.
   Using this type helps ensure the result you return will be properly rendered.
3. Here, we implement the `search` method required by the [`ImageAPI`][latz.image.ImageAPI]
   protocol. [`ImageSearchResultSet`][latz.image.ImageSearchResultSet] is a type defined
   by latz to help organize results returned by the [`ImageAPI`][latz.image.ImageAPI] classes.


### Image API context manager

We now have an `ImgurImageAPI` class that is capable of querying the Imgur API and returning
the types of results that latz needs. You will notice that this class accepts a `httpx.Client`
object which it uses to make the actual HTTP requests. We now need to write the code that
will instantiate this object and pass it into the `ImgurImageAPI` class.

To do this, we create a context manager. This context manager will be registered with latz
itself and this is how the application will make a new connection objects and run queries.
Below, is an implementation of this context manager using Python's `contextlib` module:

```python title="latz_imgur/main.py"
from contextlib import contextmanager
from typing import Iterator

import httpx


@contextmanager
def imgur_context_manager(config) -> Iterator[ImgurImageAPI]:  # (1)
    """
    Context manager that returns the `ImgurImageAPI` we wish to use

    This specific context manager handles setting up and tearing down the `httpx.Client`
    connection that we use in this plugin.
    """
    client = httpx.Client()
    client.headers = httpx.Headers({ # (2)
        "Authorization": f"Client-ID {config.backend_settings.imgur.access_key}"
    })

    try:
        yield ImgurImageAPI(client)
    finally:
        client.close() # (3)
```

1. All image API context managers will receive a `config` object holding applicable settings for
   the configured image API backend. This context manager must also yield an instantiated object
   that implements the [`ImageAPI`][latz.image.ImageAPI].
2. These are the headers that the Imgur API expects. We are able to retrieve the `client_id` from
   `config` object that is pass into this function.
3. We use context managers so that we can perform any clean up actions necessary


!!! note
    **Why use a context manager?**

    Using a context manager allows plugin authors to use libraries which made need to perform clean
    up actions on connections made. This is not only important
    for the `httpx` library but could come in handy if we ever decide to implement a plugin using a
    database connections. Python's also `contextlib.contextmanager` decorator makes these fairly
    simple to define, reducing the complexity for plugin authors.


### Registering everything with latz

We are now at the final step: registering everything we have written with latz. To do this,
we need to use the `latz.plugins.hookimpl` decorator to register our plugins. We do this
by decorating a function called `image_api` that returns a `ImageAPIPlugin` type. The
`ImageAPIPlugin` type is an object which has three fields:

- `name`: name of the plugin that users will use to specify it their configuraiton
- `image_api_context_manager`: context manager that returns the [`ImageAPI`][latz.image.ImageAPI]
   class that we defined.t
- `config_fields`: config fields that we defined in the first step. This what allows latz to
   register these settings and make them available to users.

Here is what this function looks like:

```python title="latz_imgur/main.py"
from latz.plugins import hookimpl, ImageAPIPlugin


@hookimpl
def image_api():
    """
    Registers our Imgur image API backend
    """
    return ImageAPIPlugin(
        name=PLUGIN_NAME,
        image_api_context_manager=imgur_context_manager,
        config_fields=CONFIG_FIELDS,
    )
```

## Wrapping up

In this guide, we showed how to create a latz image API plugin. The most important steps
were:

1. Creating our configuration fields, so we can allow users of the plugin to define necessary
   access tokens
2. Creating the actual `ImgurImageAPI` object which implemented the [`ImageAPI`][latz.image.ImageAPI]
   protocol.
3. Creating the image API context manager for creating our HTTP client and `ImgurImageAPI` object
4. Tying everything together by creating an `image_api` function decorated by the `latz.plugins.hookimpl`.
   This function's only responsibility is to return an `ImageAPIPlugin` object that combines everything
   we have written in this module so far.

When adapting this code to write future plugins, it is important to realize that you may not
always have to define configuration settings (perhaps your API is completely open). But, the things
that will remain constant is the [`ImageAPI`][latz.image.ImageAPI] protocol. This protocol is a contract
between your plugin and latz, and both parties must adhere to it for a smooth ride :sunglasses: 🚗.

Happy plugin writing ✌️
