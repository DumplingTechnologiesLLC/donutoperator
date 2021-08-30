from django.db import models
from django.utils import timezone


class Feedback(models.Model):
    text = models.TextField("Tip", max_length=4000)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(Feedback, self).save(*args, **kwargs)

    def __str__(self):
        text = self.text
        if len(self.text) > 20:
            text = text[0:20] + "..."
        return "{} {}".format(self.created.strftime("%Y-%m-%d"), text)
