from django import forms
from tinymce import TinyMCE
from .models import Post


class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False}
        ),
        help_text="If you want to have insert a block quote, surround the text in triple backticks like so: ```quote text```"
    )
    cover_image = forms.ImageField(
        required=False,
        help_text="It is strongly recommended that you choose an image with dimensions 200px x 250px")

    authors = forms.CharField(initial="Donutoperator")

    class Meta:
        model = Post
        fields = [
            "title",
            "authors",
            "description",
            "read_length",
            "content",
            "cover_image",
        ]
        help_texts = {
            "read_length": "How long a read is this? We recommend you use this format: [number] min read",
            "cover_image": "It is strongly recommended that you choose an image with a max height of 200"
        }
        # fields = '__all__'
