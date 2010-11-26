""""""


import re
import urllib
from .settings import settings


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


