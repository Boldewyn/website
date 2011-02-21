# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa, date, get_cat_title
%>\
<%page args="_, lang, article, title=True" />\

  % if title:
    <h1>${article.headers.title | n}</h1>
    % if article.headers.subtitle:
      <h2>${article.headers.subtitle | n}</h2>
    % endif
  % endif
  % if "no-info" not in article.headers.status:
    <section class="info">
      <p class="info-date">
        <time pubdate="pubdate" datetime="${article.headers.date.isoformat("T")}">${date(article.headers.date, lang)}</time>
      </p>
      <address class="info-author \
        % if article.headers.author == settings.DEFAULTS["AUTHOR"]:
          default-author\
        % endif
      ">${_("by %s") % _(article.headers.author)}</address>
      % if article.category:
        <p class="info-category"><a href="${article.category | aa}">${_("Filed under %s") % get_cat_title(_, article.category)}</a></p>
      % endif
      % if len(article.headers.subject) > 0:
        <p class="info-subject">${_("Keywords:")}
          % for i, tag in enumerate(article.headers.subject):
            <a href="${("tag/%s" % tag) | aa}" rel="tag">${tag}</a>\
            % if i < len(article.headers.subject) - 1:
, \
            % endif
          % endfor
        </p>
      % endif
    </section>
  % endif

  % if article.headers.abstract:
    <section class="abstract">
      <p>${article.headers.abstract}</p>
    </section>
  % endif

