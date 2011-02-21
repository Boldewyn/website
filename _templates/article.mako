# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa, repl, strip_tags
%>\
<%inherit file="base.mako" />

<article id="content" \
  % if lang != article.headers.language:
    xml:lang="${article.headers.language}"\
  % endif
>

  <%include file="article/head.mako" args="_=_, lang=lang, article=article" />

  <section class="body">
    ${content | n}
  </section>

  % if ("IsRequiredBy" in article.headers and type(article) == type(article.headers.IsRequiredBy)) or \
       ("Requires" in article.headers and type(article) == type(article.headers.Requires)):
    <section class="related-links">
      % if "Requires" in article.headers and type(article) == type(article.headers.Requires):
        <p class="requires">
          <a rel="prev" href="${article.headers.Requires.live_path}">${_("Previous:")} ${article.headers.Requires.headers.title | n}</a>
        </p>
      % endif

      % if "IsRequiredBy" in article.headers and type(article) == type(article.headers.IsRequiredBy):
        <p class="is-required-by">
          <a rel="next" href="${article.headers.IsRequiredBy.live_path}">${_("Next:")} ${article.headers.IsRequiredBy.headers.title | n}</a>
        </p>
      % endif
    </section>
  % endif

  <%include file="article/foot.mako" args="_=_, lang=lang, article=article" />

</article>

<%def name="get_title()">\
${article.headers.title | n,strip_tags} — \
</%def>

<%def name="head()">
  ${parent.head()}
  <link rel="canonical" href="${article.live_path | aa}" />
  <link rel="dc.isPartOf" href="${article.category | aa}" />
  <link rel="dc.tableOfContents" href="${article.category | aa}" />
  % for k, v in article.headers.get_dc().iteritems():
    % if v.startswith("http"):
      <link rel="dc.${k}" href="${v | repl}" />
    % else:
      <meta name="dc.${k}" content="${_(v)}" />
    % endif
  % endfor
  % for css in article.headers.stylesheet:
    <link rel="stylesheet" href="${css | repl}" />
  % endfor
  % for js in article.headers.script:
    <script src="${js | repl}"></script>
  % endfor
</%def>
