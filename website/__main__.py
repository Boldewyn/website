#!/usr/bin/python
""""""


import glob
import logging
import os
import sys
import shutil
import traceback
from ._webtools.settings import settings
from ._webtools.articles import get_articles
from ._webtools.categories import render, render_feed
from ._webtools.templates import template_engine
from ._webtools.util import copy_statics, get_templates
from ._webtools.plugins import load_plugins, fire_hook


def main():
    """"""
    return build()

def build():
    """"""
    fire_hook("build.start")
    load_plugins()
    settings.ORIG_BUILD_TARGET = settings.BUILD_TARGET.rstrip("/")
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    if settings.DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    copy_statics()
    all_articles = get_articles()
    articles = [a for a in all_articles \
                if "noref" not in a.headers.status]
    articles.sort()
    template_engine.set_articles(articles)
    for article in all_articles:
        article.save(articles=articles)
    render(articles)
    for template in get_templates():
        template_engine.render_template(template,
                template.replace(".mako", ".html"), a=articles, articles=articles)
    if not glob.glob(settings.BUILD_TARGET+"/index.html*") and \
       not glob.glob(settings.BUILD_TARGET+"/index.xhtml*"):
        template_engine.render_paginated("index", "index.html",
                                         a=articles, articles=articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/feed.xml"):
        render_feed(articles)
    template_engine.render_sitemap()
    template_engine.make_index()
    fire_hook("build.end")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logging.critical(traceback.format_exc())
        sys.exit(1)

