from django.shortcuts import render
from django.views import View
from django.db.models import Count
from roster.models import Shooting, Tag
import datetime
# Create your views here.


class RosterListView(View):
    '''
        This gets called when no year is passed through the url.
    '''

    def get(self, request):
        shootings = Shooting.objects.all().order_by('-date')
        now = datetime.datetime.now()
        distinct_tags = Tag.objects.values('text').annotate(
            text_count=Count('text')).values('text')
        print(distinct_tags)
        return render(request, "roster/index.html", {
            "shootings": shootings,
            "year": now.year,
            "states": Shooting.STATE_CHOICES,
            "races": Shooting.RACE_CHOICES,
            "genders": Shooting.GENDER_CHOICES,
            "all_tags": distinct_tags,
        })
