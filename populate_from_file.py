import os
import django
import json
from datetime import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from roster.models import Shooting, Tag, Source

print("loading tables")
STATE_CHOICES = {
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
fp = open("ripped_data/2013_data.js", "r")
table_2013 = fp.read()
table_2013 = json.loads(table_2013)
fp = open("ripped_data/2014_data.js", "r")
table_2014 = fp.read()
table_2014 = json.loads(table_2014)
fp = open("ripped_data/2015_data.js", "r")
table_2015 = fp.read()
table_2015 = json.loads(table_2015)
fp = open("ripped_data/2016_data.js", "r")
table_2016 = fp.read()
table_2016 = json.loads(table_2016)
fp = open("ripped_data/2017_data.js", "r")
table_2017 = fp.read()
table_2017 = json.loads(table_2017)
print("creating...")
tables = [table_2013, table_2014, table_2015, table_2016, table_2017]
created = []
try:
    counter = 2013
    for table in tables:
        print("populating {}".format(counter))
        counter += 1
        for entry in table:
            state = ""
            city = "No City"
            description = ""
            video_url = ""
            unfiltered_video_url = ""
            name = "No Name"
            age = -1
            race = Shooting.RACE_CHOICES[6][0]
            gender = Shooting.GENDER_CHOICES[2][0]
            date = ""
            tags = []
            sources = []
            if "state" in entry:
                state = STATE_CHOICES[entry["state"].strip()]
            if "city" in entry:
                city = entry["city"].strip()
            if "description" in entry:
                description = entry["description"].strip()
            if "video_url" in entry:
                video_url = entry["video_url"].strip()
            if "unfiltered_video_url" in entry:
                unfiltered_video_url = entry["unfiltered_video_url"].strip()
            if "name" in entry:
                name = entry["name"].strip()
            if "age" in entry:
                age = int(entry["age"])
            if "race" in entry:
                race = int(entry["race"])
            if "gender" in entry:
                gender = int(entry["gender"])
            if "date" in entry:
                date = entry["date"].strip()
                date = datetime.strptime(date, "%B %d, %Y")
            if "tags" in entry:
                tags = entry["tags"]
            if "sources" in sources:
                sources = entry["sources"]
            print("{} {}".format(entry["name"], entry["date"]))
            shooting = Shooting.objects.create(
                state=state,
                city=city,
                description=description,
                video_url=video_url,
                unfiltered_video_url=unfiltered_video_url,
                name=name,
                age=age,
                race=race,
                gender=gender,
                date=date,
            )
            for tag in tags:
                Tag.objects.create(
                    text=tag,
                    shooting=shooting,
                )
            for source in sources:
                print(source)
                Source.objects.create(
                    text=source,
                    shooting=shooting
                )
            created.append(shooting.id)
except Exception as e:
    print("Something went wrong")
    print(e)
    print("Cleaning up")
    for shooting in created:
        Shooting.objects.get(pk=shooting).delete()
print("Done")
