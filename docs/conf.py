"""Build the application documentation against its test configuration."""

import os
import sys
from importlib.metadata import version as package_version
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ["DJANGO_SETTINGS_MODULE"] = "rola.test_settings"
django.setup()

project = "Rola"
release = package_version("rola")
version = release
author = "Domen Blenkuš"
copyright = "Domen Blenkuš"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx.ext.viewcode"]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "CHANGELOG.rst"]
html_theme = "sphinx_rtd_theme"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "django": ("https://docs.djangoproject.com/en/stable/", None),
}
