""""""


import hashlib
import logging
import re
import os
import pygments
import shutil
import traceback
from htmlentitydefs import name2codepoint
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexer import Lexer
from BeautifulSoup import BeautifulSoup
from .settings import settings
from datetime import datetime
from .templates import template_engine
from .templatedefs import aa
from .util import get_extensions
from .url import Url
try:
    from dateutil.parser import parse as date_parse
except ImportError:
    def date_parse(str):
        return datetime.strptime(re.sub(r'[+-]\d{2}:?\d{2}$', '', str), settings.DATE_FORMAT)


BeautifulSoup.PRESERVE_WHITESPACE_TAGS |= set(["code"])


def _unescape(text):
    """Removes HTML or XML character references and entities from a text string.

    @author Fredrik Lundh - http://effbot.org/zone/re-sub.htm
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub(r"&#?\w+;", fixup, unicode(text.decode("UTF-8")), re.U)


def get_articles(dir=""):
    """Recursively fetch articles from the _articles directory

    If non-articles are found, they are copied to the BUILD_TARGET."""
    dir = dir.strip("/") + "/"
    articles = []
    for a in os.listdir("_articles/" + dir):
        if os.path.isdir("_articles/" + dir + a):
            r = get_articles(dir + a)
            if r:
                articles.extend(r)
        elif not set(get_extensions(a)[1]) & set(["html","xhtml","htm","xht"]):
            if not os.path.isdir(settings.BUILD_TARGET + "/" + dir):
                os.makedirs(settings.BUILD_TARGET + "/" + dir)
            shutil.copy("_articles/" + dir + a,
                        settings.BUILD_TARGET + "/" + dir + a)
        else:
            try:
                candidate = Article(dir + a)
            except ValueError, e:
                logging.warning("Couldn't process _articles/" + dir + a + ": " + str(e))
                if settings.DEBUG:
                    logging.warning(traceback.format_exc())
            else:
                if candidate.is_live():
                    articles.append(candidate)
    if dir == "/":
        articles.sort()
        return tuple(articles)
    return articles


def generate_description(markup, length=200, append=u"\u2026"):
    """If the description is missing, generate it from the article markup"""
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
    """Store article headers in a highly accessible key:value db

    With highly accessible we mean, that the items can be accessed in this way:
    * case insensitive with regard to the key
    * via dict methods (e.g., get())
    * via class methods (e.g., foo.bar)
    The rationale is, that the original keys are case-insensitive, too (modeled
    after HTTP headers), and template authors will use an instance of this."""

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
            v = unicode(v.strip().decode("UTF-8"))
            if k in headers:
                headers[k] += u", " + v
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
        for k, v in settings.DEFAULTS.iteritems():
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
        """Change a header value to a printable string"""
        if isinstance(value, Article):
            return str(value.url)
        elif isinstance(value, datetime):
            return value.isoformat("T")
        elif isinstance(value, list):
            return u", ".join(value)
        else:
            return unicode(value).replace(u"\n", u" ").strip()

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

    # Lexer aliases
    lexers = {
        'php-inline' : ['php', {"startinline": True}],
    }

    def __init__(self, path):
        """Initialize with path to article source"""
        path = path.lstrip("/")
        self.lexers.update(settings.get('LEXERS', {}))
        self.processed = False
        self.category = os.path.dirname(path).strip("/")
        self.url = Url(settings.get("ARTICLE_PATH", "") + path)
        l = filter(lambda s: s in settings.languages, self.url.get_extensions())
        self.hard_language = None
        if len(l) == 1:
            self.hard_language = l[0]

        f = open("_articles/%s" % path, 'r')
        head, content = f.read().replace("\r\n", "\n").split("\n\n", 1)
        f.close()
        self.headers = ArticleHeaders(head)
        self.raw_content = unicode(content.decode("utf-8"))
        self.soup = BeautifulSoup(self.raw_content)

        self.complete_headers()
        self.process_content()

    def is_live(self):
        """Check meta info to see, if this article is live"""
        if self.headers.available and self.headers.available < settings.now:
            return False
        if self.headers.issued and self.headers.issued > settings.now:
            return False
        if self.headers.valid and self.headers.valid < settings.now:
            return False
        if "exclude" in self.headers.status:
            return False
        if "draft" in self.headers.get("status", []) and not settings.DEBUG:
            return False
        return True

    def complete_headers(self):
        """Set default headers, that are missing"""
        defaults = {
            "ID": str(self.url),
            "date": settings.now,
            "type": "Text",
            "format": "application/xhtml+xml",
            "status": [],
            "language": self.hard_language or settings.LANGUAGE,
        }
        self.headers.set_defaults(defaults)
        if "title" not in self.headers:
            if "standalone" in self.headers.status:
                self.process_content()
                self.headers.title = self.soup.html.head.title.string
            else:
                self.headers.title = ""
        if "description" not in self.headers:
            self.process_content()
            if "abstract" in self.headers:
                self.headers.description = self.headers.abstract
            elif "standalone" in self.headers.status:
                self.headers.description = generate_description(unicode(self.soup.body).replace(u'<!--<!--', u'<!--').replace(u'-->-->', u'-->'))
            else:
                self.headers.description = generate_description(self.__unicode__())

    class MyHtmlFormatter(HtmlFormatter):
        def __init__(self, hl_lines=None):
            super(Article.MyHtmlFormatter, self).__init__(encoding='UTF-8', classprefix="s_", hl_lines=hl_lines)

        def wrap(self, inner, outfile):
            yield (0, '<ol class="highlight">')
            for i, (c, l) in enumerate(inner):
                if c != 1:
                    yield t, value
                if i+1 in self.hl_lines:
                    yield (c, '<li class="hll"><code>'+l+'</code></li>')
                else:
                    yield (c, '<li><code>'+l+'</code></li>')
            yield (0, '</ol>')

        def _highlight_lines(self, tokensource):
            for tup in tokensource:
                yield tup

    def process_content(self):
        """Change the raw content to a renderable state

        This contains syntax highlighting but not URI scheme resolving.
        The latter is done in self.save(). This function works exclusively
        upon self.soup."""
        if self.processed:
            return True
        elif "standalone" in self.headers.status:
            self.processed = True
            return True
        # Markup cleaning
        # see http://code.davidjanes.com/blog/2009/02/05/turning-garbage-html-into-xml-parsable-xhtml-using-beautiful-soup/
        for item in self.soup.findAll():
            for index, ( name, value ) in enumerate(item.attrs):
                if value == None:
                    item.attrs[index] = ( name, name )
        # Syntax highlighting:
        pres = self.soup.findAll("pre", {"data-lang": re.compile(r".+")})
        for pre in pres:
            ArticleFormatter = Article.MyHtmlFormatter(hl_lines=pre.get("data-hl", "").split(","))
            lang = pre["data-lang"]
            text = _unescape(pre.renderContents())
            try:
                if lang in self.lexers:
                    if isinstance(self.lexers[lang], Lexer):
                        lexer = self.lexers[lang]
                    else:
                        lexer = get_lexer_by_name(self.lexers[lang][0], stripnl=False, **self.lexers[lang][1])
                else:
                    lexer = get_lexer_by_name(lang, stripnl=False)
            except pygments.util.ClassNotFound:
                logging.warning("Couldn't find lexer for %s" % lang)
                lexer = guess_lexer(text)
            result = pygments.highlight(text, lexer, ArticleFormatter)
            highlighted = BeautifulSoup(result)
            for at, val in pre.attrs:
                if at == "class":
                    highlighted.ol[at] += u" "+val
                else:
                    highlighted.ol[at] = val
            pre.replaceWith(highlighted.ol)
        self.processed = True

    def save(self, **ctx):
        """Save the article to a file

        If it's a standalone, save it directly. Else send the
        context to the corresponding template. In order to recognize
        the "id:" URI scheme, the parameter **ctx must contain
        the value "articles", against which's content the URI is
        checked."""
        dr = ""
        if "draft" in self.headers.status:
            dr = "*DRAFT* "
        logging.debug(dr + self.url.get())
        if "draft" in self.headers.status and not settings.DEBUG:
            raise ValueError("Can't save drafts")
        if "noindex" not in self.headers.get("robots", ""):
            template_engine.add_to_index(self.url, self.__unicode__(), self.headers.language)
        if "standalone" in self.headers.status:
            template_engine.write_to(self.url.get_path(), self.__unicode__())
        else:
            if "articles" in ctx:
                # resolve the "id:" pseudo-scheme
                ax = self.soup.findAll("a", href=re.compile(r"^id:"))
                for a in ax:
                    id = a['href'][3:]
                    for a2 in ctx['articles']:
                        if a2.headers.ID == id:
                            a['href'] = aa(a2.url)
                            break
                # resolve links to Requires and isRequiredBy
                # TODO: Do we need multiple Requires?
                if 'Requires' in self.headers:
                    for a in ctx['articles']:
                        if a.headers.ID == self.headers.Requires:
                            self.headers.Requires = a
                            break
                if 'IsRequiredBy' in self.headers:
                    for a in ctx['articles']:
                        if a.headers.ID == self.headers.IsRequiredBy:
                            self.headers.IsRequiredBy = a
                            break
            for protocol, url_scheme in settings.PROTOCOLS.iteritems():
                # resolve all pseudo-schemes
                ax = self.soup.findAll(href=re.compile(u"^%s:" % protocol))
                ix = self.soup.findAll(src=re.compile(u"^%s:" % protocol))
                for a in ax:
                    if callable(url_scheme):
                        a['href'] = url_scheme(a['href'][len(protocol)+1:])
                    else:
                        a['href'] = url_scheme % a['href'][len(protocol)+1:]
                    if a.get('class', False):
                        a['class'] += " protocol_%s" % protocol
                    else:
                        a['class'] = "protocol_%s" % protocol
                for a in ix:
                    if callable(url_scheme):
                        a['src'] = url_scheme(a['src'][len(protocol)+1:])
                    else:
                        a['src'] = url_scheme % a['src'][len(protocol)+1:]
                    if a.get('class', False):
                        a['class'] += " protocol_%s" % protocol
                    else:
                        a['class'] = "protocol_%s" % protocol
            template_engine.render_article(self, **ctx)

    def __unicode__(self):
        # work around bug in BeautifulSoup
        return unicode(str(self.soup).decode('UTF-8'))

    def __hash__(self):
        s = hashlib.sha224(self.headers.date.strftime("%Y-%m-%dT%H:%m:%s") +
                           "_" + self.headers.ID).hexdigest()
        return int(s, 16)

    def __cmp__(self, other):
        """Compare articles by date first, ID second"""
        s = self.headers.date.strftime("%Y-%m-%dT%H:%m:%s") + "_" + self.headers.ID
        if isinstance(other, basestring):
            o = other
        else:
            o = other.headers.date.strftime("%Y-%m-%dT%H:%m:%s") + "_" + other.headers.ID
        return cmp(o, s)

