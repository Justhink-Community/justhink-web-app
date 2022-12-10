from django.contrib.sitemaps import Sitemap 
from django.shortcuts import reverse 

class StaticViewSiteMap(Sitemap):
    def items(self):
        return ['index-page', 'ideas-page', 'random-ideas-page',  'home', 'about-us-page']
    def location(self, item):
        return reverse(item)