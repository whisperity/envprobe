Contribution guidelines
=======================


Python style
------------

We use [flake8](http://flake8.pycqa.org/en/latest/) to check code style and
perform linting.

In addition to the general rules of `flake8`, please keep the following
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
