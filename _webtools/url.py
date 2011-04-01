""""""


import os.path
from urllib import quote
from .settings import settings


class Url(object):

    def __init__(self, path):
        if not isinstance(path, unicode):
            path = path.decode("UTF-8")
        path = path.lstrip(u"/")
        self.dir = u""
        if u"/" in path:
            self.dir = os.path.dirname(path).lstrip(u"/") + u"/"
        basename = os.path.basename(path) or (u"index.%s.html" % settings.LANGUAGE)
        self.base, self.extensions = self._get_base_and_extensions(basename)
        self.basename = self._sort_extensions()

    def get_head(self):
        """Get the head and basename without extensions"""
        return settings.URLPATH + self._q(self.dir + self.base)

    def get_extensions(self):
        """Get the extensions"""
        return self.extensions

    def get_path(self):
        """Get the relative part of the URL"""
        return self._q(self.dir + self.basename)

    def get(self):
        """Get the absolute URL of this instance"""
        return settings.URLPATH + self.get_path()
    __str__ = get
    __unicode__ = lambda self: unicode(self.get())

    def copy(self):
        """Create a copy of this instance"""
        return Url(self.dir + self.basename)

    def switch_language(self, lang):
        """Change the language component of the URI"""
        self.extensions = filter(lambda s: s not in settings.languages, self.extensions)
        self.extensions.insert(0, lang)
        self.basename = self._sort_extensions()
        return self

    def _q(self, v):
        if not isinstance(v, str):
            v = v.encode("UTF-8")
        return quote(v, "/")

    def _get_base_and_extensions(self, basename):
        """Get the plain basename and the known extensions"""
        extensions = []
        probes = basename.split(".")
        while len(probes) > 1 and probes[-1] in settings.known_extensions:
            extensions.append(probes.pop())
        return u".".join(probes), extensions

    def _sort_extensions(self):
        """Make sure, that extensions are in a useful order"""
        def extcmp(a, b):
            if a == "php":
                return 1
            elif b == "php":
                return -1
            elif a in settings.languages and b not in settings.languages:
                return -1
            elif a not in settings.languages and b in settings.languages:
                return 1
            else:
                return cmp(a, b)
        if not len(self.extensions):
            return self.base
        else:
            self.extensions = list(set(self.extensions))
            self.extensions.sort(extcmp)
            return u"%s.%s" % (self.base, u".".join(self.extensions))

