from django import forms
from roster.models import Shooting


class ShootingModelForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Shooting
        fields = [
        	'state', 'city', 'description', 'video_url',
        	'name', 'age', 'race', 'gender', 'date',
        ]