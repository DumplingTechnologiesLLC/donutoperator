from django.contrib.sitemaps import Sitemap
from videos.models import Video


class VideoSitemap(Sitemap):

    def items(self):
        return Video.objects.all().order_by("-date")

    def lastmod(self, obj):
        return obj.created

    def changefreq(self, obj):
        return "never"
