from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.sitemaps import ping_google
# Create your models here.


class Bodycam(models.Model):
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
    department = models.CharField(max_length=200, blank=True, null=True)
    state = models.IntegerField("State", choices=STATE_CHOICES)
    city = models.CharField("City", max_length=256, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    shooting = models.ForeignKey(
        'roster.Shooting',
        related_name='bodycams',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        "Creation Date", editable=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('bodycams:bodycam-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):  # pragma: no cover
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        try:
            ping_google()
        except Exception:
            pass
        return super(Bodycam, self).save(*args, **kwargs)

    def as_dict(self):
        """
        Serializes the bodycam into a JSON object

        if there is no shooting attached, it attaches a false shooting object with
        id -1 and name "No shooting record attached to this bodycam yet" for display
        purposes

        Provides state display string as state, and state numerical value as state_value

        returns serialized object
        """
        tags = self.tags.all()
        tags = [obj.as_dict() for obj in tags]
        if self.shooting:
            shooting = self.shooting.as_dict()
        else:
            shooting = {
                'id': -1,
                'name': 'No shooting record attached to this bodycam yet',
                'age': "",
                'date': '',
                'race': '',
                'race_value': "",
                'gender': '',
                'gender_value': 0,
                'state': '',
                'state_value': "",
                'city': '',
                'video_url': 'None',
                'unfiltered_video_url': 'None',
                'description': '',
                'tags': [],
                'sources': []
            }
        return {
            "id": self.id,
            "title": self.title,
            "video": self.video,
            "description": self.description if self.description is not None else "",
            "department": self.department if self.department is not None else "Unknown",
            "state": self.get_state_display(),
            "state_value": self.state,
            "city": self.city if self.city is not None else "Unknown",
            "date": self.date.strftime("%Y-%m-%d"),
            "shooting": shooting,
            "tags": tags,
        }

    def __str__(self):
        return self.title
