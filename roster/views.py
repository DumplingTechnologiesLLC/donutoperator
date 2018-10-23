from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.db.models import Count
from roster.models import Shooting, Tag, Source
from roster.forms import ShootingModelForm
from django.http import QueryDict
import datetime
import json
# Create your views here.


def convert_format(url):
    url = url.split("?")[1][2:]
    pre_format = '<iframe width="100%" height="315" src="https://www.youtube.com/embed/'
    post_format = ('" frameborder="0" allow="autoplay; encrypted-'
                   'media" allowfullscreen></iframe>')
    return pre_format + url + post_format


class DeleteShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = request.POST.get("id")
        try:
            Shooting.objects.get(pk=data).delete()
            return HttpResponse(status=200)
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )


class EditShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.POST.get("shooting"))
        try:
            shooting = Shooting.objects.get(pk=int(data["id"]))
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )
        url = None
        if (data["video_url"] is not None and len(data["video_url"]) > 0 and
                data["video_url"].find("?") > -1):
            url = convert_format(data["video_url"])
            shooting.unfiltered_video_url = data["video_url"]
        elif data["video_url"].find("?") < 0 and len(data["video_url"]) > 0:
            return HttpResponse("Please provide a valid video url", status=400)
        try:
            name = data["name"]
            if len(name) == 0:
                name = "No Name"
            city = data["city"]
            if len(city) == 0:
                city = "Unknown"
            age = data["age"]
            if (isinstance(age, str) and len(age) == 0) or age is None:
                age = -1
            else:
                age = int(age)
                if age < 0:
                    return HttpResponse(
                        "Please provide a positive number for the age", status=400)
            shooting.state = int(data["state"])
            shooting.city = city
            shooting.description = data["description"]
            shooting.video_url = url
            shooting.name = name
            shooting.age = age
            shooting.race = int(data["race"])
            shooting.gender = int(data["gender"])
            shooting.date = data["date"].split("T")[0]
            shooting.tags.all().delete()
            shooting.sources.all().delete()
            shooting.save()
            for source in data["sources"]:
                if Source.objects.filter(text=source, shooting=shooting).count() == 0:
                    Source.objects.create(
                        text=source,
                        shooting=shooting
                    )
            for tag in data["tags"]:
                if Tag.objects.filter(text=tag, shooting=shooting).count() == 0:
                    Tag.objects.create(
                        text=tag,
                        shooting=shooting
                    )
            return HttpResponse(status=200)
        except Exception as e:
            message = "<br><br>error: {}<br><br>data: {}".format(
                str(e), json.dumps(data))
            return HttpResponse(message, status=500)


class SubmitShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.POST.get("shooting"))
        url = None
        if (data["video_url"] is not None and len(data["video_url"]) > 0 and
                data["video_url"].find("?") > -1):
            url = convert_format(data["video_url"])
        elif data["video_url"].find("?") < 0 and len(data["video_url"]) > 0:
            return HttpResponse("Please provide a valid video URL", status=400, )
        try:
            name = data["name"]
            if len(name) == 0:
                name = "No Name"
            city = data["city"]
            if len(city) == 0:
                city = "Unknown"
            age = data["age"]
            if (isinstance(age, str) and len(age) == 0) or age is None:
                age = -1
            else:
                age = int(age)
                if age < 0:
                    return HttpResponse(
                        "Please provide a positive number for the age", status=400)
            date = data["date"].split("T")[0]
            shooting = Shooting.objects.create(
                state=int(data["state"]),
                city=city,
                description=data["description"],
                video_url=url,
                name=name,
                age=age,
                race=int(data["race"]),
                gender=int(data["gender"]),
                date=date,
            )
            for source in data["sources"]:
                Source.objects.create(
                    text=source,
                    shooting=shooting
                )
            for tag in data["tags"]:
                Tag.objects.create(
                    text=tag,
                    shooting=shooting
                )
            return HttpResponse(status=200)
        except Exception as e:
            message = "<br><br>error: {}<br><br>data: {}".format(
                str(e), json.dumps(data))
            return HttpResponse(message, status=500, )


class RosterListView(View):
    '''
        This gets called when no year is passed through the url.
    '''

    def get(self, request, date=datetime.datetime.now().year):
        display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        shootings = Shooting.objects.filter(
            date__year=display_date.year).order_by('-date')
        distinct_tags = Tag.objects.values('text').annotate(
            text_count=Count('text')).values('text')
        return render(request, "roster/index.html", {
            "shootings": [obj.as_dict() for obj in shootings],
            "total": shootings.count(),
            "year": display_date.year,
            "states": Shooting.STATE_CHOICES,
            "races": Shooting.RACE_CHOICES,
            "genders": Shooting.GENDER_CHOICES,
            "all_tags": distinct_tags,

        })
