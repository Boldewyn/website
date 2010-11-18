""""""


import hashlib
import re
import os
import pygments
import shutil
from htmlentitydefs import name2codepoint
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from BeautifulSoup import BeautifulSoup
from .settings import settings
from datetime import datetime
from .templates import template_engine


# define a determined "now"
_now = datetime.now()


def get_articles(dir=""):
    """Recursively fetch articles"""
    dir = dir.strip("/") + "/"
    articles = []
    for a in os.listdir("_articles/" + dir):
        if os.path.isdir("_articles/" + dir + a):
            r = get_articles(dir + a)
            if r:
                articles.extend(r)
        elif not a.endswith("html"):
            if not os.path.isdir(settings.BUILD_TARGET + "/" + dir):
                os.makedirs(settings.BUILD_TARGET + "/" + dir)
            shutil.copy("_articles/" + dir + a,
                    settings.BUILD_TARGET + "/" + dir + a)
        else:
            candidate = Article(dir + a)
            if candidate.is_live():
                articles.append(candidate)
    if dir == "/":
        articles.sort()
        return tuple(articles)
    return articles


def generate_description(markup, length=200, append=u"\u2026"):
    """If the description is missing, generate it"""
    plain = re.sub(r"<[^>]+>", "", markup)
    plain = re.sub(r"\s+", " ", plain).strip()
    if len(plain) < length:
        return plain
    if "&" in plain:
        plain = plain.replace("&apos;", "'")
        def repl_quot(m):
            p = m.group(1)
            if p.lower().startswith("#x"):
                return unichr(int("0x"+p[2:]))
            elif p.startswith("#"):
                return unichr(int(p[1:]))
            elif p in name2codepoint:
                return unichr(name2codepoint[p])
            else:
                return "X"
        plain = re.sub(r'&\([^;]+\);', repl_quot, plain)
    if len(plain) < length:
        return plain
    plainadd = ""
    if " " in plain[length:length+50]:
        plainadd = plain[length:length+50].split(" ")[0]
    return plain[:length]+plainadd+append


def get_headers(string):
    """Convert the HTTP-style headers of articles to dict"""
    headers = {}
    string = re.sub(re.compile(r'^#.*', re.M), r'', string)
    string = re.sub(r'[ \t]*\n[ \t]+', ' ', string)
    for line in string.splitlines():
        if not line:
            continue
        k,v = line.split(":", 1)
        k = k.upper()
        v = v.strip()
        if k in headers:
            headers[k] += ", " + v
        else:
            headers[k] = v
    return headers


class ArticleHeaders(object):
    """Store article headers in a highly accessible key:value db"""

    DC_TERMS = ("ABSTRACT", "ACCESSRIGHTS", "ACCRUALMETHOD",
                "ACCRUALPERIODICITY", "ACCRUALPOLICY", "ALTERNATIVE", "AUDIENCE",
                "AVAILABLE", "BIBLIOGRAPHICCITATION", "CONFORMSTO", "CONTRIBUTOR",
                "COVERAGE", "CREATED", "CREATOR", "DATE", "DATEACCEPTED",
                "DATECOPYRIGHTED", "DATESUBMITTED", "DESCRIPTION", "EDUCATIONLEVEL",
                "EXTENT", "FORMAT", "HASFORMAT", "HASPART", "HASVERSION",
                "IDENTIFIER", "INSTRUCTIONALMETHOD", "ISFORMATOF", "ISPARTOF",
                "ISREFERENCEDBY", "ISREPLACEDBY", "ISREQUIREDBY", "ISSUED",
                "ISVERSIONOF", "LANGUAGE", "LICENSE", "MEDIATOR", "MEDIUM",
                "MODIFIED", "PROVENANCE", "PUBLISHER", "REFERENCES", "RELATION",
                "REPLACES", "REQUIRES", "RIGHTS", "RIGHTSHOLDER", "SOURCE", "SPATIAL",
                "SUBJECT", "TABLEOFCONTENTS", "TEMPORAL", "TITLE", "TYPE", "VALID")
    DC_ALIAS = {
        "ID": "IDENTIFIER",
        "AUTHOR": "CREATOR",
    }
    BOOLS = ("STANDALONE", "EXCLUDE")
    DATES = ("DATE", "MODIFIED", "AVAILABLE", "CREATED", "DATEACCEPTED", "DATECOPYRIGHTED",
             "DATESUBMITTED", "ISSUED", "MODIFIED")
    LISTS = ("SUBJECT", "STYLESHEET", "SCRIPT")

    def __init__(self, data=None):
        """Initialize header storage"""
        self.h = {}
        if isinstance(data, dict):
            self.set_headers(data)
        elif isinstance(data, basestring):
            self.set_headers(get_headers(data))

    def set_headers(self, headers):
        """Set a bulk of headers (string or dict)"""
        for k, v in headers.iteritems():
            self.set_header(k, v)

    def set_header(self, name, value):
        """Set a single header"""
        name = name.upper()
        if name in self.DATES and isinstance(value, basestring):
            value = datetime.strptime(value, settings.DATE_FORMAT)
        elif name in self.LISTS and not isinstance(value, list):
            value = [ x.strip() for x in value.split(",") ]
        elif name in self.BOOLS and not isinstance(value, bool):
            if re.search("^(False|0+|No)$", value, re.I):
                value = False
            else:
                value = bool(value)
        self.h[name] = value

    def set_defaults(self, d):
        """Set default values en gros"""
        for k, v in d.iteritems():
            if k not in self:
                self.set_header(k, v)
        for k, v in settings.DEFAULTS:
            if k not in self:
                self.set_header(k, v)
        for k in self.BOOLS:
            if k not in self:
                self.set_header(k, False)
        for k in self.LISTS:
            if k not in self:
                self.set_header(k, [])

    def get_dc(self):
        """Get the Dublin Core headers together"""
        dc = {}
        for k,v in self.h.iteritems():
            if k in self.DC_TERMS:
                dc[k.lower()] = self.value_to_string(v)
            elif k in self.DC_ALIAS:
                dc[self.DC_ALIAS[k].lower()] = self.value_to_string(v)
        return dc

    def value_to_string(self, value):
        """"""
        if isinstance(value, datetime):
            return value.isoformat("T")
        elif isinstance(value, list):
            return u", ".join(value)
        else:
            return unicode(value).replace("\n", " ").strip()

    def __getattr__(self, name, default=None):
        """Get a header, via dict method, too"""
        if name.upper() in self.h:
            return self.h[name.upper()]
        else:
            return default

    __getitem__ = __getattr__
    get = __getattr__

    def __setattr__(self, name, value):
        """Set a header, via dict method, too"""
        if name == "h":
            object.__setattr__(self, name, value)
        else:
            self.set_header(name.upper(), value)

    __setitem__ = __setattr__

    def __delattr__(self, name):
       """Delete a header, via dict method, too"""
       if name.upper() in self.h:
           del self.h[name.upper()]

    __delitem__ = __delattr__

    # Missing dict methods
    __len__ = lambda self: len(self.h)
    __contains__ = lambda self, v: self.h.__contains__(v.upper())
    __iter__ = lambda self: self.h.__iter__()
    iterkeys = __iter__


