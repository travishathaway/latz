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

### Configuring

latz comes initially configured with the "unsplash" image search backend. To use this,
you will need to create an Unsplash account and create a test application. After getting
your "access_key", you will need to configure it by adding it to your `.latz.json`
config file. An example is show below:

```json
{
  "backend": "unsplash",
  "backend_settings": {
    "unsplash": {
      "access_key": "your-access-key"
    }
  }
}
```

_This file must be stored in your home directory or your current working directory._

To see other available image search backends, see [Available image search backends](#available-image-search-backends) below.

### Usage



### Available image search backends

Here are a list of the available search backends:

#### Built-in

- "unsplash"
- "placeholder"

#### Third-party

- [latz-imgur][latz-imgur]

### How to extend and write your own image search backend

Please see the [creating plugins][creating-plugins] guide in the documentation.
