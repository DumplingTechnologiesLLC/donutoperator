from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.db.models import Count
from roster.models import Shooting, Tag, Source
import datetime
import json
# Create your views here.


def convert_format(url):
    url = url.split("?")[1][2:]
    pre_format = '<iframe width="100%" height="315" src="https://www.youtube.com/embed/'
    post_format = '" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
    return pre_format + url + post_format


class SubmitShootingView(LoginRequiredMixin, View):
    def post(self, request):
        # print(request.POST)
        data = json.loads(request.POST.get("shooting"))
        # print(data)
        url = None
        if data["video_url"] is not None and len(data["video_url"]) > 0 and data["video_url"].find("?") > -1:
            url = convert_format(data["video_url"])
        try:
            print(data["date"].split("T")[0])
            date = data["date"].split("T")[0]
            shooting=Shooting.objects.create(
                state=int(data["state"]),
                city=data["city"],
                description=data["description"],
                video_url=url,
                name=data["name"],
                age=int(data["age"]),
                race=int(data["race"]),
                gender=int(data["gender"]),
                date=date,
            )
            print(data["sources"])
            for source in data["sources"]:
                Source.objects.create(
                    text=source,
                    shooting=shooting
                )
            print(data["tags"])
            for tag in data["tags"]:
                Tag.objects.create(
                    text=tag,
                    shooting=shooting
                )
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(str(e), status=500, )


class RosterListView(View):
    '''
        This gets called when no year is passed through the url.
    '''

    def get(self, request):
        shootings=Shooting.objects.all().order_by('-date')
        now=datetime.datetime.now()
        distinct_tags=Tag.objects.values('text').annotate(
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
