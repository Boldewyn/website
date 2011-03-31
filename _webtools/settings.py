""""""


import imp
import logging
import os
import sys
from datetime import datetime


_ = lambda s: s


class Settings(object):

    def __init__(self):
        self.h = {}
        h = {
            "BUILD_TARGET": "site",
            "CATEGORY": [],
            "CREATE_NEGOTIABLE_LANGUAGES": True,
            "DATE_FORMAT": "%Y-%m-%dT%H:%M:%S",
            "DEBUG": False,
            "DEFAULTS": {},
            "LANGUAGE": "en",
            "PAGINATE_N": 20,
            "PROTOCOLS": {
                "w": "http://en.wikipedia.org/wiki/%s",
                "g": "http://google.com/search?q=%s",
            },
            "URL": "http://localhost/",
        }

        if "/" in __file__:
            codebase = os.path.abspath(os.path.dirname(__file__)+"/..")
            sys.path.insert(0, codebase)
        else:
            codebase = os.path.abspath("..")
        self.h["CODEBASE"] = codebase

        try:
            config = imp.load_source("_config",
                         os.path.abspath("_config.py"))
        except (ImportError, IOError):
            logging.warning("No config imported!")
        else:
            for k,v in config.__dict__.iteritems():
                if k[0] != "_":
                    self.h[k] = v
            del config
        for k, v in h.iteritems():
            if k not in self.h:
                self.h[k] = v
        for k, v in h['PROTOCOLS'].iteritems():
            if k not in self.h['PROTOCOLS']:
                self.h['PROTOCOLS'][k] = v
        if "STATICURL" not in self.h:
            self.h["STATICURL"] = self.h["URL"]
        if "AUTHOR" not in self.h["DEFAULTS"]:
            self.h["DEFAULTS"]["AUTHOR"] = _(u"unknown")
        #self.h['languages'] = [x for x in os.listdir(codebase+"/_locale") \
        #                               if os.path.isdir(codebase+"/_locale/"+x)]
        self.h['languages'] = []
        if os.path.isdir("_locale") and codebase != os.path.abspath("."):
            self.h['languages'] += [x for x in os.listdir("_locale") \
                                            if os.path.isdir("_locale/"+x)]
        l = self.h['LANGUAGE']
        if l is not None and l not in self.languages:
            self.h['languages'].append(l)
        self.h['languages'].sort()
        # make lang entries unique
        self.h['languages'] = list(set(self.h['languages']))
        self.h['known_extensions'] = self.h['languages'] + self.h.get('KNOWN_EXTENSIONS', []) + \
                                     ["html", "htm", "xhtml", "xml", "xht", "php", "atom", "rdf", "rss", "py"]
        self.h['now'] = datetime.now()

    def __str__(self):
        return str(self.h)

    def __getattr__(self, name, default=None):
        """Get a setting, via dict method, too"""
        if name in self.h:
            return self.h[name]
        else:
            return default

    __getitem__ = __getattr__
    get = __getattr__

    def __setattr__(self, name, value):
        """Set a setting, via dict method, too"""
        if name == "h":
            object.__setattr__(self, name, value)
        else:
            self.h[name] = value

    __setitem__ = __setattr__

    def __delattr__(self, name):
       """Delete a setting, via dict method, too"""
       if name in self.h:
           del self.h[name]

    __delitem__ = __delattr__

    # Missing dict methods
    __len__ = lambda self: len(self.h)
    __contains__ = lambda self, v: self.h.__contains__(v)
    __iter__ = lambda self: self.h.__iter__()
    iterkeys = __iter__


settings = Settings()

