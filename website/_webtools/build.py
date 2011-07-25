""""""


import glob
import logging
import os
import shutil
from website._webtools.settings import settings
from website._webtools.articles import get_articles
from website._webtools.categories import render, render_feed
from website._webtools.templates import template_engine
from website._webtools.util import get_templates
from website._webtools.plugins import load_plugins, fire_hook
try:
    from shutil import ignore_patterns
except ImportError:
    # Workaround for Python < 2.5
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


logger = logging.getLogger("website.build")


def copy_statics():
    """Copy static files from project to final site folder"""
    shutil.rmtree(settings.BUILD_TARGET, True)
    copytree(".", settings.BUILD_TARGET,
            ignore=ignore_patterns("_*", ".*swp", ".git*",
                                   "*.mako", "Makefile", *settings.get("IGNORED_PATTERNS", [])))


def build():
    """Build the final website"""
    fire_hook("build.start")
    load_plugins()
    settings.ORIG_BUILD_TARGET = settings.BUILD_TARGET.rstrip("/")
    settings.BUILD_TARGET = os.path.abspath(settings.BUILD_TARGET)
    copy_statics()
    all_articles = get_articles()
    articles = [a for a in all_articles \
                if "noref" not in a.headers.status]
    articles.sort()
    template_engine.set_articles(articles)
    for article in all_articles:
        article.save(articles=articles)
    render(articles)
    for template in get_templates():
        template_engine.render_template(template,
                template.replace(".mako", ".html"), a=articles, articles=articles)
    if not glob.glob(settings.BUILD_TARGET+"/index.html*") and \
       not glob.glob(settings.BUILD_TARGET+"/index.xhtml*"):
        template_engine.render_paginated("index", "index.html",
                                         a=articles, articles=articles)
    if not os.path.isfile(settings.BUILD_TARGET+"/feed.xml"):
        render_feed(articles)
    template_engine.render_sitemap()
    template_engine.make_index()
    fire_hook("build.end")
    return 0

