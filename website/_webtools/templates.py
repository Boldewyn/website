""""""


try:
    import json
except ImportError:
    import simplejson as json
import logging
import sqlite3
import math
import os
import re
from datetime import datetime
from mako.template import Template
from mako import exceptions
from mako.lookup import TemplateLookup
from calendar import timegm
from .settings import settings
from .i18n import get_gettext
from .url import Url


logger = logging.getLogger("website.templates")


class TemplateEngine(object):
    """"""

    def __init__(self):
        self.indexdata = {}
        self.sitemap = []
        self.lookup = TemplateLookup(directories=[".", settings.CODEBASE], default_filters=["x"])
        self.renderers = []
        if settings.NEGOTIATE_EXTENSIONS:
            for lang in settings.languages:
                self.renderers.append(LocalizedRenderer(lang))
        else:
            self.renderers.append(LocalizedRenderer(None))

    def set_articles(self, articles):
        for r in self.renderers:
            r.set_articles(articles)

    def render_paginated(self, template, path, **ctx):
        """Render a template, but break the content into multiple pages"""
        for r in self.renderers:
            r.render_paginated(template, path, **ctx)

    def render_article(self, article, **ctx):
        """Render an article"""
        for r in self.renderers:
            r.render_article(article, **ctx)

    def render_template(self, template, path, **ctx):
        """Render a template within the given context ctx"""
        for r in self.renderers:
            r.render_template(template, path, **ctx)

    def write_to(self, path, content, mtime=settings.now):
        """Write content to a file

        The file will be written to a subfolder of
        settings.BUILD_TARGET.

        The modification time will be set to mtime. If
        sort_ext is True, the extensions will be
        sorted in a way to be useful for Apache's mod_
        negotiation.
        """
        save_path = os.path.join(settings.BUILD_TARGET, path.lstrip("/"))
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        to = open(save_path, 'w')
        try:
            to.write(content.encode("UTF-8"))
        except:
            logger.critical(exceptions.text_error_template().render())
            exit()
        to.close()
        if not isinstance(mtime, datetime):
            mtime = settings.now
        os.utime(save_path, (timegm(mtime.timetuple()), timegm(mtime.timetuple())))
        return save_path

    def render_sitemap(self):
        """Render a sitemap.xml"""
        if not os.path.isfile(settings.BUILD_TARGET+"/sitemap.xml"):
            for r in self.renderers:
                self.sitemap.extend(r.get_sitemap())
            data = {"sitemap": self.sitemap}
            tpl = self.lookup.get_template("_templates/sitemap.xml.mako")
            data["local_sitemap"] = ""
            data['settings'] = settings
            if os.path.isfile("_doc/local_sitemap.xml"):
                data["local_sitemap"] = open("_doc/local_sitemap.xml", "rb").read()
            to = open(os.path.join(settings.BUILD_TARGET, "sitemap.xml"), 'w')
            try:
                to.write(tpl.render_unicode(**data).encode("UTF-8"))
            except:
                logger.critical(exceptions.text_error_template().render())
                exit()
            to.close()
        else:
            logger.info("Sitemap already exists")

    def add_to_index(self, url, content, lang=None):
        """Add content to the search index"""
        if settings.NEGOTIATE_EXTENSIONS:
            lang = lang or settings.LANGUAGE
            if set(settings.languages) & set(url.get_extensions()):
                # hardcoded language
                self.indexdata[url.get()] = content
            else:
                self.indexdata[url.copy().switch_language(lang).get()] = content
        else:
            self.indexdata[url.get()] = content

    def make_index(self):
        """Generate an index of all files' contents"""
        type = settings.get("INDEX", False)
        if type:
            data = self.indexdata.copy()
            W = re.compile(r'\W+', re.U)
            for k in data:
                data[k] = list(set(W.split(re.sub(r'<.+?>', '', data[k].lower()))))
                data[k] = filter(lambda s: s and len(s) > 1, data[k])
            if type in ("ALL", "JSON"):
                index = open(os.path.join(settings.BUILD_TARGET, "index.json"), "wb")
                index.write(json.dumps(data))
                index.close()
            if type in ("ALL", "SQLITE"):
                sqlite3.enable_callback_tracebacks(settings.DEBUG)
                db = sqlite3.connect(os.path.join(settings.BUILD_TARGET, "index.sqlite"))
                cur = db.cursor()
                cur.execute('CREATE TABLE terms ( p, t )')
                for k in data:
                    for i in data[k]:
                        cur.execute('INSERT INTO terms (p, t) VALUES (?, ?)', (unicode(k), unicode(i)))
                cur.close()
                db.commit()
                db.close()
        return bool(type)


def get_tagcloud(articles, offset=1):
    """Get all tags from a set of articles"""
    def thresholds(mn, mx, steps=5):
        mn = float(mn)
        mx = float(mx)
        th = []
        for x in range(steps-1):
            th.append(mn + (1+x)*(mx-mn)/(steps))
        th.append(mx)
        return th
    tags = {}
    rtags = []
    min_n = 100000
    max_n = 0
    for article in articles:
        for tag in article.headers['SUBJECT']:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
    for tag, n in tags.iteritems():
        if n < offset:
            del tags[tag]
        if n > max_n:
            max_n = n
        if n < min_n:
            min_n = n
    th = thresholds(min_n, max_n)
    for tag, n in tags.iteritems():
        normed_n = 0
        while th[normed_n] < float(n):
            normed_n += 1
        rtags.append((tag, normed_n+1, n))
    rtags.sort(key=lambda s: s[0].lower())
    return rtags


