from .models import Video, Tag
from feedback.models import Feedback
from config.utils import mobileBrowser
import datetime


def supply_basic_data(request):
    distinct_tags = Tag.objects.all().distinct()
    number_of_feedbacks = Feedback.objects.all().count()
    years = []
    title_current_year = datetime.datetime.now().year
    number_of_shootings_this_year = Video.objects.filter(
        date__year=title_current_year).count()
    for x in range(2013, title_current_year + 1):
        years.append(x)
    return {
        "title_current_year": title_current_year,
        "valid_years": years,
        "number_of_shootings_this_year": number_of_shootings_this_year,
        "number_of_feedbacks": number_of_feedbacks,
        "states": Video.STATE_CHOICES,
        "all_tags": distinct_tags,
        "mobile": mobileBrowser(request)
    }
