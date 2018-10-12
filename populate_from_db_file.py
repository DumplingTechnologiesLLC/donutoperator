import os
import django
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from roster.models import Shooting, Tag, Source

fp = open("db_backup.js", "r")
db_table = fp.read()
db_table = json.loads(db_table)
created = []


def populate_year(table):
    print("Creating...")
    for entry in table:
        print("{} {}".format(entry["name"], entry["date"]))
        name = entry['name']
        age = entry["age"]
        race = entry['race']
        state = entry['state']
        city = entry['city']
        description = entry['description']
        video_url = entry["video_url"]
        unfiltered_video_url = entry["unfiltered_video_url"]
        date = entry['date']
        gender = entry['gender']
        shooting = Shooting.objects.create(
            name=name,
            age=age,
            date=date,
            race=race,
            state=state,
            video_url=video_url,
            unfiltered_video_url=unfiltered_video_url,
            city=city,
            gender=gender,
            description=description,
        )
        created.append(shooting.id)
        for tag in entry["tags"]:
            Tag.objects.create(
                text=tag["text"],
                shooting=shooting
            )
        for source in entry["sources"]:
            Source.objects.create(
                text=source["text"],
                shooting=shooting
            )
    print("Done")


try:
    populate_year(db_table)
except Exception as e:
    print("Something went wrong")
    print(str(e))
    print("Cleaning up")
    for id in created:
        Shooting.objects.get(pk=id).delete()
print("Done")
