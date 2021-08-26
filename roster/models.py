from django.db import models
from bodycams.models import Bodycam
from django.utils import timezone
from django.urls import reverse
from django.contrib.sitemaps import ping_google
from django.contrib.auth import get_user_model

User = get_user_model()


class Shooting(models.Model):
    AL = 0
    AK = 1
    AZ = 2
    AR = 3
    CA = 4
    CO = 5
    CT = 6
    DE = 7
    FL = 8
    GA = 9
    HI = 10
    ID = 11
    IL = 12
    IN = 13
    IA = 14
    KS = 15
    KY = 16
    LA = 17
    ME = 18
    MD = 19
    MA = 20
    MI = 21
    MN = 22
    MS = 23
    MO = 24
    MT = 25
    NE = 26
    NV = 27
    NH = 28
    NJ = 29
    NM = 30
    NY = 31
    NC = 32
    ND = 33
    OH = 34
    OK = 35
    OR = 36
    PA = 37
    RI = 38
    SC = 39
    SD = 40
    TN = 41
    TX = 42
    UT = 43
    VT = 44
    VA = 45
    WA = 46
    WV = 47
    WI = 48
    WY = 49
    DC = 50
    PR = 51
    GU = 52
    STATE_CHOICES = (
        (AL, "AL"),
        (AK, "AK"),
        (AZ, "AZ"),
        (AR, "AR"),
        (CA, "CA"),
        (CO, "CO"),
        (CT, "CT"),
        (DE, "DE"),
        (FL, "FL"),
        (GA, "GA"),
        (HI, "HI"),
        (ID, "ID"),
        (IL, "IL"),
        (IN, "IN"),
        (IA, "IA"),
        (KS, "KS"),
        (KY, "KY"),
        (LA, "LA"),
        (ME, "ME"),
        (MD, "MD"),
        (MA, "MA"),
        (MI, "MI"),
        (MN, "MN"),
        (MS, "MS"),
        (MO, "MO"),
        (MT, "MT"),
        (NE, "NE"),
        (NV, "NV"),
        (NH, "NH"),
        (NJ, "NJ"),
        (NM, "NM"),
        (NY, "NY"),
        (NC, "NC"),
        (ND, "ND"),
        (OH, "OH"),
        (OK, "OK"),
        (OR, "OR"),
        (PA, "PA"),
        (RI, "RI"),
        (SC, "SC"),
        (SD, "SD"),
        (TN, "TN"),
        (TX, "TX"),
        (UT, "UT"),
        (VT, "VT"),
        (VA, "VA"),
        (WA, "WA"),
        (WV, "WV"),
        (WI, "WI"),
        (WY, "WY"),
        (DC, "DC"),
        (PR, "PR"),
        (GU, "GU"),
    )
    MALE = 0
    FEMALE = 1
    UNKNOWN_GENDER = 2
    GENDER_CHOICES = (
        (MALE, "Male"),
        (FEMALE, "Female"),
        (UNKNOWN_GENDER, "Unknown")
    )
    NATIVE_AMERICAN = 0
    ASIAN = 1
    BLACK = 2
    PACIFIC_ISLANDER = 3
    WHITE = 4
    HISPANIC_LATINO = 5
    NONE_GIVEN = 6
    OTHER = 7
    RACE_CHOICES = (
        (NATIVE_AMERICAN, "Native American"),
        (ASIAN, "Asian"),
        (BLACK, "Black"),
        (PACIFIC_ISLANDER, "Native Hawaiian or Other Pacific Islander"),
        (WHITE, "White"),
        (HISPANIC_LATINO, "Hispanic/Latino"),
        (NONE_GIVEN, "None Given"),
        (OTHER, "Other"),
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
    specially_exempted_users = models.ManyToManyField(
        User,
        related_name="exempted_shootings"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shootings",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        "Creation Date", editable=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('roster:shooting-detail', args=[str(self.id)])

    def bodycam(self):  # pragma: no cover
        try:
            if self.bodycams.all().first() is not None:
                return self.bodycams.all().first()
            else:
                return False
        except Exception:
            return False

    def save(self, *args, **kwargs):  # pragma: no cover
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        try:
            ping_google()
        except Exception:
            pass
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
