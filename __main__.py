#!/usr/bin/python
""""""


import os
import sys
import shutil
from _webtools.settings import settings
import _webtools.articles
import _webtools.categories
import _webtools.templates
from _webtools.templates import template_engine


def init():
    """"""
    shutil.rmtree(settings.BUILD_TARGET, True)
    shutil.copytree(".", settings.BUILD_TARGET,
            ignore=shutil.ignore_patterns("_*", ".*swp", ".git*"))


def main():
    """"""
    os.chdir(os.path.dirname(__file__))
    init()
    all_articles = _webtools.articles.get_articles()
    articles = [a for a in all_articles \
               if "noref" not in a.headers.get("requires", "").lower()]
    articles.sort()
    template_engine.set("articles", articles)
    for article in all_articles:
        article.save()
    _webtools.categories.render(articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/index.html") and \
       os.path.isfile("_templates/index.mako"):
        template_engine.render_paginated("index", "index.html",
                                         a=articles, articles=articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/feed.xml"):
        _webtools.categories.render_feed(articles)
    template_engine.render_sitemap()
    return 0


if __name__ == "__main__":
    if settings.BUILD_TARGET is None:
        settings.BUILD_TARGET = "site"
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    sys.exit(main())

