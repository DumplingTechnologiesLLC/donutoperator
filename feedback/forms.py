from captcha.fields import CaptchaField
from django import forms
from .models import Feedback


class FeedbackModelForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Feedback
        fields = "__all__"
