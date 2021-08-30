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
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sitemaps.views import sitemap
from config.sitemaps import VideoSitemap
from config.views import *

sitemaps = {
    'videos': VideoSitemap,
}


urlpatterns = [
    re_path(r'^sitemap\.xml$', sitemap, {
            'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^e1da49db34b0bdfdddaba2ad6552f848/$', sitemap, {'sitemaps': sitemaps},
            name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^robots\.txt', include('robots.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^about/$', AboutPage.as_view(), name="about-page"),
    re_path(r'^login/$', LoginView.as_view(), name='login'),
    re_path(r'^logout/$', LogoutView.as_view(),
            {'next_page': '/'}, name='logout'),
    re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'', include('videos.urls')),
    re_path(r'', include('feedback.urls')),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
