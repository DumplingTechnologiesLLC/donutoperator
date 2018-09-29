from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField


class Blog(models.Model):
    published = models.BooleanField("Published", default=False)
    created = models.DateTimeField("Publish Date", editable=False)
    modified = models.DateTimeField()
    content = HTMLField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Blog, self).save(*args, **kwargs)
