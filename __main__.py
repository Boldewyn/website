#!/usr/bin/python
""""""


import os
import sys
import shutil
from _settings import settings
import _articles


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
        article.save(target)
    return 0


if __name__ == "__main__":
    target = "site"
    sys.exit(main(target))

