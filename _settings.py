""""""


class Settings(object):

    def __init__(self):
        try:
            config = __import__("_config", level=1)
        except ImportError:
            pass
        else:
            for k,v in config.__dict__.iteritems():
                if k[0] != "_":
                    setattr(self, k, v)
            del config

    def __str__(self):
        return str(self.__dict__)

    def __getattr__(self, name):
        return None


settings = Settings()

