from django.core.cache import cache
from itertools import chain
import logging
QUERYSET_KEY = "SHOOTINGS"


def retrieve_from_cache(date):
	""" Given a date, returns a queryset stitched together into a list
	from the cache, or None

	Arguments:
	:param date: a year, in YYYY format

	Returns:
	A list if a key is found for that year, otherwise None
	"""
	queryset1 = cache.get("{}{}1".format(QUERYSET_KEY, date))
	queryset2 = cache.get("{}{}2".format(QUERYSET_KEY, date))
	queryset3 = cache.get("{}{}3".format(QUERYSET_KEY, date))
	queryset4 = cache.get("{}{}4".format(QUERYSET_KEY, date))
	if (queryset1 is not None and
		queryset2 is not None and
		queryset3 is not None and
			queryset4 is not None):
		logging.info("Cache hit")
		print("Cache hit")
		return list(chain(queryset1, queryset2, queryset3, queryset4))
	logging.info("Cache missed")
	print("Cache missed")
	return None


def invalidate_cache(date):
	""" Given a year, invalidates the cache for a particular year so that the
	database call goes through

	Arguments:
	:param date: a year in YYYY form to be used as the key

	Returns:
	Nothing
	"""
	keys = [
		"{}{}1".format(QUERYSET_KEY, date),
		"{}{}2".format(QUERYSET_KEY, date),
		"{}{}3".format(QUERYSET_KEY, date),
		"{}{}4".format(QUERYSET_KEY, date)
	]
	logging.info("Cache invalidated for {}".format(date))
	print("Cache invalidated for {}".format(date))
	cache.delete_many(keys)


def store_in_cache(queryset, date):
	""" Given a queryset, breaks and store them up in the cache to avoid the memory
	overflow

	Arguments:
	:param queryset: a queryset to be stored in the cache
	:param date: a year in YYYY form to be used as the key

	Returns:
	Nothing
	"""
	total = queryset.count()
	if total % 4 == 0:
		offset = total / 4
	else:
		offset = int(total / 4)
	logging.info("Cache stored for {}".format(date))
	print("Cache stored for {}".format(date))
	cache.set("{}{}1".format(QUERYSET_KEY, date), queryset[0:offset])
	cache.set("{}{}2".format(QUERYSET_KEY, date), queryset[offset:(2 * offset)])
	cache.set("{}{}3".format(QUERYSET_KEY, date), queryset[(offset * 2):(offset * 3)])
	cache.set("{}{}4".format(QUERYSET_KEY, date), queryset[offset * 3:])
