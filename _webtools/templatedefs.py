""""""


import re
import urllib
from .settings import settings


def uu(string):
    """URL quoting without the slash"""
    string = string.encode("utf8")
    return urllib.quote_plus(string, "/")


def aa(path):
    """Make a path absolute"""
    if re.match(r"[a-z0-9\-]+:", path) or path.startswith("//"):
        return path
    return settings.URL + uu(path.lstrip("/"))


