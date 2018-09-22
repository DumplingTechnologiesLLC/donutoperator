from django.conf.urls import url
from roster import views
app_name = "roster"

urlpatterns = [
	url(r'^submit-killing$', views.SubmitShootingView.as_view(), name="submit-killing"),
    url(r'^$', views.RosterListView.as_view(), name="index"),
]
