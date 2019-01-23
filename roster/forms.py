from django import forms
from roster.models import Shooting, Tip
from captcha.fields import CaptchaField


def convert_format(url):
    url = url.split("?")[1][2:]
    pre_format = '<iframe width="100%" height="315" src="https://www.youtube.com/embed/'
    post_format = ('" frameborder="0" allow="autoplay; encrypted-'
                   'media" allowfullscreen></iframe>')
    return pre_format + url + post_format


class TipModelForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Tip
        fields = "__all__"


class ShootingModelForm(forms.ModelForm):
    class Meta:
        model = Shooting
        fields = [
            'state', 'city', 'description', 'video_url',
            'name', 'age', 'race', 'gender', 'date',
        ]

    def clean_name(self):
        """
        Cleans the name input.

        If the name is blank, sets the name to "No Name"

        returns cleaned name
        """
        data = self.cleaned_data['name']
        if data is None:
            data = ""
        if len(data) == 0:
            return "No Name"
        return data

    def clean_city(self):
        """
        Cleans the city input

        If the city is blank, sets the city to "Unknown"

        returns cleaned city
        """
        data = self.cleaned_data["city"]
        if data is None:
            data = ""
        if len(data) == 0:
            return "Unknown"
        return data

    def clean_video_url(self):
        """
        Cleans the video_url

        if data is None, sets to "", if data.length > 0 and it doesn't have a "?",
        raises a validation error. Otherwise calls convert_format on the data

        returns cleaned video_url
        """
        data = self.cleaned_data.get("video_url", "")
        if data is None:
            data = ""
        if len(data) > 0:
            if data.find("?") < 0 and len(data) > 0:
                raise forms.ValidationError("Please provide a valid video URL")
            return convert_format(data)
        return data