class Article(object):
    """A single article or blog post"""

    def __init__(self, path):
        """Initialize with path to article source"""
        self.headers = ArticleHeaders()
        self.path = "/"+path.lstrip("/")
        self.rdf_path = self.path+".rdf"
        if self.rdf_path.endswith("html.rdf"):
            self.rdf_path = ".".join(self.path.split(".")[:-1]) + ".rdf"
        head, content = open("_articles/" + path, 'r').read().split("\n\n", 1)
        self.headers.set_headers(get_headers(head))
        self.raw_content = unicode(content.decode("utf-8")).replace("\r\n", "\n")
        self.process_content()
        self.complete_headers()
        self.category = os.path.dirname(path).strip("/")

    def is_live(self):
        """Check meta info, to see if this article is live"""
        if self.headers.available and self.headers.available < _now:
            return False
        if self.headers.issued and self.headers.issued > _now:
            return False
        if self.headers.valid and self.headers.valid < _now:
            return False
        if self.headers.exclude == True:
            return False
        if "draft" in self.headers.get("status", "").lower() and not settings.DEBUG:
            return False
        return True

    def complete_headers(self):
        """Set default headers, that are missing"""
        defaults = {
            "ID": settings.URL+self.path.lstrip("/"),
            "date": _now,
            "type": "Text",
            "format": "application/xhtml+xml",
            "title": "No Title",
        }
        if self.headers.standalone:
            self.headers.title = BeautifulSoup(self.content).html.head.title.string
        if "description" not in self.headers:
            if "abstract" in self.headers:
                self.headers.description = self.headers.abstract
            elif self.headers.standalone:
                self.headers.description = generate_description(unicode(BeautifulSoup(self.content).body))
            else:
                self.headers.description = generate_description(self.content)
        self.headers.set_defaults(defaults)

    def process_content(self):
        """Change the raw content to a renderable state"""
        content = self.raw_content
        if self.headers.standalone:
            self.content = unicode(self.raw_content)
            return True
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        pres = soup.findAll("pre", {"data-lang": re.compile(r".*")})
        for pre in pres:
            formatter = HtmlFormatter(encoding='UTF-8', classprefix='s_', hl_lines=pre.get("data-hl", "").split(","))
            lang = pre["data-lang"]
            try:
                lexer = get_lexer_by_name(lang)
            except pygments.util.ClassNotFound:
                lexer = guess_lexer(pre.renderContents())
            result = pygments.highlight(pre.renderContents(), lexer, formatter)
            pre.contents = BeautifulSoup(result).pre.contents
            if "class" not in pre:
                pre["class"] = ""
            pre['class'] += " highlight"
        self.content = unicode(soup)

    def save(self, **additions):
        """"""
        if settings.DEBUG:
            print self.path
        if "language" in self.headers:
            additions["lang"] = self.headers.language
        if "modified" in self.headers:
            additions["sitemap_lastmod"] = self.headers.modified
        else:
            additions["sitemap_lastmod"] = self.headers.date
        if "accrualperiodicity" in self.headers:
            additions["sitemap_changefreq"] = self.headers.accrualperiodicity
        target = settings.get("ARTICLE_PATH", "")
        if self.headers.standalone:
            template_engine.write_to(target+"/"+self.path, self.content)
        else:
            template_engine.render_template("article", target+"/"+self.path,
                    content=self.content, article=self, **additions)
        additions["nolang"] = True
        template_engine.render_template("article.rdf", target+"/"+self.rdf_path,
                content=self.content, article=self, **additions)

    def __unicode__(self):
        return self.content

    def __hash__(self):
        s = hashlib.sha224(self.headers.date.strftime("%Y-%m-%dT%H:%m:%s") +
                           "_" + self.headers.ID).hexdigest()
        return int(s, 16)

    def __cmp__(self, other):
        s = self.headers.date.strftime("%Y-%m-%dT%H:%m:%s") + "_" + self.headers.ID
        o = other.headers.date.strftime("%Y-%m-%dT%H:%m:%s") + "_" + other.headers.ID
        return cmp(s, o)

