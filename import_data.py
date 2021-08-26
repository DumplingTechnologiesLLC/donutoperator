from django.contrib.auth import get_user_model
import os
import django
import json
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from roster.models import Shooting, Tag, Source  # noqa
from django.core.exceptions import MultipleObjectsReturned  # noqa
User = get_user_model()
datafiles = [
    ('misc-data-and-scripts/ripped_data/2013_data.js', 2013),
    ('misc-data-and-scripts/ripped_data/2014_data.js', 2014),
    ('misc-data-and-scripts/ripped_data/2015_data.js', 2015),
    ('misc-data-and-scripts/ripped_data/2016_data.js', 2016),
    ('misc-data-and-scripts/ripped_data/2017_data.js', 2017),
]


state_lookup = {

    "AL": 0,
    "AK": 1,
    "AZ": 2,
    "AR": 3,
    "CA": 4,
    "CO": 5,
    "CT": 6,
    "DE": 7,
    "FL": 8,
    "GA": 9,
    "HI": 10,
    "ID": 11,
    "IL": 12,
    "IN": 13,
    "IA": 14,
    "KS": 15,
    "KY": 16,
    "LA": 17,
    "ME": 18,
    "MD": 19,
    "MA": 20,
    "MI": 21,
    "MN": 22,
    "MS": 23,
    "MO": 24,
    "MT": 25,
    "NE": 26,
    "NV": 27,
    "NH": 28,
    "NJ": 29,
    "NM": 30,
    "NY": 31,
    "NC": 32,
    "ND": 33,
    "OH": 34,
    "OK": 35,
    "OR": 36,
    "PA": 37,
    "RI": 38,
    "SC": 39,
    "SD": 40,
    "TN": 41,
    "TX": 42,
    "UT": 43,
    "VT": 44,
    "VA": 45,
    "WA": 46,
    "WV": 47,
    "WI": 48,
    "WY": 49,
    "DC": 50,
    "PR": 51,
    "GU": 52,
}


def convert_date(datestr):
    if datestr is None:
        return None
    # Expects format: December 31, 2020
    MONTH_LOCATION = 0
    DAY_LOCATION = 1
    YEAR_LOCATION = 2
    parts = datestr.split(' ')
    month_lookup = {
        'JANUARY': 1,
        'JAN': 1,
        'FEBRUARY': 2,
        'FEB': 2,
        'MARCH': 3,
        'MARCH': 3,
        'APRIL': 4,
        'APR': 4,
        'MAY': 5,
        'JUNE': 6,
        'JUN': 6,
        'JULY': 7,
        'JUL': 7,
        'AUGUST': 8,
        'AUG': 8,
        'SEPTEMBER': 9,
        'SEPT': 9,
        'SEP': 9,
        'OCTOBER': 10,
        'OCT': 10,
        'NOVEMBER': 11,
        'NOV': 11,
        'DECEMBER': 12,
        'DEC': 12,
    }
    year = int(parts[YEAR_LOCATION])
    month = int(month_lookup[parts[MONTH_LOCATION].upper()])
    day = int(parts[DAY_LOCATION][:-1])

    return datetime.date(year, month, day)


user, created = User.objects.get_or_create(
    username="Sentinel User"
)
for file, year in datafiles:
    with open(file) as f:
        data = json.load(f)
        for person in data:
            try:
                shooting = Shooting.objects.get(
                    name=person["name"],
                    age=person.get("age", -1),
                    date__year=year
                )
            except Shooting.DoesNotExist:
                shooting = Shooting.objects.create(
                    has_bodycam=False,
                    state=state_lookup[person["state"]],
                    city=person.get('city', ''),
                    description="",
                    video_url="",
                    unfiltered_video_url="",
                    name=person.get('name', 'No Name'),
                    age=person.get('age', -1),
                    race=person.get('race', Shooting.NONE_GIVEN),
                    gender=person.get('gender', Shooting.UNKNOWN_GENDER),
                    date=convert_date(person.get('date', None)),
                    created_by=user,
                    created=datetime.datetime.now()
                )
            except MultipleObjectsReturned:
                for shooting in Shooting.objects.filter(name=person["name"],
                                                        age=person["age"],
                                                        date__year=year
                                                        ):
                    for tag in person["tags"]:
                        mmtag, created = Tag.objects.get_or_create(text=tag)
                        mmtag.shootings.add(shooting)
                        bodycam = shooting.bodycam()
                        if bodycam:
                            mmtag.bodycams.add(bodycam)
                continue
            for tag in person.get('tags', []):
                mmtag, created = Tag.objects.get_or_create(text=tag)
                mmtag.shootings.add(shooting)
                bodycam = shooting.bodycam()
                if bodycam:
                    mmtag.bodycams.add(bodycam)
            for source in person.get('sources', []):
                source, created = Source.objects.get_or_create(
                    text=source,
                    shooting=shooting)
