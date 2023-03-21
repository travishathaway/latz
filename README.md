# Overview

[pluggy]: https://pluggy.readthedocs.io/en/stable/
[click]: https://click.palletsprojects.com/
[pydantic]: https://docs.pydantic.dev/
[rich]: https://rich.readthedocs.io/
[anaconda.org]: https://anaconda.org
[latz-imgur]: https://github.com/travishathaway/latz-imgur
[creating-plugins]: creating-plugins

This is a command line tool used for retrieving images from various image
search backends (e.g. Unsplash, Google). This tool is primarily developed for educational purposes
to show people how to develop plugin friendly Python applications. Furthermore,
it is an example project that shows how to effectively pair a handful of
popular Python libraries to write command line applications.

To facilitate our plugin architecture, the [pluggy][pluggy] library is used.
Other libraries used include the following:

- [click][click]: used for structuring the command line application 🖱 💻
- [pydantic][pydantic]: used for handling configuration file validation 🗃
- [rich][rich]: used for UX/UI elements and generally making the application more pretty 🌈

### Why "latz"

"latz" is short and easy to type! This is super important when writing CLI programs.
I also might add a geolocation search feature, so it is a reference  to the word "latitude".

## Quick Start

### Installation

latz is available for install either on PyPI:

```bash
# Run from a new virtual environment
$ pip install latz
```

or my own [anaconda.org][anaconda.org] channel:

```bash
$ conda create -n latz 'thath::latz'
```

If you are interested in tinkering around with the code yourself, you can also
run it locally:

```bash
$ git clone git@github.com:/travishathaway/latz.git
$ cd latz
# Create a virtual environment however you like..
$ pip install -e .
```

### Usage

Latz comes initially configured with the "unsplash" image search backend. To use this,
you will need to create an Unsplash account and create a test application. After getting
your "access_key", you can set this value by running this command:

```bash
$ latz config set search_backend_settings.unsplash.access_key=<YOUR_ACCESS_KEY>
```

Once this is configured, you can search Unsplash for bunny pictures:

```bash
$ latz search "bunny"
[
    ImageSearchResultSet(
        results=(
            ImageSearchResult(
                url='https://unsplash.com/photos/u_kMWN-BWyU/download?ixid=MnwzOTMwOTR8MHwxfHNlYXJjaHwxfHxidW5ueXxlbnwwfHx8fDE2Nzk0MTA2NzQ',
                width=3456,
                height=5184
            ),
            # ... results truncated
        ),
        total_number_results=10,
        search_backend='unsplash'
    )
]
```

### Configuring

The configuration for latz is stored in your home direct and is in the JSON format.
Below is a what a default version of this configuration looks like:

```json
{
  "search_backends": [
    "unsplash"
  ],
  "search_backend_settings": {
    "placeholder": {
      "type": "kitten"
    },
    "unsplash": {
      "access_key": "your-access-key"
    }
  }
}
```

_Latz will also search in your current working directory for a `.latz.json` file and use this in your configuration.
Files in the current working directory will be prioritized over your home directory location._

To see other available image search backends, see [Available image search backends](#available-image-search-backends) below.

### Available image search backends

Here are a list of the available search backends:

#### Built-in

- "unsplash"
- "placeholder"

#### Third-party

- [latz-imgur][latz-imgur]

### How to extend and write your own image search backend

Please see the [creating plugins][creating-plugins] guide in the documentation.
