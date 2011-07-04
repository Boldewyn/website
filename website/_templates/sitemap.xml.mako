<%!
from _webtools.templatedefs import aa
%>\
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${local_sitemap | n}\
  % for url in sitemap:
    <url>
      <loc>${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(url[0])}</loc>
      <lastmod>${url[1].strftime("%Y-%m-%d")}</lastmod>
      <changefreq>${url[2]}</changefreq>
      <priority>${unicode(url[3])}</priority>
    </url>
  % endfor
</urlset>

