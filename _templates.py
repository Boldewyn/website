""""""


import gettext
import os
from mako.template import Template
from mako import exceptions
from mako.lookup import TemplateLookup
from _settings import settings


class TemplateEngine(object):
    """"""

    def __init__(self):
        self.ctx = {}

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
            def sort_by(a, b):
                return cmp(a.headers.date, b.headers.date) or \
                       cmp(a.headers.ID, b.headers.ID)
            self.ctx["latest_articles"].sort(sort_by)
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
        #for lang in settings.LANGUAGES:
        self.collect_page_requisites()
        nctx = self.ctx.copy()
        nctx.update(ctx)
        ctx = nctx
        t = gettext.translation('website', "_locale", fallback=True)
        ctx["_"] = t.ugettext
        save_path = os.path.join(settings.BUILD_TARGET, path.lstrip("/"))
        _lookup = TemplateLookup(directories=["."], default_filters=["x"], module_directory='_mod')
        tpl = Template(filename="_templates/"+template+'.mako', module_directory='_mod',
                    lookup=_lookup, default_filters=["x"])
        if not os.path.isdir(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        to = open(save_path, 'w')
        try:
            to.write(tpl.render_unicode(**ctx).encode("UTF-8"))
        except:
            print exceptions.text_error_template().render()
            exit()
        to.close()


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

