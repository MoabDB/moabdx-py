# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from moabdb import __version__
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MoabDB'
year = datetime.datetime.now().date().year
copyright = f'2022–{year}'
author = 'MoabDB'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.ifconfig',
              'sphinx.ext.extlinks']
source_suffix = ['.rst']
master_doc = 'index'
exclude_patterns = ['_build']
highlight_language = 'python3'
release = __version__



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = f'<strong>{project}</strong> <i>{release}</i>'
html_baseurl = 'https://docs.moabdb.com/'
html_static_path = ['_static']
html_css_files = ["custom.css"]
html_logo = "_static/images/MoabDB.png"

html_use_smartypants = True
html_use_modindex = False
html_use_index = False
html_show_sourcelink = False

# html_theme_options = {
#     'light_logo': 'pelican-logo.svg',
#     'dark_logo': 'pelican-logo.svg',
#     'navigation_with_keys': True,
# }

html_theme_options = {
    "light_css_variables": {
        "color-background-secondary": 'rgba(248, 249, 251, 0)',
        "color-brand-content": "#7C4DFF",
    },
}

favicons = [
    {
        "rel": "icon",
        "static-file": "favicons/favicon-32x32.png",
        "type": "image/png",
    },
    {
        "rel": "icon",
        "sizes": "16x16",
        'static-file': "favicons/favicon-16x16.png",
        "type": "image/png",
    },
    {
        "rel": "icon",
        "sizes": "32x32",
        "static-file": "favicons/favicon-32x32.png",
        "type": "image/png",
    },
    {
        "rel": "apple-touch-icon",
        "sizes": "180x180",
        "static-file": "favicons/apple-touch-icon.png",
        "type": "image/png",
    },
    {
        "rel": "android-chrome",
        "sizes": "192x192",
        "static-file": "favicons/android-chrome-192x192.png",
        "type": "image/png",
    },
    {
        "rel": "android-chrome",
        "sizes": "512x512",
        "static-file": "favicons/android-chrome-512x512.png",
        "type": "image/png",
    },
]
