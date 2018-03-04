Contribution guidelines
=======================

Python style
------------
We use [pycodestyle](https://pypi.python.org/pypi/pycodestyle/) to
automatically check our coding style.

In addition to the general rules of `pycodestyle`, please keep the following
rules while writing your code:

  * Comments must be whole sentences, beginning with a capital letter and
    ending with a closing `.`.

### Order of `import` commands
Order your `import` commands according to as follows:

  1. **System-wide** imports come first and foremost, e.g.
    `import multiprocessing`.
  2. _(Empty line for readability)_
  3. Imports from the library modules of `envprobe`.

Between each of these _levels_, imports are sorted alphabetically on the
importing module's name, even if we only import a single class or function from
it.
