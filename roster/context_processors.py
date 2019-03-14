from roster.models import Shooting, Tag, Tip, Feedback
import datetime

def supply_basic_data(request):
    distinct_tags = Tag.objects.all().distinct()
    number_of_tips = Tip.objects.all().count()
    number_of_feedbacks = Feedback.objects.all().count()
    years = []
    for x in range(2013, datetime.datetime.now().year + 1):
        years.append(x)
    return {
        "valid_years": years,
    	"number_of_feedbacks": number_of_feedbacks,
        "number_of_tips": number_of_tips,
        "states": Shooting.STATE_CHOICES,
        "races": Shooting.RACE_CHOICES,
        "genders": Shooting.GENDER_CHOICES,
        "all_tags": distinct_tags,
    }
