# -*- coding: utf-8 -*-
<%inherit file="base.mako"/>\
\
<section id="content">\
<h1>${_(u"Another Blog Around")}</h1>\
<h2>${_(u"Latest Articles:")}</h2>\
<%namespace name="article_list" file="article_list.mako" />\
${article_list.list(a, "front_latest archive")}\
<%namespace name="page" file="paginate.mako" />\
${page.paginate(pag)}\
</section>\
