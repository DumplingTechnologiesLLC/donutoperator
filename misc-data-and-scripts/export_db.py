import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
import json
from datetime import datetime
django.setup()

from roster.models import Shooting, Tag, Source

fp = open("db_backup.js", "w")
shootings = Shooting.objects.all()
shootings_as_json = []
for shooting in shootings:
    data = {
        "tags": [],
        "sources": [],
        "state": shooting.state,
        "city": shooting.city,
        "description": shooting.description,
        "video_url": shooting.video_url,
        "unfiltered_video_url": shooting.unfiltered_video_url,
        "name": shooting.name,
        "age": shooting.age,
        "race": shooting.race,
        "gender": shooting.gender,
        "date": shooting.date.strftime("%Y-%m-%d")
    }
    for source in shooting.sources.all():
        data["sources"].append({
            "text": source.text,
        })
    for tag in shooting.tags.all():
        data["tags"].append({
            "text": tag.text,
        })
    shootings_as_json.append(data)

with open("db_backup.js", 'w') as outfile:
    json.dump(shootings_as_json, outfile)
