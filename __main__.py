#!/usr/bin/python
""""""


import os
import sys
import shutil
from _settings import settings
import _articles
import _categories
import _templates


_dir = os.path.dirname(__file__)


def init(target):
    """"""
    path = os.path.abspath(target)
    shutil.rmtree(path, True)
    shutil.copytree(_dir, path,
            ignore=shutil.ignore_patterns("_*", ".*swp", ".git*"))


def main(target):
    """"""
    init(target)
    articles = _articles.get_articles()
    for article in articles:
        article.save(target, articles=articles)
    _categories.render_tags(target, articles)
    _categories.render_archives(target, articles)
    _categories.render_indexes(target, articles)
    if not os.path.isfile(target+"/index.html") and \
       os.path.isfile("_templates/index.mako"):
        _templates.render_template("index", os.path.abspath(target)+"/index.html", articles=articles)
    return 0


if __name__ == "__main__":
    target = settings.BUILD_TARGET
    if target is None:
        target = "site"
    sys.exit(main(target))

