from django import forms
from bodycams.models import Bodycam
import re


class BodycamModelForm(forms.ModelForm):

    class Meta:
        model = Bodycam
        fields = [
            "title",
            "video",
            "description",
            "department",
            "state",
            "city",
            "date",
        ]

    def clean_video(self):
        """Cleans the video submitted for a bodycam

        Expects: a stringified iframe embed code

        Logic:
                - Checks to see if the code is an iframe
                        if no - returns ValidationError
                - Replaces the default width and height provided by the source with 100%
                - Checks if width or height not provided, and concatenates them to the
                	header
                - returns video

        Returns:
        formatted video
        """
        video = self.cleaned_data['video']
        if "iframe" not in video:
            raise forms.ValidationError("The video input MUST be an embed code")
        else:
            video = re.sub('width=\"[0-9]+\"', 'width="100%"', video)
            video = re.sub('height=\"[0-9]+\"', 'height="100%"', video)
            if "width=" not in video and "width:" not in video:
                # width not specified, which shouldn't happen but lets handle it
                pre_portion = "<iframe"
                video_portion = video[7:]  # the portion after the iframe tag
                video = pre_portion + " width='100%' " + video_portion
            if "height=" not in video and "height:" not in video:
                # height not specified, which shouldn't happen but lets handle it
                pre_portion = "<iframe"
                video_portion = video[7:]  # the portion after the iframe tag
                video = pre_portion + " height='100%' " + video_portion
            return video
