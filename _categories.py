""""""


import os
from mako.template import Template
from mako.lookup import TemplateLookup


_dir = os.path.dirname(__file__)
_lookup = TemplateLookup(directories=["."])


def render_template(template, path, **ctx):
    """"""
    template = Template(filename="_templates/"+template+
                                      '.mako', lookup=_lookup)
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    to = open(path, 'w')
    to.write(template.render(**ctx))
    to.close()


def render_tags(target, articles):
    """"""
    tags = {}
    for article in articles:
        a_tags = getattr(article.headers, 'SUBJECT', [])
        for a_tag in a_tags:
            if a_tag not in tags:
                tags[a_tag] = []
            tags[a_tag].append(article)
    for tag, a in tags.iteritems():
        render_template("tag", os.path.abspath(target)+"/tag/"+
                        tag+"/index.html", **locals())


def render_archives(target, articles):
    """"""
    dates = {}
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates[d] = []
        dates[d].append(article)
    for date, a in dates.iteritems():
        render_template("archive", os.path.abspath(target)+"/archive/"+
                        date+"/index.html", **locals())


def render_indexes(target, articles):
    """"""
    categories = {}
    for article in articles:
        if article.category not in categories:
            categories[article.category] = []
        categories[article.category].append(article)
    for category, a in categories.iteritems():
        if category+"/index.html" not in a:
            render_template("category", os.path.abspath(target)+"/"+
                            category+"/index.html", **locals())

