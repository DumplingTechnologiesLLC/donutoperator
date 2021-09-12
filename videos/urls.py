from django.conf.urls import url, include
from rest_framework import routers
from .views import *

app_name = "videos"
router = routers.SimpleRouter()
router.register(r'api/videos/admin', EditorVideoViewSet, basename="videos")
router.register(r'api/videos', VideoViewSet, basename="videos-readonly")
# router.register(r'accounts', AccountViewSet)

urlpatterns = [
    # url("api/", include([
    #     url("bodycams", BodycamsAPI.as_view(), name="api-bodycams"),
    # ])),
    url(r'^$', VideoIndexView.as_view(), name="index"),
    url(r'^(?P<date>[0-9]+)$', VideoIndexView.as_view(), name="date-index"),
    # url(r'^/dashboard$', VideoDashboard.as_view(), name="dashboard"),
    # url(r'^/dashboard/(?P<date>[0-9]+)$',
    #     VideoDashboard.as_view(), name="dashboard-date"),
    # url(r'^ajax/', include([
    #     url(r'^bodycams/json$', BodycamData.as_view(), name="bodycam-data"),
    #     url(r'^bodycam/submit$', BodycamSubmit.as_view(), name="bodycam-submit"),
    #     url(r'^bodycam/edit$', BodycamEdit.as_view(), name="bodycam-edit"),
    #     url(r'^bodycam/link$', BodycamLink.as_view(), name="link-bodycam-shooting"),
    # ]))
] + router.urls
