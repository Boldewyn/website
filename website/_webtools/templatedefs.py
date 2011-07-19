""""""


try:
    import json
except ImportError:
    import simplejson as json
import re
import os
import urllib
from .articles import Article
from .settings import settings
from .url import Url
try:
    from babel.dates import format_date
    from babel import UnknownLocaleError
except ImportError:
    def format_date(datetime, locale=None):
        return datetime.strftime("%Y-%m-%d %H:%M")


def urlquote(string):
    """URL quoting without the slash"""
    string = string.encode("utf8")
    return urllib.quote(string, "/")


def aa(path):
    """Make a path absolute"""
    if isinstance(path, Url):
        return path.get()
    elif re.match(r"[a-z0-9\-]+:", path) or path.startswith("//"):
        return path
    return Url(path).get()


def laa(lang=None, url=None):
    """Make a path absolute, add language"""
    if lang is None:
        lang = settings.LANGUAGE
    def _laa(path):
        if isinstance(path, Article):
            if path.headers.translation:
                for t in path.headers.translation:
                    if t.headers.language.startswith(lang):
                        return t.url.get()
            return path.url.copy().switch_language(lang).get()
        elif isinstance(path, Url):
            return path.copy().switch_language(lang).get()
        else:
            return Url(path).switch_language(lang).get()
    if url is None:
        return _laa
    else:
        return _laa(url)


def static(path):
    """Make a static path absolute"""
    if re.match(r"[a-z0-9\-]+:", path) or path.startswith("//"):
        return path
    return settings.STATICURL.rstrip("/") + "/" + urlquote(path.lstrip("/"))


def repl(base, path="#a#"):
    """Replace placeholders with paths"""
    base = base.replace("#a#", path.rstrip("/") + "/")
    base = base.replace("#s#", settings.STATICURL.rstrip("/") + "/")
    return base


def date(datetime, lang):
    """Format a date depending on current locale"""
    if lang is None:
        lang = settings.LANGUAGE
    try:
        r = format_date(datetime, locale=lang)
    except UnknownLocaleError:
        r = format_date(datetime, locale=settings.LANGUAGE)
    return r


def jsq(string):
    """"""
    return json.JSONEncoder().encode(unicode(string))[1:-1]


def get_cat_title(_, category):
    """Get the 'true' title of a category"""
    try:
      title = _(settings.CATEGORY[category]["title"])
    except:
      title = category
    return title


def strip_tags(s):
    """Strip HTML tags"""
    return re.sub(ur"<.+?>", ur"", s)


def month(_2, i):
    """Return the textual representation of a month"""
    _ = lambda s: s
    months = [_('Jan.'), _('Feb.'), _('Mar.'), _('Apr.'), _('May'), _('June'), _('July'), _('Aug.'), _('Sep.'), _('Oct.'), _('Nov.'), _('Dec.')]
    return _2(months[i-1])

