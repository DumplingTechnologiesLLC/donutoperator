import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
import json
from datetime import datetime
django.setup()

from roster.models import Shooting, Tag

fp = open("data.txt", "r")
table_2018 = fp.read()
table_2018 = json.loads(table_2018)

tag_fp = open("tag_data.txt", "r")
tags_2018 = tag_fp.read()
tags_2018 = json.loads(tags_2018)


def populate_year(table):
    for x in range(0, len(table)):
        print(table[x])
        name = table[x]['fields']['name']
        race = table[x]['fields']['race']
        state = table[x]['fields']['state']
        description = table[x]['fields']['description']
        date = table[x]['fields']['date']
        gender = table[x]['fields']['gender']
        shooting = Shooting.objects.get(
        	name=name,
        	date=date,
        	race=race,
        	state=state,
        	gender=gender
        )
        shooting.description = description
        shooting.save()

populate_year(table_2018)
