from django.conf.urls import url
from roster import views
app_name = "roster"

urlpatterns = [
	url(r'^ajax/ajax-shootings$', views.AjaxSelect2Shootings.as_view(), name="ajax-shootings"),
    url(r'^ajax/submit-killing$',
    	views.SubmitShootingView.as_view(), name="submit-killing"),
    url(r'^ajax/delete-killing$',
    	views.DeleteShootingView.as_view(), name="delete-killing"),
    url(r'^ajax/edit-killing$',
    	views.EditShootingView.as_view(), name="edit-killing"),
    url(r'^(?P<date>[0-9]+)$', views.RosterListView.as_view(), name="date-index"),
    url(r'^$', views.RosterListView.as_view(), name="index"),
]
