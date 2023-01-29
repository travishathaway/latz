# TODO

This is an informal way of keeping track of small things I need to do
to this repository.

### Add py.typed stubs

More information here
- https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports

This is primarily so that plugin libraries can properly run mypy against their
projects.

This article helped me finally figure everything out:

https://dev.to/whtsky/don-t-forget-py-typed-for-your-typed-python-package-2aa3


### Starting to think that type hints aren't the best way to validate plugins 😭

Up to this point, I was leaning heavily on type hints to help me validate
user defined plugins. But, I think this isn't really the best approach. Ultimately,
these checkers are optional, and not everyone might be interested in using them.

I think it will be necessary to write an actual plugin validation piece to
make sure that authors have written their plugins correctly. I hope it won't
be that hard. It will make the user experience better though when writing the
plugins.
