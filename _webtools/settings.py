""""""


import imp
import os


class Settings(object):

    def __init__(self):
        self.h = {}
        h = {
            "DATE_FORMAT": "%Y-%m-%dT%H:%M:%S",
            "DEBUG": False,
            "CREATE_NEGOTIABLE_LANGUAGES": True,
            "CATEGORY": [],
            "PAGINATE_N": 20,
            "URL": "http://localhost/",
            "LANGUAGE": "en",
            "PROTOCOLS": {
                "w": "http://en.wikipedia.org/wiki/%s",
                "g": "http://google.com/search?q=%s",
            },
            "DEFAULTS": {},
        }

        try:
            config = imp.load_source("_config",
                         os.path.abspath("./_config.py"))
        except ImportError:
            print "No config imported!"
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
            self.h["DEFAULTS"]["AUTHOR"] = "unknown"
        self.h['languages'] = [x for x in os.listdir("_locale") if os.path.isdir("_locale/"+x)]
        l = self.h['LANGUAGE']
        if l not in self.languages:
            self.h['languages'].append(l)
        self.h['languages'].sort()
        self.h['known_extensions'] = self.h['languages'] + self.h.get('KNOWN_EXTENSIONS', []) + \
                                     ["html", "htm", "xhtml", "xht", "php"]

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

