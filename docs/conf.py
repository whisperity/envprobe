# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from datetime import date

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------

project = "Envprobe"
copyright = "2018-{0}, Whisperity".format(date.today().year)
author = "Whisperity"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.autosummary",
        "sphinx.ext.intersphinx",
        "sphinx.ext.napoleon",
        "sphinx_rtd_theme"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for AutoDoc -----------------------------------------------------

# A boolean that decides whether module names are prepended to all object names
# (for object types where a "module" of some kind is defined),
# e.g. for py:function directives.
add_module_names = False

# This value selects what content will be inserted into the main body of an
# autoclass directive. The possible values are:
#
#  "class"
#    Only the class’ docstring is inserted. This is the default. You can still
#    document __init__ as a separate method using automethod or the members
#    option to autoclass.
#
#  "both"
#    Both the class’ and the __init__ method’s docstring are concatenated and
#    inserted.
#
#  "init"
#    Only the __init__ method’s docstring is inserted.
autoclass_content = "both"


# -- Options for AutoSummary -------------------------------------------------

# Boolean indicating whether to scan all found documents for autosummary
# directives, and to generate stub pages for each.
autosummary_generate = True


# -- Options for Napoleon ----------------------------------------------------

# True to use the .. admonition:: directive for Notes sections.
# False to use the .. rubric:: directive instead.
napoleon_use_admonition_for_notes = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If true, the reST sources are included in the HTML build as _sources/name.
html_copy_source = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# The style name to use for Pygments highlighting of source code.
pygments_style = "sphinx"
