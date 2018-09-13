from django.conf.urls import url
from roster import views
app_name = "roster"

urlpatterns = [
    url(r'^$', views.RosterListView.as_view(), name="index"),
]
