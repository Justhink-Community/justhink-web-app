from django.contrib.sitemaps import Sitemap 
from django.shortcuts import reverse 

class StaticViewSiteMap(Sitemap):
    def items(self):
        return ['index-page', 'ideas-page', 'trend-ideas-page', 'favourite-ideas-page']
    def location(self, item):
        return reverse(item)