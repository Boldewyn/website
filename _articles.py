""""""


import re
import os
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from BeautifulSoup import BeautifulSoup
from _settings import settings
from datetime import datetime
import _templates


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
        self.headers = {}
        self.path = path
        head, content = open(_dir + "/_articles/" + path, 'r').read().split("\n\n", 1)
        self.set_headers(get_headers(head))
        self.raw_content = unicode(content.decode("utf-8")).replace("\r\n", "\n")
        self.process_content()
        self.category = os.path.dirname(path).strip("/")

    def set_headers(self, headers):
        """"""
        for k, v in headers.iteritems():
            self.set_header(k, v)
        if "ID" not in self.headers:
            self.headers["ID"] = "article-"+re.sub(re.compile(r'\W+', re.U), '-', self.path)
        if "DATE" not in self.headers:
            self.headers["DATE"] = datetime.now()
        if "AUTHOR" not in self.headers:
            self.headers["AUTHOR"] = settings.DEFAULT_AUTHOR or ""

    def set_header(self, name, value):
        """"""
        if name == "DATE" and isinstance(value, basestring):
            value = datetime.strptime(value, settings.DATE_FORMAT)
        elif name == "SUBJECT":
            value = [ x.strip() for x in value.split(",") ]
        self.headers[name] = value

    def process_content(self, content = None):
        """"""
        content = content or self.raw_content
        soup = BeautifulSoup(content)
        pres = soup.findAll("pre", {"class": re.compile(r"\blang:\S+\b")})
        formatter = HtmlFormatter(encoding='UTF-8', classprefix='s_')
        for pre in pres:
            lang = re.sub(r"^.*\blang:(\S+).*$", r"\1", pre["class"])
            try:
                lexer = get_lexer_by_name(lang)
            except pygments.util.ClassNotFound:
                lexer = guess_lexer(pre.renderContents())
            result = pygments.highlight(pre.renderContents(), lexer, formatter)
            pre.contents = BeautifulSoup(result).pre.contents
            pre['class'] += " highlight"
        self.content = unicode(soup)
        if "ABSTRACT" not in self.headers:
            if "DESCRIPTION" in self.headers:
                self.headers["ABSTRACT"] = self.headers['DESCRIPTION']
            else:
                self.headers["ABSTRACT"] = self.content[:40]+"..."

    def save(self, target, **additions):
        """"""
        target = os.path.abspath(target)
        if settings.ARTICLE_PATH:
            target += "/" + settings.ARTICLE_PATH
        _templates.render_template("article", target+"/"+self.path,
                content=self.content, article=self, **additions)

    def __unicode__(self):
        return self.content

