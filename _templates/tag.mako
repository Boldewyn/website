# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa
%>
<%inherit file="base.mako"/>

<section id="content" class="tag">
  <h1>${_(u"Tag “%s”") % tag}</h1>

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
${_(u"Tag “%s”") % tag} — \
</%def>

<%def name="head()">
  <link rel="alternate" type="application/atom+xml" title="${_("Feed for tag %s") % tag}" href="${laa(lang, "tag/%s/feed.xml" % tag)}" />
</%def>
