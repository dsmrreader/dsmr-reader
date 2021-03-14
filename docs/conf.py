# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import datetime


# -- Project information -----------------------------------------------------

project = 'DSMR-reader'
copyright = '2015 - {} DSMR-reader'.format(datetime.datetime.now().year)
author = 'Dennis Siemensma'

# The full version, including alpha/beta/rc tags
release = 'v4'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
sys.path.append(os.path.abspath('exts'))
extensions = [
    'sphinx_reredirects',
]

redirects = {  # sphinx_reredirects
    # Legacy redirects.
    'settings': '/reference/env-settings.html',
    'troubleshooting': '/how-to/index.html',
    'contributing': 'index.html',
    'donations': 'index.html',
    'faq/uninstall': '/how-to/index.html',
    'faq/database': '/how-to/index.html',
    'faq/restart_processes': '/how-to/index.html',
    'faq/update': '/how-to/index.html',
    'data_integrity': '/how-to/index.html',
    'requirements': '/explanation/about.html',
    'tour': '/explanation/about.html',
    'screenshots': '/explanation/about.html',
    'installation/restore': '/how-to/index.html',
    'installation/datalogger': '/how-to/installation/remote-datalogger.html',
    'installation/quick': '/how-to/installation/quick.html',
    'installation/explained': '/tutorials/installation/step-by-step.html',
    'installation/docker': '/how-to/third-party/docker-installation.html',

    # Reworked structure redirects.
    'intro': '/explanation/about.html',
    'credits': '/explanation/hall-of-fame.html',

    'configuration': '/tutorial/configuration.html',
    'application': '/tutorial/setting-up.html',

    'installation': '/how-to/installation/quick.html',
    'faq/v3_upgrade': '/tutorials/upgrading/to-v3.html',
    'faq/v4_upgrade': '/tutorials/upgrading/to-v4.html',
    'development': '/how-to/development.html',
    'home_assistant': '/how-to/third-party/home-assistant.html',
    'admin/email': '/how-to/admin/email.html',
    'admin/backup_dropbox': '/how-to/admin/backup_dropbox.html',
    'admin/email_backup': '/how-to/admin/email_backup.html',
    'admin/mindergas': '/how-to/admin/mindergas.html',
    'admin/mqtt': '/how-to/admin/mqtt.html',
    'admin/notifications': '/how-to/admin/notifications.html',
    'admin/pvoutput': '/how-to/admin/pvoutput.html',
    'mqtt': '/how-to/index.html',

    'changelog': '/reference/changelog.html',
    'env_settings': '/reference/env-settings.html',
    'plugins': '/reference/plugins.html',
    'api': '/reference/api.html',
    'faq': '/how-to/index.html',
}

master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'plugins', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_sidebars = {'**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'], }

locale_dirs = ['_locale/']
gettext_compact = False
