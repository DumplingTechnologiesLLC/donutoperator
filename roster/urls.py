from django.conf.urls import url, include
from roster import views
app_name = "roster"

urlpatterns = [
    url("api/", include([
        url("killings", views.ShootingsAPI.as_view(), name="api-shootings"),
        url("tags", views.TagsAPI.as_view(), name="api-tags"),
    ])),
    url(
    	r'^ajax/ajax-shootings$',
    	views.AjaxSelect2Shootings.as_view(),
    	name="ajax-shootings"
    ),
    url(r'^tip$', views.TipPage.as_view(), name="tip-page"),
    url(r'^feedback$', views.FeedbackPage.as_view(), name="feedback-page"),
    url(r'^tips$', views.TipList.as_view(), name="tip-list"),
    url(r'^ajax/submit-killing$',
        views.SubmitShootingView.as_view(), name="submit-killing"),
    url(r'^ajax/delete-killing$',
        views.DeleteShootingView.as_view(), name="delete-killing"),
    url(r'^ajax/edit-killing$',
        views.EditShootingView.as_view(), name="edit-killing"),
    url(r'^ajax/shootings$', views.RosterListData.as_view(), name="shooting-data"),
    url(r'^(?P<date>[0-9]+)$', views.RosterListView.as_view(), name="date-index"),
    url(r'^$', views.RosterListView.as_view(), name="index"),
]
