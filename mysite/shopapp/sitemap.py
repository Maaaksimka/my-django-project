from django.contrib.sitemaps import Sitemap

from .models import Products

class ShopSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Products.objects.filter(created_at__isnull=False).order_by("-created_at")

    def lastmod(self, obj: Products):
        return obj.created_at