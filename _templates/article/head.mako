# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa, date, get_cat_title
%>\
<%page args="_, lang, article, title=True" />\

  % if title:
    <h1 class="entry-title">${article.headers.title | n}</h1>
    % if article.headers.subtitle:
      <h2>${article.headers.subtitle | n}</h2>
    % endif
  % endif
  % if "no-info" not in article.headers.status:
    <section class="info">
      <p class="info-date">
        <time class="updated" pubdate="pubdate" datetime="${article.headers.date.isoformat("T")}">${date(article.headers.date, lang)}</time>
      </p>
      <address class="author vcard \
        % if article.headers.author == settings.DEFAULTS["AUTHOR"]:
          default-author\
        % endif
      ">${_("by %s") % '<span class="fn">'+_(article.headers.author)+'</span>' | n}</address>
      % if article.category:
        <p class="info-category">${_("Filed under %s") % '<a href="%s" rel="tag">%s</a>' % (laa(lang, article.category+"/"), get_cat_title(_, article.category)) | n}</p>
      % endif
      % if len(article.headers.subject) > 0:
        <p class="info-subject">${_("Keywords:")}
          % for i, tag in enumerate(article.headers.subject):
            <a href="${laa(lang, "tag/%s/" % tag)}" rel="tag">${tag}</a>\
            % if i < len(article.headers.subject) - 1:
, \
            % endif
          % endfor
        </p>
      % endif
    </section>
  % endif

  % if article.headers.abstract:
    <section class="abstract entry-summary">
      <p>${article.headers.abstract}</p>
    </section>
  % endif

