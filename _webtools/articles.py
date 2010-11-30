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
try:
    from dateutil.parser import parse as date_parse
except ImportError:
    def date_parse(str):
        return datetime.strptime(str, settings.DATE_FORMAT)


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
        elif not any([a.endswith("."+x) for x in ("html","xhtml","php")]):
            if not os.path.isdir(settings.BUILD_TARGET + "/" + dir):
                os.makedirs(settings.BUILD_TARGET + "/" + dir)
            shutil.copy("_articles/" + dir + a,
                        settings.BUILD_TARGET + "/" + dir + a)
        else:
            try:
                candidate = Article(dir + a)
            except ValueError:
                print "*Error* Couldn't process _articles/" + dir + a
            else:
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


class ArticleHeaders(object):
    """Store article headers in a highly accessible key:value db"""

    DC_TERMS = ("abstract", "accessRights", "accrualMethod",
                "accrualPeriodicity", "accrualPolicy", "alternative", "audience",
                "available", "bibliographicCitation", "conformsTo", "contributor",
                "coverage", "created", "creator", "date", "dateAccepted",
                "dateCopyrighted", "dateSubmitted", "description", "educationLevel",
                "extent", "format", "hasFormat", "hasPart", "hasVersion",
                "identifier", "instructionalMethod", "isFormatOf", "isPartOf",
                "isReferencedBy", "isReplacedBy", "isRequiredBy", "issued",
                "isVersionOf", "language", "license", "mediator", "medium",
                "modified", "provenance", "publisher", "references", "relation",
                "replaces", "requires", "rights", "rightsHolder", "source", "spatial",
                "subject", "tableOfContents", "temporal", "title", "type", "valid")
    DC_ALIAS = {
        "ID": "identifier",
        "AUTHOR": "creator",
    }
    BOOLS = ()
    DATES = ("DATE", "MODIFIED", "AVAILABLE", "CREATED", "DATEACCEPTED", "DATECOPYRIGHTED",
             "DATESUBMITTED", "ISSUED", "MODIFIED")
    LISTS = ("SUBJECT", "STYLESHEET", "SCRIPT", "STATUS")

    def __init__(self, data=None):
        """Initialize header storage"""
        self._h = {}
        if isinstance(data, dict):
            self.set_headers(data)
        elif isinstance(data, basestring):
            self.parse_headers(data)

    def parse_headers(self, string):
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
        self.set_headers(headers)
        return headers

    def set_headers(self, headers):
        """Set a bulk of headers (string or dict)"""
        for k, v in headers.iteritems():
            self.set(k, v)

    def set_defaults(self, d):
        """Set default values en gros"""
        for k, v in d.iteritems():
            if k not in self:
                self.set(k, v)
        for k, v in settings.DEFAULTS:
            if k not in self:
                self.set(k, v)
        for k in self.BOOLS:
            if k not in self:
                self.set(k, False)
        for k in self.LISTS:
            if k not in self:
                self.set(k, [])

    def get_dc(self):
        """Get the Dublin Core headers together

        The result is a dictionary of strings, ready to be printed.
        """
        dc = {}
        for term in self.DC_TERMS:
            if term in self:
                dc[term] = self.value_to_string(self[term])
        for alias, term in self.DC_ALIAS.iteritems():
            if alias in self and term not in dc:
                dc[term] = self.value_to_string(self[alias])
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
        if name.upper() in self._h:
            return self._h[name.upper()]
        else:
            return default

    __getitem__ = __getattr__
    get = __getattr__

    def __setattr__(self, name, value):
        """Set a header, via dict method, too"""
        if name == "_h":
            object.__setattr__(self, name, value)
        else:
            name = name.upper()
            if name in self.DATES and isinstance(value, basestring):
                value = date_parse(value)
            elif name in self.LISTS and not isinstance(value, list):
                value = [ x.strip() for x in value.split(",") ]
            elif name in self.BOOLS and not isinstance(value, bool):
                if re.search("^(False|0+|No)$", value, re.I):
                    value = False
                else:
                    value = bool(value)
            if name == "STATUS":
                value = [x.lower() for x in value]
            self._h[name] = value

    __setitem__ = __setattr__
    set = __setattr__

    def __delattr__(self, name):
       """Delete a header, via dict method, too"""
       if name.upper() in self._h:
           del self._h[name.upper()]

    __delitem__ = __delattr__

    # Missing dict methods
    __len__ = lambda self: len(self._h)
    __contains__ = lambda self, v: self._h.__contains__(v.upper())
    __iter__ = lambda self: self._h.__iter__()
    iterkeys = __iter__


class Article(object):
    """A single article or blog post"""

    def __init__(self, path):
        """Initialize with path to article source"""
        self.path = "/"+path.lstrip("/")
        self.category = os.path.dirname(path).strip("/")
        self.content = ""

        f = open("_articles" + self.path, 'r')
        head, content = f.read().replace("\r\n", "\n").split("\n\n", 1)
        f.close()
        self.headers = ArticleHeaders(head)
        self.raw_content = unicode(content.decode("utf-8"))

        self.complete_headers()
        self.process_content()

    def is_live(self):
        """Check meta info, to see if this article is live"""
        if self.headers.available and self.headers.available < _now:
            return False
        if self.headers.issued and self.headers.issued > _now:
            return False
        if self.headers.valid and self.headers.valid < _now:
            return False
        if "exclude" in self.headers.status:
            return False
        if "draft" in self.headers.get("status", []) and not settings.DEBUG:
            return False
        return True

    def complete_headers(self):
        """Set default headers, that are missing"""
        defaults = {
            "ID": settings.URL+self.path.lstrip("/"),
            "date": _now,
            "type": "Text",
            "format": "application/xhtml+xml",
            "status": [],
        }
        self.headers.set_defaults(defaults)
        if "title" not in self.headers:
            if "standalone" in self.headers.status:
                self.process_content()
                self.headers.title = BeautifulSoup(self.content).html.head.title.string
            else:
                self.headers.title = ""
        if "description" not in self.headers:
            self.process_content()
            if "abstract" in self.headers:
                self.headers.description = self.headers.abstract
            elif "standalone" in self.headers.status:
                self.headers.description = generate_description(unicode(BeautifulSoup(self.content).body))
            else:
                self.headers.description = generate_description(self.content)

    def process_content(self):
        """Change the raw content to a renderable state"""
        if len(self.content):
            return True
        elif "standalone" in self.headers.status:
            self.content = unicode(self.raw_content)
            return True
        soup = BeautifulSoup(self.raw_content, convertEntities=BeautifulSoup.HTML_ENTITIES)
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
            if "draft" in self.headers.status:
                print "*DRAFT* ",
            print self.path
        elif "draft" in self.headers.status:
            raise ValueError("Can't save drafts")
        target = settings.get("ARTICLE_PATH", "")
        if "standalone" in self.headers.status:
            template_engine.write_to(target+"/"+self.path, self.content)
        else:
            if "language" in self.headers:
                additions["lang"] = self.headers.language
            if "modified" in self.headers:
                additions["sitemap_lastmod"] = self.headers.modified
            else:
                additions["sitemap_lastmod"] = self.headers.date
            if "accrualperiodicity" in self.headers:
                additions["sitemap_changefreq"] = self.headers.accrualperiodicity
            template_engine.render_template(self.headers.get("template", "article"),
                                            target+"/"+self.path, content=self.content,
                                            article=self, **additions)

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

