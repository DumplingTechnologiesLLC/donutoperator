from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# from django.db import models
# from tinymce import HTMLField


image_storage = FileSystemStorage(
    # Physical file location ROOT
    location=u'{0}/uploads/'.format(settings.MEDIA_ROOT),
    # Url for file
    base_url=u'{0}uploads/'.format(settings.MEDIA_URL),
)


def image_directory_path(instance, filename):
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
    cover_image = models.ImageField(
        default='DonutsDonut.png', upload_to=image_directory_path, storage=image_storage)
    views = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
