from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.sitemaps import ping_google
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class Video(models.Model):
    STATE_CHOICES = (
        (0, "AL"),
        (1, "AK"),
        (2, "AZ"),
        (3, "AR"),
        (4, "CA"),
        (5, "CO"),
        (6, "CT"),
        (7, "DE"),
        (8, "FL"),
        (9, "GA"),
        (10, "HI"),
        (11, "ID"),
        (12, "IL"),
        (13, "IN"),
        (14, "IA"),
        (15, "KS"),
        (16, "KY"),
        (17, "LA"),
        (18, "ME"),
        (19, "MD"),
        (20, "MA"),
        (21, "MI"),
        (22, "MN"),
        (23, "MS"),
        (24, "MO"),
        (25, "MT"),
        (26, "NE"),
        (27, "NV"),
        (28, "NH"),
        (29, "NJ"),
        (30, "NM"),
        (31, "NY"),
        (32, "NC"),
        (33, "ND"),
        (34, "OH"),
        (35, "OK"),
        (36, "OR"),
        (37, "PA"),
        (38, "RI"),
        (39, "SC"),
        (40, "SD"),
        (41, "TN"),
        (42, "TX"),
        (43, "UT"),
        (44, "VT"),
        (45, "VA"),
        (46, "WA"),
        (47, "WV"),
        (48, "WI"),
        (49, "WY"),
        (50, "DC"),
        (51, "PR"),
        (52, "GU"),
    )
    title = models.CharField(max_length=120)
    video = models.CharField(max_length=100000)
    description = models.CharField(
        "Description",
        max_length=10000,
        blank=True,
        null=True
    )
    state = models.IntegerField("State", choices=STATE_CHOICES)
    city = models.CharField("City", max_length=256, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    specially_exempted_users = models.ManyToManyField(
        User,
        related_name="exempted_videos"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="videos",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        "Creation Date", editable=False, null=True, blank=True)

    def get_absolute_url(self):
        return self.video

    def save(self, *args, **kwargs):  # pragma: no cover
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        try:
            ping_google()
        except Exception:
            pass
        return super(Video, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    text = models.CharField("Text", max_length=1000)
    videos = models.ManyToManyField(Video, related_name="tags")

    def __str__(self):
        return self.text
