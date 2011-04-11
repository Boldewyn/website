# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa, aa, static
%>\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="${lang or 'en'}" lang="${lang or 'en'}">
  <head>
    <meta charset="UTF-8" />
    <!--[if lt IE 9]>
      <script src="${'html5.js' | static}"></script>
    <![endif]-->
    <link rel="stylesheet" href="${'style.css' | static}" />
    <link rel="alternate" type="application/atom+xml" href="${"feed.xml" | aa}" />
    <link rel="profile" href="http://www.w3.org/2003/g/data-view" />
    <link rel="schema.dc" href="http://purl.org/dc/terms/" />
    <link rel="transformation" href="http://dublincore.org/transform/dc-html-20080804-grddl/dc-html2rdfxml.xsl" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <script src="${'script.js' | static}"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    ${self.head()}
    <title>${self.get_title()}</title>
  </head>
  <body>
    ${self.header()}
    <div id="body">
      ${self.body()}
      ${self.aside()}
    </div>
    ${self.footer()}
    ${self.foot()}
  </body>
</html>
\
<%def name="head()"/>\
<%def name="foot()"/>\
\
<%def name="get_title()"/>\
\
<%def name="category_title(category)">
  <%
    try:
      title = _(settings.CATEGORY[category]["title"])
    except:
      title = category
  %>
  ${title}
</%def>\
\
<%def name="header()">
  <header>
    <nav>
      <ul>
        <li class="home"><a href="${settings.URL}" rel="home">${_(u"Home")}</a></li>
        % if categories:
          % for category in categories:
            <li><a href="${laa(lang, category+"/")}">${self.category_title(category)}</a></li>
          % endfor
        % endif
      </ul>
    </nav>
  </header>
</%def>\
\
<%def name="footer()">
  <footer>
  </footer>
</%def>\
\
<%def name="aside()">
  <aside>
    % if tagcloud:
      <div class="tagcloud">
        <h2>${_(u"Tags")}</h2>
        <p>
          % for tag, t, n in tagcloud:
            <a class="tc_${str(t)}" rel="tag" href="${laa(lang, "tag/%s/" % tag)}">${tag} <span class="tc_info">${str(n)}</span></a>
          % endfor
        </p>
      </div>
    % endif
    % if archives:
      <div class="archives">
        <h2>${_(u"Archive")}</h2>
        <ul>
          % for d in archives:
            <li><a href="${laa(lang, '/archive/%s/' % d)}">${d}</a></li>
          % endfor
        </ul>
      </div>
    % endif
    % if latest_articles and len(latest_articles):
      <div class="latest">
        <h2>${_(u"Latest Articles")}</h2>
        <ul>
          % for art in latest_articles:
            <li><a href="${laa(lang, art.url)}">${art.headers.title | n}</a></li>
          % endfor
        </ul>
      </div>
    % endif
  </aside>
</%def>\
