#!/usr/bin/python
""""""


import os
import sys
import shutil
from _settings import settings
import _articles
from mako.template import Template


_dir = os.path.dirname(__file__)


def init(target):
    """"""
    path = os.path.abspath(target)
    shutil.rmtree(path, True)
    shutil.copytree(_dir, path,
            ignore=shutil.ignore_patterns("_*", ".*swp", ".git*"))


def render_template(template, path, **ctx):
    """"""
    template = Template(filename=_dir+"/_templates/"+template+
                                      '.mako')
    to = open(path, 'w')
    to.write(template.render(**ctx))
    to.close()


def main(target):
    """"""
    init(target)
    articles = _articles.get_articles()
    categories = {}
    for article in articles:
        article.save(target)
        p = os.path.dirname(article.path)
        if p not in categories:
            categories[p] = []
        categories[p].append(article)
    for category, a in categories.iteritems():
        if category+"/index.html" not in a:
            render_template("category", os.path.abspath(target)+"/"+
                            category+"/index.html", **locals())
    return 0


if __name__ == "__main__":
    target = "site"
    sys.exit(main(target))

