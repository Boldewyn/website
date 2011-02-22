""""""


try:
    import json
except ImportError:
    import simplejson as json
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
from .util import get_extensions


class TemplateEngine(object):
    """"""

    def __init__(self):
        self.indexdata = {}
        self.ctx = {}
        self.sitemap = []
        self.lookup = TemplateLookup(directories=[".", settings.CODEBASE], default_filters=["x"])
                                     #module_directory="_webtools/mod")
        self.ctx['all_languages'] = settings.languages

    def set(self, name, value):
        self.ctx[name] = value

    def collect_page_requisites(self):
        if "articles" in self.ctx:
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

    def render_paginated(self, template, path, **ctx):
        """Render a template, but break the content into multiple pages

        TODO: The below stripping of articles with hard_language set will
        make this approach imprecise.
        """
        pl = settings.PAGINATE_N
        articles = ctx["a"][:]
        if len(articles) > pl:
            if "pag" not in ctx:
                ctx["pag"] = {}
            if "base" not in ctx["pag"]:
                ctx["pag"]["base"] = "/".join(path.split("/")[:-1])+\
                                     "/page_%s"
            pages = (len(articles)-1) // pl + 1
            ctx["pag"]["first"] =  path
            ctx["pag"]["pages"] = pages
            for p in range(1, pages):
                ctx["pag"]["cur"] = p+1
                ctx["a"] = articles[p*pl:(p+1)*pl]
                self.render_template(template,
                            ctx["pag"]["base"]%(p+1)+".html", **ctx)
            ctx["pag"]["cur"] = 1
            ctx["a"] = articles[:pl]
        self.render_template(template, path, **ctx)

    def render_template(self, template, path, **ctx):
        """Render a template within the given context ctx"""
        self.collect_page_requisites()
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        if "url" not in ctx:
            ctx["url"] = path
        filename = template
        if "full_path" not in ctx or ctx["full_path"] == False:
            filename = "_templates/"+template+".mako"
        tpl = self.lookup.get_template(filename)
        if not settings.CREATE_NEGOTIABLE_LANGUAGES or ctx.get("nolang", False):
            ctx["_"] = lambda s: unicode(s)
            if "lang" in ctx:
                ctx["_"] = get_gettext(ctx["lang"])
            else:
                ctx["lang"] = settings.LANGUAGE
            try:
                self.write_to(path, tpl.render_unicode(**ctx), ctx.get("date", settings.now))
            except:
                print exceptions.text_error_template().render()
                exit()
        else:
            articles = ctx.get('articles')[:]
            a = ctx.get('a', [])[:]
            for lang in settings.languages:
                ctx["_"] = get_gettext(lang)
                ctx["lang"] = lang
                ctx["articles"] = filter(lambda a: a.hard_language in [lang, None], articles)
                if len(a):
                    ctx["a"] = filter(lambda a: a.hard_language in [lang, None], a)
                try:
                    self.write_to(path+"."+lang, tpl.render_unicode(**ctx), ctx.get("date", settings.now))
                except:
                    print exceptions.text_error_template().render()
                    exit()
        sitemap = [path, ctx.get("date", settings.now), "yearly", 0.5]
        if "sitemap_lastmod" in ctx:
            sitemap[1] = ctx["sitemap_lastmod"]
        if "sitemap_changefreq" in ctx:
            sitemap[2] = ctx["sitemap_changefreq"]
        if "sitemap_priority" in ctx:
            sitemap[3] = ctx["sitemap_priority"]
        self.sitemap.append(sitemap)

    def write_to(self, path, content, mtime=settings.now, sort_extensions=True):
        """Write content to a file"""
        if sort_extensions:
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
            path = "%s/%s.%s" % (dirname, basename, ".".join(extensions))
        save_path = os.path.join(settings.BUILD_TARGET, path.lstrip("/"))
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        if ".php." in os.path.basename(path):
            save_path = re.sub(r"^(.+)\.php\.(.+)$", r"\1.\2.php", save_path)
        to = open(save_path, 'w')
        try:
            to.write(content.encode("UTF-8"))
        except:
            print exceptions.text_error_template().render()
            exit()
        to.close()
        if not isinstance(mtime, datetime):
            mtime = settings.now
        os.utime(save_path, (timegm(mtime.timetuple()), timegm(mtime.timetuple())))

    def render_sitemap(self):
        """Render a sitemap.xml"""
        if not os.path.isfile(settings.BUILD_TARGET+"/sitemap.xml"):
            data = {"sitemap": self.sitemap}
            tpl = self.lookup.get_template("_templates/sitemap.xml.mako")
            data["local_sitemap"] = ""
            if os.path.isfile("_doc/local_sitemap.xml"):
                data["local_sitemap"] = open("_doc/local_sitemap.xml", "rb").read()
            to = open(os.path.join(settings.BUILD_TARGET, "sitemap.xml"), 'w')
            try:
                to.write(tpl.render_unicode(**data).encode("UTF-8"))
            except:
                print exceptions.text_error_template().render()
                exit()
            to.close()
        else:
            print "Sitemap already exists."

    def add_to_index(self, path, content):
        """Add content to the search index"""
        self.indexdata[path.lstrip("/")] = content

    def make_index(self):
        """Generate an index of all files' contents"""
        index = open(os.path.join(settings.BUILD_TARGET, "index.json"), "wb")
        data = self.indexdata.copy()
        W = re.compile(r'\W+', re.U)
        for k in data:
            data[k] = list(set(W.split(re.sub(r'<.+?>', '', data[k]))))
        index.write(json.dumps(data))
        index.close()


template_engine = TemplateEngine()


def get_tagcloud(articles, offset=1):
    """Get all tags from the categories"""
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
    rtags.sort()
    return rtags


def get_categories(articles):
    """Get all categories from the articles"""
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

