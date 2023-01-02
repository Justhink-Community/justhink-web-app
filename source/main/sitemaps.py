from django.contrib.sitemaps import Sitemap 
from django.shortcuts import reverse 
from user_profile.models import Profile

class StaticViewSiteMap(Sitemap):
    def items(self):
        return ['index-page', 'ideas-page', 'random-ideas-page',  'home', 'about-us-page']
    def location(self, item):
        return reverse(item)

class ProfileSiteMap(Sitemap):
    changefreq = 'hourly'
    priority = 0.9

    def items(self):
        return Profile.objects.all()