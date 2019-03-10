from django.db import models
from bodycams.models import Bodycam
from django.utils import timezone


class Shooting(models.Model):
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
    GENDER_CHOICES = (
        (0, "Male"),
        (1, "Female"),
        (2, "Unknown")
    )
    RACE_CHOICES = (
        (0, "Native American"),
        (1, "Asian"),
        (2, "Black"),
        (3, "Native Hawaiian or Other Pacific Islander"),
        (4, "White"),
        (5, "Hispanic/Latino"),
        (6, "None Given"),
        (7, "Other"),
    )
    has_bodycam = models.BooleanField("Has Bodycam", default=False)
    state = models.IntegerField("State", choices=STATE_CHOICES)
    city = models.CharField("City", max_length=256, blank=True, null=True)
    description = models.CharField(
        "Description",
        max_length=10000,
        blank=True,
        null=True
    )
    video_url = models.CharField(
        "Video",
        max_length=1000,
        blank=True,
        null=True
    )
    unfiltered_video_url = models.CharField(
        "Unfiltered Video Url",
        max_length=1000,
        blank=True,
        null=True
    )
    name = models.CharField(
        "Name",
        max_length=256,
        blank=True,
        null=True
    )
    age = models.IntegerField("Age", blank=True, null=True)
    race = models.IntegerField("Race", choices=RACE_CHOICES)
    gender = models.IntegerField("Gender", choices=GENDER_CHOICES)
    date = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(
        "Creation Date", editable=False, null=True, blank=True)

    def bodycam(self):  # pragma: no cover
        try:
            if self.bodycams.all().first() is not None:
                return self.bodycams.all().first()
            else:
                return False
        except:
            return False

    def save(self, *args, **kwargs):  # pragma: no cover
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(Shooting, self).save(*args, **kwargs)

    def as_dict(self):
        """
        Serializes the shooting into JSON form.

        Formats the date to YYYY-MM-DD

        for race, gender and state, it provides the display as
        race, gender and state, and the numerical value as
        race_value, gender_value, state_value

        returns serialized object
        """
        tags = self.tags.all()
        tags = [obj.as_dict() for obj in tags]
        sources = self.sources.all()
        sources = [obj.as_dict()["text"] for obj in sources]
        date = ""
        bodycam_video = "None"
        if self.has_bodycam and type(self.bodycam()) is not bool:
            bodycam_video = self.bodycam().video
        if isinstance(self.date, str):
            date = self.date
        else:  # pragma: no cover
            date = self.date.strftime("%Y-%m-%d")
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age if self.age is not None and self.age > -1 else "No Age",
            "date": date,
            "race": self.get_race_display(),
            "race_value": self.race,
            "gender": self.get_gender_display(),
            "gender_value": self.gender,
            "state": self.get_state_display(),
            "state_value": self.state,
            "city": self.city if self.city is not None and self.city != "" else "Unknown",
            "video_url": self.video_url if self.video_url is not None and self.video_url != "" else "None",
            "unfiltered_video_url": self.unfiltered_video_url if self.unfiltered_video_url is not None and self.unfiltered_video_url != "" else "None",
            "description": self.description if self.description is not None else "",
            "tags": tags,
            "sources": sources,
            "bodycam_video": bodycam_video
        }

    def __str__(self):
        return "{} {}".format(self.date, self.name)


class Source(models.Model):
    text = models.CharField("Text", max_length=1000)
    shooting = models.ForeignKey(
        Shooting,
        on_delete=models.CASCADE,
        related_name="sources"
    )

    def as_dict(self):
        """
        Serializes the tag into a JSON object

        returns tag as JSON
        """
        return {
            "id": self.id,
            "text": self.text,
        }

    def __str__(self):
        return self.text


class Tag(models.Model):
    text = models.CharField("Text", max_length=1000)
    shootings = models.ManyToManyField(Shooting, related_name="tags")
    bodycams = models.ManyToManyField(Bodycam, related_name='tags')

    def as_dict(self):
        """
        Serializes the source into a JSON object

        returns source as JSON
        """
        return {
            "id": self.id,
            "text": self.text,
        }

    def __str__(self):
        return self.text


class Tip(models.Model):
    text = models.TextField("Tip", max_length=4000)
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(Tip, self).save(*args, **kwargs)

    def __str__(self):
        text = self.text
        if len(self.text) > 20:
            text = text[0:20] + "..."
        return "{} {}".format(self.created.strftime("%Y-%m-%d"), text)


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
