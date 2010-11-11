#!/usr/bin/python
""""""


import os
import sys
import shutil
from _settings import settings
import _articles
import _categories
import _templates
from _templates import template_engine


def init():
    """"""
    shutil.rmtree(settings.BUILD_TARGET, True)
    shutil.copytree(".", settings.BUILD_TARGET,
            ignore=shutil.ignore_patterns("_*", ".*swp", ".git*"))


def main():
    """"""
    os.chdir(os.path.dirname(__file__))
    init()
    articles = _articles.get_articles()
    template_engine.set("articles", articles)
    for article in articles:
        article.save()
    _categories.render(articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/index.html") and \
       os.path.isfile("_templates/index.mako"):
        template_engine.render_paginated("index", "index.html",
                a=list(articles), articles=articles)
    template_engine.render_sitemap()
    return 0


if __name__ == "__main__":
    if settings.BUILD_TARGET is None:
        settings.BUILD_TARGET = "site"
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    sys.exit(main())

