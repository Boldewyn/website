#!/usr/bin/python
""""""


import glob
import os
import sys
import shutil
from _webtools.settings import settings
import _webtools.articles
import _webtools.categories
from _webtools.templates import template_engine


def init():
    """"""
    shutil.rmtree(settings.BUILD_TARGET, True)
    shutil.copytree(".", settings.BUILD_TARGET,
            ignore=shutil.ignore_patterns("_*", ".*swp", ".git*", "*.mako"))


def get_templates(dir=""):
    """Recursively fetch templates that need processing"""
    dir = dir.strip("/")
    if dir != "":
        dir += "/"
    templates = []
    for a in os.listdir("./"+dir):
        if os.path.isdir("./"+dir + a):
            if a[0] not in ["_", "."] and \
               not (dir + a).startswith(settings.ORIG_BUILD_TARGET+"/"):
                templates.extend(get_templates(dir + a))
        elif a.endswith(".mako"):
            templates.append(dir + a)
    return templates


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
    return 0


if __name__ == "__main__":
    if settings.BUILD_TARGET is None:
        settings.BUILD_TARGET = "site"
    settings.ORIG_BUILD_TARGET = settings.BUILD_TARGET.rstrip("/")
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    sys.exit(main())

