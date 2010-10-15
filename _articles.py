""""""


import re
import os
import pygments
import mako
from BeautifulSoup import BeautifulSoup
from _settings import settings
from datetime import datetime


_dir = os.path.dirname(__file__)


def get_articles(dir=""):
    """Recursively fetch articles"""
    dir = dir.strip("/") + "/"
    articles = []
    for a in os.listdir(_dir + "/_articles/" + dir):
        if os.path.isdir(_dir + "/_articles/" + dir + a):
            r = get_articles(dir + a)
            if r:
                articles.extend(r)
        else:
            articles.append(Article(dir + a))
    return frozenset(articles)


def get_headers(string):
    """Convert the HTTP-style headers of articles to dict"""
    headers = {}
    string = re.sub(r'[ \t]*\n[ \t]+', ' ', string)
    for line in string.splitlines():
        k,v = line.split(":", 1)
        k = k.upper()
        v = v.strip()
        if k in headers:
            headers[k] += ", " + v
        else:
            headers[k] = v
    return headers


class Article(object):
    """"""

    def __init__(self, path):
        """"""
        self.headers = {
            "DATE": datetime.now(),
        }
        self.path = path
        headers, content = open(_dir + "/_articles/" + path, 'r').read().split("\n\n", 1)
        self.set_headers(get_headers(headers))
        self.raw_content = unicode(content.decode("utf-8"))
        self.process_content()
        self.category = os.path.dirname(path).strip("/")

    def set_headers(self, headers):
        """"""
        for k, v in headers.iteritems():
            self.set_header(k, v)

    def set_header(self, name, value):
        """"""
        if name == "DATE":
            value = datetime.strptime(value, settings.DATE_FORMAT)
        elif name == "SUBJECT":
            value = [ x.strip() for x in value.split(",") ]
        self.headers[name] = value

    def process_content(self, content = None):
        """"""
        content = content or self.raw_content
        self.content = content
        if "ABSTRACT" not in self.headers:
            if "DESCRIPTION" in self.headers:
                self.headers["ABSTRACT"] = self.headers['DESCRIPTION']
            else:
                self.headers["ABSTRACT"] = self.content[:40]+"..."

    def save(self, target):
        """"""
        target = os.path.abspath(target)
        if settings.ARTICLE_PATH:
            target += "/" + settings.ARTICLE_PATH
        if not os.path.isdir(target + "/" + os.path.dirname(self.path)):
            os.makedirs(target + "/" + os.path.dirname(self.path))
        f = open(target + "/" + self.path, 'w')
        f.write(self.content)
        return f.close()

    def __unicode__(self):
        return self.content

