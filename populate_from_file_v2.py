import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
import json
from datetime import datetime
django.setup()

from roster.models import Shooting, Tag, Source

fp = open("db_as_text.txt", "r")
table_2018 = fp.read()
table_2018 = json.loads(table_2018)
print("creating...")
for entry in table_2018:
    print(entry)
    shooting = Shooting.objects.create(
        state=entry["state"],
        city=entry["city"],
        description=entry["description"],
        video_url=entry["video_url"],
        name=entry["name"],
        age=entry["age"],
        race=entry["race"],
        gender=entry["gender"],
        date=entry["date"],
    )
    for tag in entry['tags']:
        Tag.objects.create(
            text=tag['text'],
            shooting=shooting,
        )
    for source in entry['sources']:
        print(source)
        Source.objects.create(
            text=source["text"],
            shooting=shooting
        )
print("done")
