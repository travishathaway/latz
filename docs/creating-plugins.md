# Creating Plugins

[imgur-docs]: https://apidocs.imgur.com/
[poetry]: https://python-poetry.org/
[pydantic]: https://docs.pydantic.dev/
[httpx]: http://localhost
[latz-imgur]: https://github.com/travishathaway/latz-imgur
[pydantic-dynamic-models]: https://docs.pydantic.dev/usage/models/#dynamic-model-creation
[latz_imgur_main]: https://github.com/travishathaway/latz-imgur/blob/main/latz_imgur/main.py
[python-protocol]: https://docs.python.org/
[httpx-async-client]: https://www.python-httpx.org/api/#asyncclient


This guide will show you how to create your own latz search backend hook.
These search backend hooks allow you to add additional image search APIs to latz.
Once complete, you will be able to use these new search backends with the `latz search`
command.

Check out [latz-imgur on GitHub][latz-imgur] if you would like to skip ahead and browse
the final working example.

## Requirements

To follow along, you will need to create an Imgur account and register an application
via their web interface. Once complete, save the `client_id` you receive as we will be using
that for this application. Head over to [their documentation][imgur-docs] for more information.

For managing dependencies and to make it easier to publish to PyPI later, we use the tool
[poetry][poetry]. Please install and configure this if you do not currently have it on your computer.

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
```

!!! note
    Latz uses this `ImgurBackendConfig` model to dynamically generate its own `AppConfig`
    model at runtime. Check out [Dynamic model creation][pydantic-dynamic-models] in the
    [pydantic docs][pydantic] to learn more.

### Search backend hook function

Now that our plugin is able to gather the configuration settings necessary to run (i.e. the
"access_key" we get from Imgur), we are ready to write the actual search API code. To make this
work, we need to define an async search function that returns an `ImageSearchResultSet`.
Latz will pass an instance of the [httpx.AsyncClient][httpx-async-client], the application
configuration and the search query to this function for us.

Below is an example of what this could look like:

!!! note
    Click on the tool tips in the code to learn more :thinking: :books:

```python title="latz_imgur/main.py"
import urllib.parse

import httpx

from latz.exceptions import SearchBackendError
from latz.image import ImageSearchResultSet, ImageSearchResult

#: Base URL for the Imgur API
BASE_URL = "https://api.imgur.com/3/"

#: Endpoint used for searching images
SEARCH_ENDPOINT = urllib.parse.urljoin(BASE_URL, "gallery/search")

async def search(client, config, query: str) -> ImageSearchResultSet: # (1)
    """
    Search hook that will be invoked by latz while invoking the "search" command
    """
    client.headers = httpx.Headers({
        "Authorization": f"Client-ID {config.search_backend_settings.imgur.access_key}"
    })
    json_data = await _get(client, SEARCH_ENDPOINT, query)

    search_results = tuple(
        ImageSearchResult(  # (2)
            url=record_image.get("link"),
            width=record_image.get("width"),
            height=record_image.get("height")
        )
        for record in json_data.get("data", tuple())
        for record_image in record.get("images", tuple())
    )

    return ImageSearchResultSet(
        search_results, len(search_results), search_backend=PLUGIN_NAME
    )

async def _get(client: httpx.AsyncClient, url: str, query: str) -> dict:
    """
    Wraps `client.get` call in a try, except so that we raise
    an application specific exception instead.

    :raises SearchBackendError: Encountered during problems querying the API
    """
    try:
        resp = await client.get(url, params={"query": query})
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise SearchBackendError(str(exc), original=exc)

    json_data = resp.json()

    if not isinstance(json_data, dict):
        raise SearchBackendError("Received malformed response from search backend")

    return json_data
```

1. The arguments passed to this function give you everything you need to make a search
   request. The `client` is a [httpx.AsyncClient][httpx-async-client], the `config` object
   is the application configuration and the `query` string is the search string passed in
   from the command line.
2. [`ImageSearchResult`][latz.image.ImageSearchResult] is a special type defined by latz.
   Using this type helps ensure the result you return will be properly rendered.

### Registering everything with latz

We are now at the final step: registering everything we have written with latz. To do this,
we need to use the `latz.plugins.hookimpl` decorator to register our plugins. We do this
by decorating a function called `search_backend` that returns a `SearchBackendHook` object.
The `SearchBackendHook` object is an object which has three fields:

- `name`: name of the plugin that users will use to specify it their configuration
- `search`: async function that will be called to search for images
- `config_fields`: Pydantic model representing the config fields we want to expose in the
   application

Here is what this function looks like:

```python title="latz_imgur/main.py"
from latz.plugins import hookimpl, SearchBackendHook

@hookimpl
def search_backend():
    """
    Registers our Imgur image API backend
    """
    return SearchBackendHook(
        name=PLUGIN_NAME,
        search=search,
        config_fields=ImgurBackendConfig(access_key=""),
    )
```

## Wrapping up

In this guide, we showed how to create a latz search backend hook. The most important steps
were:

1. Creating our configuration fields, so we can allow users of the plugin to define necessary
   access tokens
2. Creating the `search` function which returns an [`ImageSearchResultSet`][latz.image.ImageSearchResultSet]
   object.
3. Tying everything together by creating an `search_backend` function decorated by `latz.plugins.hookimpl`.
   This function's only responsibility is to return an [`SearchBackendHook`][latz.plugins.hookspec.SearchBackendHook]
   object that combines everything we have written in this module so far.

Thanks for following along and happy plugin writing ✌️
