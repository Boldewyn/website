""""""


from os.path import abspath as _a
from os.path import dirname as _d
from .settings import settings


if "/" in __file__:
    settings.CODEBASE = _a(_d(__file__)+"/..")
else:
    settings.CODEBASE = _a("..")

