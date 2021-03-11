"""
COPYRIGHT (c) 2020 "Matt from Documatt"
(https://gitlab.com/documatt/sphinx-reredirects)
"""

import os
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging
from fnmatch import fnmatch
from string import Template

OPTION_REDIRECTS = "redirects"
OPTION_REDIRECTS_DEFAULT = {}

OPTION_TEMPLATE_FILE = "redirect_html_template_file"
OPTION_TEMPLATE_FILE_DEFAULT = None

REDIRECT_FILE_DEFAULT_TEMPLATE = '<html><head><meta http-equiv="refresh" content="0; url=${to_uri}"></head></html>'

logger = logging.getLogger(__name__)


def setup(app: Sphinx):
    """
    Extension setup, called by Sphinx
    """
    app.connect("build-finished", init)
    app.add_config_value(OPTION_REDIRECTS, OPTION_REDIRECTS_DEFAULT, "env")
    app.add_config_value(OPTION_TEMPLATE_FILE, OPTION_TEMPLATE_FILE_DEFAULT, "env")


def init(app: Sphinx, exception):
    redirects: dict = app.config[OPTION_REDIRECTS]
    template_file: str = app.config[OPTION_TEMPLATE_FILE]

    if not redirects:
        logger.info('No redirects found')
        return

    # HTML used as redirect file content
    redirect_template = REDIRECT_FILE_DEFAULT_TEMPLATE
    if template_file:
        redirect_file_path = Path(app.srcdir, template_file)
        redirect_template = redirect_file_path.read_text()

    # For each entry
    for source, target in redirects.items():
###        logger.info(f"Processing reredirect '{source}' to '{target}'")
        # # examine if it matches to some doc
        # for doc in app.env.found_docs:
        #     logger.info(f"Comparing '{source}' with '{doc}'")
        #     if fnmatch(doc, source):
        # if so, apply $source placeholder

        new_target = apply_placeholders(source, target)
        # create redirect file
        redirect_file_path = Path(app.outdir).joinpath(source).with_suffix(".html")
        create_redirect_file(redirect_template, redirect_file_path, new_target)


def apply_placeholders(source: str, target: str) -> str:
    return Template(target).substitute({"source": source})


def create_redirect_file(content_template: str, at_path: Path, to_uri: str) -> None:
    target_dir = os.path.dirname(at_path.resolve())

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    content = Template(content_template).substitute({"to_uri": to_uri})

    at_path.touch()
    at_path.write_text(content)

    logger.info(f"Created redirect file '{at_path}' to '{to_uri}'")
