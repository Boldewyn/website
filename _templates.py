""""""


import os
from mako.template import Template
from mako import exceptions
from mako.lookup import TemplateLookup
from _settings import settings


_dir = os.path.dirname(__file__)
_lookup = TemplateLookup(directories=["."])


def render_template(template, path, **ctx):
    """"""
    ctx['settings'] = settings
    if "articles" in ctx and "tagcloud" not in ctx:
        ctx["tagcloud"] = get_tagcloud(ctx["articles"])
    path = os.path.abspath(path)
    tpl = Template(filename="_templates/"+template+'.mako',
                   lookup=_lookup)
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    to = open(path, 'w')
    try:
        to.write(tpl.render(**ctx))
    except:
        print exceptions.text_error_template().render()
        exit()
    to.close()


def get_tagcloud(articles, offset=1):
    """"""
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

