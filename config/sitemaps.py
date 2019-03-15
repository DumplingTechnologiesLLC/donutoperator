from django.contrib.sitemaps import Sitemap
from roster.models import Shooting
from bodycams.models import Bodycam


class KillingsSitemap(Sitemap):

    def items(self):
        return Shooting.objects.all().order_by("-date")

    def lastmod(self, obj):
        return obj.created

    def changefreq(self, obj):
        return "never"


class BodycamSitemap(Sitemap):

    def items(self):
        return Bodycam.objects.all().order_by("-date")

    def lastmod(self, obj):
        return obj.created

    def changefreq(self, obj):
        return "never"
