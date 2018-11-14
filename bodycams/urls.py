from django.conf.urls import url
from bodycams.views import *
from filebrowser.sites import site
site.directory = "uploads/"

app_name = "bodycams"

urlpatterns = [
	url(r'^bodycams$', BodycamIndexView.as_view(), name="bodycams"),
	url(r'^bodycams/dashboard$', BodycamDashboard.as_view(), name="dashboard"),
	url(r'^bodycams/dashboard/(?P<date>[0-9]+)$', BodycamDashboard.as_view(), name="dashboard-date"),
	url(r'^bodycams/(?P<date>[0-9]+)$', BodycamIndexView.as_view(), name="date-index"),
	url(r'^ajax/bodycam/submit$', BodycamSubmit.as_view(), name="bodycam-submit"),
	url(r'^ajax/bodycam/edit$', BodycamEdit.as_view(), name="bodycam-edit"),
	url(r'^ajax/bodycam/link$', BodycamLink.as_view(), name="link-bodycam-shooting"),
]
