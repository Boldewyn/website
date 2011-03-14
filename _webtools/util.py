""""""


import os
import shutil
from .settings import settings
try:
    from shutil import ignore_patterns
except ImportError:
    import fnmatch
    def ignore_patterns(*patterns):
        def _ignore_patterns(path, names):
            ignored_names = []
            for pattern in patterns:
                ignored_names.extend(fnmatch.filter(names, pattern))
            return set(ignored_names)
        return _ignore_patterns

    def copytree(src, dst, symlinks=False, ignore=None):
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()
        os.makedirs(dst)
        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    copytree(srcname, dstname, symlinks, ignore)
                else:
                    shutil.copy2(srcname, dstname)
            except (IOError, os.error), why:
                errors.append((srcname, dstname, str(why)))
            except Error, err:
                errors.extend(err.args[0])
        try:
            shutil.copystat(src, dst)
        except OSError, why:
            if WindowsError is not None and isinstance(why, WindowsError):
                pass
            else:
                errors.extend((src, dst, str(why)))
        if errors:
            raise Error, errors
else:
    from shutil import copytree


def copy_statics():
    """"""
    shutil.rmtree(settings.BUILD_TARGET, True)
    copytree(".", settings.BUILD_TARGET,
            ignore=ignore_patterns("_*", ".*swp", ".git*",
                                   "*.mako", "Makefile"))


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
    return ".".join(probes), extensions


def sort_extensions(path):
    """Sort extensions to a useful order, remove duplicates"""
    dirname = os.path.dirname(path)
    basename, extensions = get_extensions(path)
    def extcmp(a, b):
        if a == "php":
            return -1
        elif b == "php":
            return 1
        elif a in settings.languages and b not in settings.languages:
            return -1
        elif a not in settings.languages and b in settings.languages:
            return 1
        else:
            return cmp(a, b)
    extensions.sort(extcmp)
    exteinsions = list(set(extensions))
    return "%s/%s.%s" % (dirname, basename, ".".join(extensions))

