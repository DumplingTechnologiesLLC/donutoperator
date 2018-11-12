from roster.models import Shooting, Tag
from django.db.models import Count


def supply_basic_data(request):
    distinct_tags = Tag.objects.values('text').annotate(
        text_count=Count('text')).values('text')
    return {
        "states": Shooting.STATE_CHOICES,
        "races": Shooting.RACE_CHOICES,
        "genders": Shooting.GENDER_CHOICES,
        "all_tags": distinct_tags,
        "summarized_shootings": [
            (shooting.id, shooting.name) for shooting in Shooting.objects.filter(
            	bodycam__isnull=True)]
    }
