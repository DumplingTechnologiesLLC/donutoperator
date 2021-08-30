from django.urls import re_path
from .views import FeedbackPage
app_name = 'feedback'
urlpatterns = [
    re_path(r'^feedback$', FeedbackPage.as_view(), name="feedback-page"),
]
