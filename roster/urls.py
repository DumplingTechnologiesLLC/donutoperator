from django.conf.urls import url
from roster import views
app_name = "roster"

urlpatterns = [
    url(r'^submit-killing$', views.SubmitShootingView.as_view(), name="submit-killing"),
    url(r'^delete-killing$', views.DeleteShootingView.as_view(), name="delete-killing"),
    url(r'^edit-killing$', views.EditShootingView.as_view(), name="edit-killing"),
    url(r'^(?P<date>[0-9]+)$', views.RosterListView.as_view(), name="date-index"),
    url(r'^$', views.RosterListView.as_view(), name="index"),
]
