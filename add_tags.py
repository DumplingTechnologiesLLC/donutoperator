import os
import django
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.core.exceptions import MultipleObjectsReturned
from roster.models import Shooting, Tag
datafiles = [
	('ripped_data/2013_data.js', 2013),
	('ripped_data/2014_data.js', 2014),
	('ripped_data/2015_data.js', 2015),
	('ripped_data/2016_data.js', 2016),
	('ripped_data/2017_data.js', 2017),
]
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
			continue
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
		for tag in person["tags"]:
			mmtag, created = Tag.objects.get_or_create(text=tag)
			mmtag.shootings.add(shooting)
			bodycam = shooting.bodycam()
			if bodycam:
				mmtag.bodycams.add(bodycam)
