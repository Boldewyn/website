""""""


try:
    import json
except ImportError:
    import simplejson as json
import re
import urllib
from .settings import settings
from babel.dates import format_date
from babel import UnknownLocaleError


def urlquote(string):
    """URL quoting without the slash"""
    string = string.encode("utf8")
    return urllib.quote_plus(string, "/")


def aa(path):
    """Make a path absolute"""
    if re.match(r"[a-z0-9\-]+:", path) or path.startswith("//"):
        return path
    return settings.URL + urlquote(path.lstrip("/"))


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


