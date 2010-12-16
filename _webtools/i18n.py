""""""


import gettext
import os
from .settings import settings


class WebtoolsTranslations(gettext.GNUTranslations):
    """A little bit of introspection into GNUTranslations."""
    def update(self, other):
        """Allow to update the catalog with the one of another instance"""
        self._catalog.update(other._catalog)


def get_gettext(lang):
    """Return the ready to use '_' function"""
    t = gettext.translation("website", localedir=settings.CODEBASE+"/_locale",
                            languages=[lang], class_=WebtoolsTranslations,
                            fallback=True)
    if settings.CODEBASE != os.path.abspath("."):
        u = gettext.translation("website", localedir="_locale", languages=[lang],
                                class_=WebtoolsTranslations, fallback=True)
        t.update(u)
    c_ = t.ugettext
    return c_

