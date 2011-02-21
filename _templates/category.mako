# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa
%>\
<%inherit file="base.mako"/>

<section id="content" class="category">
  <h1>${self.category_title(category)}</h1>

  % if description:
    <section class="description">
      ${description | n}
    </section>
  % endif

  <%namespace name="article_list" file="article_list.mako" />
  ${article_list.list(a)}

  <%namespace name="page" file="paginate.mako" />
  ${page.paginate(pag)}

</section>

<%def name="get_title()">\
${_(u"Category “%s”") % category} — \
</%def>

<%def name="head()">
  <link rel="alternate" type="application/atom+xml" title="${_("Feed for category %s") % category}" href="${("%s/feed.xml" % category) | aa}" />
</%def>
