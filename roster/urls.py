from django.conf.urls import url
from roster import views
app_name = "roster"

urlpatterns = [
    url(r'^$', RosterListView.as_view(), name="index"),
]