def get_categories(articles):
    """Get all categories from a set of articles"""
    categories = []
    for article in articles:
        if article.category not in categories:
            categories.append(article.category)
        if "/" in article.category:
            rootcat = article.category.split("/")[0]
            if rootcat not in categories:
                categories.append(rootcat)
    def s(a, b):
        oa = settings.CATEGORY.get(a, {}).get("order", 100)
        ob = settings.CATEGORY.get(b, {}).get("order", 100)
        if oa == ob:
            return cmp(a, b)
        return cmp(oa, ob)
    categories.sort(s)
    return categories


def get_archives(articles):
    """Get all archive links"""
    dates = []
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates.append(d)
    return dates


class LocalizedRenderer(object):
    """Handle the rendering of stuff, one language at a time"""

    def __init__(self, lang, ctx=None):
        self.lang = lang
        self.ctx = ctx or {}
        self.ctx["lang"] = self.lang
        self.ctx["_"] = get_gettext(self.lang)
        self.sitemap = []
        self.lookup = TemplateLookup(directories=[".", settings.CODEBASE], default_filters=["x"])

    def set_articles(self, articles):
        """Set articles, that are needed to get tagcloud et al."""
        articles = articles[:]
        for article in articles:
            article.url.switch_language(self.lang)
        if self.lang is not None:
            self.ctx["articles"] = filter(lambda a: a.hard_language in (self.lang, None), articles)
        else:
            self.ctx["articles"] = articles
        self.collect_page_requisites()

    def collect_page_requisites(self):
        """generate page items out of the general context"""
        if "articles" not in self.ctx:
            raise ValueError
        if "categories" not in self.ctx:
            self.ctx["categories"] = get_categories(self.ctx["articles"])
        if "tagcloud" not in self.ctx:
            self.ctx["tagcloud"] = get_tagcloud(self.ctx["articles"])
        if "archives" not in self.ctx:
            self.ctx["archives"] = get_archives(self.ctx["articles"])
        self.ctx["latest_articles"] = list(self.ctx["articles"])
        self.ctx["latest_articles"].sort()
        self.ctx["latest_articles"] = self.ctx["latest_articles"][:5]
        self.ctx['settings'] = settings

    def render_article(self, article, **ctx):
        """Render an article"""
        if article.hard_language not in (self.lang, None):
            return False
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        filename = article.headers.get("template", "article")
        if not filename.endswith(".mako"):
            filename = "_templates/"+filename+".mako"
        url = article.url.copy().switch_language(self.lang)
        next = None
        prev = None
        for i, art in enumerate(self.ctx.get('articles', [])):
            if art == article:
                if len(self.ctx['articles']) > i+1:
                    prev = self.ctx['articles'][i+1]
                if i > 0:
                    next = self.ctx['articles'][i-1]
                break
        ctx.update({
            'url': url,
            'article': article,
            'articles': self.ctx['articles'],
            'content': article.__unicode__(),
            'next_article': next,
            'prev_article': prev,
        })
        tpl = self.lookup.get_template(filename)
        sitemap = [url, article.headers.date, "yearly", 0.5]
        date = article.headers.date
        if "modified" in article.headers:
            sitemap[1] = article.headers.modified
            date = article.headers.modified
        if "accrualperiodicity" in article.headers:
            sitemap[2] = article.headers.accrualperiodicity
        template_engine.write_to(url.get_path(), tpl.render_unicode(**ctx),
                                 date)
        self.sitemap.append(sitemap)
        return True

    def render_paginated(self, template, path, **ctx):
        """Render a template, but break the content into multiple pages"""
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        ctx.update({
            'articles': self.ctx['articles'],
        })
        pl = settings.PAGINATE_N
        articles = ctx["a"][:]
        if self.lang is not None:
            articles = filter(lambda a: a.hard_language in (self.lang, None), articles)
        path = path.lstrip("/")
        dirname = os.path.dirname(path)
        baseurl = Url(path).switch_language(self.lang)
        if len(articles) > pl:
            if "pag" not in ctx:
                ctx["pag"] = {}
            if "base" not in ctx["pag"]:
                ctx["pag"]["base"] = dirname + "/" + ctx["_"]("page_%s")
            pages = (len(articles)-1) // pl + 1
            ctx["pag"]["first"] = baseurl.get_path()
            ctx["pag"]["pages"] = pages
            for p in range(1, pages):
                ctx["pag"]["cur"] = p+1
                ctx["a"] = articles[p*pl:(p+1)*pl]
                self.render_template("_templates/%s.mako" % template,
                            Url(ctx["pag"]["base"]%(p+1) + ".html").switch_language(self.lang),
                            **ctx)
            ctx["pag"]["cur"] = 1
            ctx["a"] = articles[:pl]
        self.render_template("_templates/%s.mako" % template, baseurl, **ctx)

    def render_template(self, template, path, **ctx):
        """Render a template within the given context ctx"""
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        ctx.update({
            'articles': self.ctx['articles'],
        })
        if self.lang is not None and "a" in ctx:
            ctx["a"] = filter(lambda a: a.hard_language in (self.lang, None), ctx["a"])
        if not isinstance(path, Url):
            path = Url(path).switch_language(self.lang)
        else:
            path.switch_language(self.lang)
        ctx['url'] = path
        tpl = self.lookup.get_template(template)
        template_engine.write_to(ctx['url'].get_path(), tpl.render_unicode(**ctx),
                                 ctx.get("date", settings.now))
        sitemap = [ctx["url"].copy(), ctx.get("date", settings.now), "monthly", 0.5]
        self.sitemap.append(sitemap)

    def get_sitemap(self):
        """Return the current items of the sitemap"""
        return self.sitemap


template_engine = TemplateEngine()










