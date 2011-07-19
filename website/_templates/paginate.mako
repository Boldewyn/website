# -*- coding: utf-8 -*-
<%!
from website._webtools.templatedefs import laa
%>\
<%def name="paginate(ctx)">\
<%
  plen = settings.PAGINATION_DISPLAY_LENGTH or 4
  need_ellipsis = True
%>\
% if ctx and ctx["pages"]:
<%
def phref(p):
    if p == 1:
        if "%s" in ctx["first"]:
            r = ctx["first"] % 1
        r = ctx["first"]
        if r.endswith(".html"):
          r = r[:-5]
        return r
    else:
        return ctx["base"] % p
%>\
<ol class="paginate">\
% if ctx["cur"] == 1:
<li class="current start"><span data-href="${laa(lang, phref(1))}">${_(u"Start")}</span></li>\
% else:
<li class="start"><a href="${laa(lang, phref(1))}">${_(u"Start")}</a></li>\
% endif
% for p in range(1, ctx["pages"]+1):
% if p > 1+plen and p < ctx['pages']-plen and p not in range(ctx['cur']-plen, ctx['cur']+1+plen):
% if need_ellipsis:
<%
  need_ellipsis = False
%>\
<li class="ellipsis">…</li>\
% endif
<%
  continue
%>\
% endif
% if ctx["cur"] == p:
<li class="current"><span data-href="${laa(lang, phref(p))}">${str(p)}</span></li>\
% else:
<li><a href="${laa(lang, phref(p))}">${str(p)}</a></li>\
% endif
<%
  need_ellipsis = True
%>\
% endfor
% if ctx["cur"] == ctx["pages"]:
<li class="current end"><span data-href="${laa(lang, ctx["base"] % ctx["pages"])}">${_(u"End")}</span></li>\
% else:
<li class="end"><a href="${laa(lang, ctx["base"] % ctx["pages"])}">${_(u"End")}</a></li>\
% endif
</ol>\
% endif
</%def>\
