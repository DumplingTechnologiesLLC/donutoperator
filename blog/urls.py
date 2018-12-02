from django.conf.urls import url
from blog.views import *
from filebrowser.sites import site
site.directory = "uploads/"

app_name = "blog"

urlpatterns = [
    url(r'^news/$', PostIndexView.as_view(), name="blog-index"),
    url(r'^post/(?P<pk>\d+)/edit$', PostEditView.as_view(), name='edit'),
    url(r'^post/(?P<pk>\d+)/$', PostDisplayView.as_view(), name='display'),
    url(r'^create-news-story/$', PostCreateView.as_view(), name='create'),
    url(r'^news-dashboard/$', PostDashboard.as_view(), name='dashboard'),
    url(r'^image/delete/$', PostImageDeleteView.as_view(), name="image-delete"),
    url(r'^image/create/$', PostImageCreateView.as_view(), name="image-create"),
]
