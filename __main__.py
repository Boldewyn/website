#!/usr/bin/python
""""""


import glob
import os
import sys
import shutil
import traceback
from _webtools.settings import settings
import _webtools.articles
import _webtools.categories
from _webtools.templates import template_engine
from _webtools.util import copy_statics, get_templates


def main():
    """"""
    copy_statics()
    all_articles = _webtools.articles.get_articles()
    articles = [a for a in all_articles \
                if "noref" not in a.headers.status]
    articles.sort()
    template_engine.set("articles", articles)
    for article in all_articles:
        article.save(articles=articles)
    _webtools.categories.render(articles)
    for template in get_templates():
        template_engine.render_template(template,
                template.replace(".mako", ".html"), a=articles, articles=articles,
                full_path=True)
    if not glob.glob(settings.BUILD_TARGET+"/index.html*") and \
       not glob.glob(settings.BUILD_TARGET+"/index.xhtml*"):
        template_engine.render_paginated("index", "index.html",
                                         a=articles, articles=articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/feed.xml"):
        _webtools.categories.render_feed(articles)
    template_engine.render_sitemap()
    template_engine.make_index()
    return 0


if __name__ == "__main__":
    settings.ORIG_BUILD_TARGET = settings.BUILD_TARGET.rstrip("/")
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

