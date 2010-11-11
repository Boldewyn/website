""""""


import urllib


def u(string):
    """URL quoting without the slash"""
    string = string.encode("utf8")
    return urllib.quote_plus(string, "/")


