from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User
# from django.forms.models import model_to_dict
# from django.db import models
# from tinymce import HTMLField


image_storage = FileSystemStorage(
    # Physical file location ROOT
    location=u'{0}/uploads/'.format(settings.MEDIA_ROOT),
    # Url for file
    base_url=u'{0}uploads/'.format(settings.MEDIA_URL),
)


def image_directory_path(instance, filename):  # pragma: no cover
    # file will be uploaded to MEDIA_ROOT/my_sell/picture/<filename>
    return u'picture/{0}'.format(filename)


class Post(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=250, null=True)
    read_length = models.CharField("Article Length", max_length=20)
    content = HTMLField('Content')
    published = models.BooleanField("Published", default=False)
    created = models.DateTimeField("Creation Date", editable=False)
    publish_date = models.DateTimeField("Publish Date", null=True, blank=True)
    modified = models.DateTimeField("Last Modified", editable=False)
    authors = models.CharField("Authors", max_length=100, default="Donutoperator")
    cover_image = models.ImageField(default='DonutsDonut.png',)
    views = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class AWSImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        related_name="images",
        null=True,
        blank=True,
    )
    image = models.ImageField()
    unassigned = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="images",
        blank=True,
        null=True
    )

    def as_dict(self):
        return {
            "image": self.image.url,
            "id": self.id
        }


@receiver(models.signals.post_delete, sender=AWSImage)
def remove_file_from_s3(sender, instance, using, **kwargs):
    """Post Delete receiver to delete the file from Amazon S3
    """
    instance.image.delete(save=False)
