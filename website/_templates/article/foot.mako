# -*- coding: utf-8 -*-
<%!
from website._webtools.templatedefs import aa, jsq, strip_tags
%>\
<%page args="_, lang, article" />\
\
% if "no-discussion" not in article.headers.status and "DISQUS_NAME" in settings:
<section class="discussion">\
<div id="disqus_thread"></div>\
<script>
var disqus_shortname='${settings.DISQUS_NAME}',\
disqus_identifier="${aa(article.url) | jsq}",\
disqus_title="${article.headers.title | n,strip_tags,jsq}";\
% if settings.DEBUG:
var disqus_developer=1;\
% endif
(function(d) {\
var a;\
if(d.cookie.search(/nodisq=1/)===-1){\
a=d.createElement('script');a.type='text/javascript';a.async=true;\
a.src='http://'+disqus_shortname+'.disqus.com/embed.js';\
(d.getElementsByTagName('head')[0]||d.getElementsByTagName('body')[0]).appendChild(a);\
}else{\
a=d.createElement('a');a.setAttribute('href','#');a.onclick=function(){\
d.cookie='nodisq=0; path=/';location.reload();};\
a.appendChild(d.createTextNode("${_(u'Discussion disabled due to privacy settings. Click here to re-enable.')}"));\
d.getElementById("disqus_thread").appendChild(a);\
}\
})(document);
</script>\
<p class="dsq-brlink">\
<a href="http://${settings.DISQUS_NAME}.disqus.com" class="dsq-brlink">${_(u"Blog comments powered by %s") % '<span class="logo-disqus">Disqus</span>' | n}</a>\
</p>\
</section>\
% endif
