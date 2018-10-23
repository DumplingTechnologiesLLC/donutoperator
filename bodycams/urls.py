from django.conf.urls import url
from blog.views import *
from filebrowser.sites import site
site.directory = "uploads/"

app_name = "bodycams"

urlpatterns = [
]
