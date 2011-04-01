# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa, aa, repl, strip_tags
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
          <a rel="prev" href="${laa(lang, article.headers.Requires.url)}">${_("Previous:")} ${article.headers.Requires.headers.title | n}</a>
        </p>
      % endif

      % if "IsRequiredBy" in article.headers and type(article) == type(article.headers.IsRequiredBy):
        <p class="is-required-by">
          <a rel="next" href="${laa(lang, article.headers.IsRequiredBy.url)}">${_("Next:")} ${article.headers.IsRequiredBy.headers.title | n}</a>
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
  <link rel="canonical" href="${aa(article.url)}" />
  <link rel="dc.isPartOf" href="${laa(lang, article.category+"/")}" />
  <link rel="dc.tableOfContents" href="${laa(lang, article.category+"/")}" />
  <meta name="description" content="${article.headers.description}" />
  <meta name="keywords" content="${",".join(article.headers.subject)}" />
  % if article.headers.robots:
    <meta name="robots" content="${article.headers.robots}" />
  % else:
    <meta name="robots" content="index, follow" />
  % endif
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
