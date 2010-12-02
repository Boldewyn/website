""""""


import os


class Settings(object):

    def __init__(self):
        self.h = {
            "DATE_FORMAT": "%Y-%m-%dT%H:%M:%S",
            "DEBUG": False,
            "CREATE_NEGOTIABLE_LANGUAGES": True,
            "DEFAULTS": [],
            "PAGINATE_N": 20,
        }

        try:
            config = __import__("_config", level=1)
        except ImportError:
            print "No config imported!"
        else:
            for k,v in config.__dict__.iteritems():
                if k[0] != "_":
                    self.h[k] = v
            del config
        self.h['languages'] = [x for x in os.listdir("_locale") if os.path.isdir("_locale/"+x)]
        l = dict(self.DEFAULTS).get('LANGUAGE', '')
        if l not in self.languages:
            self.h['languages'].append(l)
        self.h['languages'].sort()

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

