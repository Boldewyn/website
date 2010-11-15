""""""


import gettext
import os
from datetime import datetime
from mako.template import Template
from mako import exceptions
from mako.lookup import TemplateLookup
from .settings import settings


class TemplateEngine(object):
    """"""

    def __init__(self):
        self.ctx = {}
        self.sitemap = []
        self.lookup = TemplateLookup(directories=["."], default_filters=["x"],
                                     module_directory="_webtools/mod")

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
        """"""
        pl = settings.PAGINATE_N
        articles = ctx["a"][:]
        if len(articles) > pl:
            if "pag" not in ctx:
                ctx["pag"] = {}
            if "base" not in ctx["pag"]:
                ctx["pag"]["base"] = "page_%s.html"
            pages = (len(articles)-1) // pl + 1
            ctx["pag"]["first"] =  path.split("/")[-1]
            ctx["pag"]["pages"] = pages
            for p in range(1, pages):
                ctx["pag"]["cur"] = p+1
                ctx["a"] = articles[p*pl:(p+1)*pl]
                self.render_template(template,
                        "/".join(path.split("/")[:-1]) +
                        "/" + ctx["pag"]["base"]%(p+1), **ctx)
            ctx["pag"]["cur"] = 1
            ctx["a"] = articles[:pl]
        self.render_template(template, path, **ctx)

    def render_template(self, template, path, **ctx):
        """"""
        #for lang in settings.get("LANGUAGES", ["en"]):
        self.collect_page_requisites()
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        t = gettext.translation("website", "_locale", fallback=True)
        ctx["_"] = t.ugettext
        tpl = Template(filename="_templates/"+template+".mako",
                       module_directory="_webtools/mod",
                       lookup=self.lookup, default_filters=["x"])
        try:
            self.write_to(path, tpl.render_unicode(**ctx))
        except:
            print exceptions.text_error_template().render()
            exit()
        sitemap = [path, datetime.now(), "yearly", 0.5]
        if "sitemap_lastmod" in ctx:
            sitemap[1] = ctx["sitemap_lastmod"]
        if "sitemap_changefreq" in ctx:
            sitemap[2] = ctx["sitemap_changefreq"]
        if "sitemap_priority" in ctx:
            sitemap[3] = ctx["sitemap_priority"]
        self.sitemap.append(sitemap)

    def write_to(self, path, content):
        """"""
        save_path = os.path.join(settings.BUILD_TARGET, path.lstrip("/"))
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        to = open(save_path, 'w')
        try:
            to.write(content.encode("UTF-8"))
        except:
            print exceptions.text_error_template().render()
            exit()
        to.close()

    def render_sitemap(self):
        """Render a sitemap.xml"""
        if not os.path.isfile(settings.BUILD_TARGET+"/sitemap.xml"):
            data = {"sitemap": self.sitemap}
            tpl = Template(filename="_templates/sitemap.xml.mako",
                           module_directory='_webtools/mod',
                           lookup=self.lookup, default_filters=["x"])
            data["local_sitemap"] = ""
            if os.path.isfile("_doc/local.sitemap"):
                data["local_sitemap"] = open("_doc/local.sitemap", "rb").read()
            to = open(os.path.join(settings.BUILD_TARGET, "sitemap.xml"), 'w')
            try:
                to.write(tpl.render_unicode(**data).encode("UTF-8"))
            except:
                print exceptions.text_error_template().render()
                exit()
            to.close()
        else:
            print "Sitemap already exists."


template_engine = TemplateEngine()


def get_tagcloud(articles, offset=1):
    """Get all tags from the categories"""
    tags = {}
    for article in articles:
        for tag in article.headers['SUBJECT']:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
    if offset > 1:
        for tag, n in tags.iteritems():
            if n < offset:
                del tags[tag]
    return tags


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
    categories.sort()
    return categories


def get_archives(articles):
    """Get all archive links"""
    dates = []
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates.append(d)
    return dates

