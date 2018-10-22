from django import forms
from tinymce import TinyMCE
from .models import Post
from django.utils.safestring import mark_safe

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
        help_text=mark_safe(("If you want to quote someone, surround the text in triple "
            "backticks like so: ```quote text``` and give one empty line above and below"
            " the text. <br><br>If you have a block quote, enter an empty line, then"
            " type 3 backticks, then start a new line, insert the paragraph, then at the"
            " end of the paragraph hit enter, type 3 more backticks (so they are on"
            " their own line) and then give one line of empty space before continuing"
            " with the article<br><br><strong>Example:</strong><br>Before quote text"
            "<br><br>```<br>line 1<br>line 2<br> line 3<br>```<br><br>After quote text"))
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
