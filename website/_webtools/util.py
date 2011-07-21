""""""


import logging
import os
from website._webtools.settings import settings


logger = logging.getLogger("website.util")


def get_templates(dir=""):
    """Recursively fetch templates that need processing"""
    dir = dir.strip("/")
    if dir != "":
        dir += "/"
    templates = []
    for a in os.listdir("./"+dir):
        if os.path.isdir("./"+dir + a):
            if a[0] not in ["_", "."] and \
               not (dir + a).startswith(settings.ORIG_BUILD_TARGET+"/"):
                templates.extend(get_templates(dir + a))
        elif a.endswith(".mako"):
            templates.append(dir + a)
    return templates


def get_extensions(path):
    """Get the list of known extensions of a path"""
    base = os.path.basename(path)
    extensions = []
    probes = base.split(".")
    while len(probes) > 1 and probes[-1] in settings.known_extensions:
        extensions.append(probes.pop())
    if not len(probes):
        probes.append('index')
    return ".".join(probes), extensions


