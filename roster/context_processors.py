from roster.models import Shooting, Tag

def supply_basic_data(request):
    distinct_tags = Tag.objects.all().distinct()
    return {
        "states": Shooting.STATE_CHOICES,
        "races": Shooting.RACE_CHOICES,
        "genders": Shooting.GENDER_CHOICES,
        "all_tags": distinct_tags,
    }
