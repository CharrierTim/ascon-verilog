"""Sphinx configuration file."""
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

base_path = (Path(__file__).parent.parent.parent / "src/bench/").resolve()
sys.path.insert(0, str(base_path))
for path in base_path.rglob("*"):
    if path.is_dir():
        sys.path.insert(0, str(path))

project = "ascon-verilog"
copyright = "2025, Timothée Charrier"  # noqa: A001
author = "Timothée Charrier"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx.ext.autosummary",
    "numpydoc",
]

templates_path: list[str] = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path: list[str] = ["_static"]

# -- Options for numpydoc ----------------------------------------------------
# https://numpydoc.readthedocs.io/en/latest/format.html

numpydoc_class_members_toctree = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

html_theme_options = {
    "show_prev_next": False,
    "navbar_end": ["theme-switcher", "navbar-icon-links.html"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/CharrierTim/ascon-verilog",
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
    ],
}

html_sidebars = {
    "**": [],
}
html_context = {
    "default_mode": "light",
}

html_title = f"{project} v{release} Manual"
html_last_updated_fmt = "%b %d, %Y"
