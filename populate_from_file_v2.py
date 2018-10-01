import os
import django
import json
from datetime import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from roster.models import Shooting, Tag, Source

print("loading tables")
fp = open("ripped_data/2013_data.html", "r")
table_2013 = fp.read()
table_2013 = json.loads(table_2013)
fp = open("ripped_data/2014_data.html", "r")
table_2014 = fp.read()
table_2014 = json.loads(table_2014)
fp = open("ripped_data/2015_data.html", "r")
table_2015 = fp.read()
table_2015 = json.loads(table_2015)
fp = open("ripped_data/2016_data.html", "r")
table_2016 = fp.read()
table_2016 = json.loads(table_2016)
fp = open("ripped_data/2017_data.html", "r")
table_2017 = fp.read()
table_2017 = json.loads(table_2017)
print("creating...")
tables = [table_2013, table_2014, table_2015, table_2016, table_2017]
counter = 2013
for table in tables:
    print("populating {}".format(counter))
    counter += 1
    for entry in table:
        state = "No State"
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
            state = entry["state"].strip()
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
            age = int(entry["age"]).strip()
        if "race" in entry:
            race = int(entry["race"]).strip()
        if "gender" in entry:
            gender = int(entry["gender"]).strip()
        if "date" in entry:
            date = entry["date"].strip()
            date = datetime.strptime(date, "%B %d, %Y")
        if "tags" in entry:
            tags = entry["tags"]
        if "sources" in sources:
            sources = entry["sources"]
        print(entry)
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
print("done")
