"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
# from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from config.sitemaps import KillingsSitemap, BodycamSitemap
from filebrowser.sites import site as filebrowser_site
from rest_framework.documentation import include_docs_urls
from config.views import *

sitemaps = {
    'killings': KillingsSitemap,
    'bodycams': BodycamSitemap
}


urlpatterns = [
    re_path(r'^admin/filebrowser/', filebrowser_site.urls),
    re_path(r'^sitemap\.xml$', sitemap, {
            'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^e1da49db34b0bdfdddaba2ad6552f848/$', sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^robots\.txt', include('robots.urls')),
    re_path(r'^api/documentation', APIList.as_view(),
            name="api-documentation"),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^docs/', include_docs_urls(title='PKBP API')),
    re_path(r'^about/$', AboutPage.as_view(), name="about-page"),
    re_path(r'^changelog/$', ChangeLog.as_view(), name="changelog"),
    re_path(r'^login/$', login, name='login'),
    re_path(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path("^grappelli/", include("grappelli.urls")),
    re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'', include('roster.urls')),
    re_path(r'', include('blog.urls')),
    re_path(r'', include('bodycams.urls')),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
