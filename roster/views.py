from django.http import HttpResponse, JsonResponse
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


def connect_sources_and_tags(shooting, data):
    """Adds all sources and tags within data to given Shooting

    {
        "sources": [string, string,...],
        "tags": [string, string,...]
    }

    Arguments:
    :param shooting: a Shooting Django ORM object
    :param data: a dictionary with an array of strings for sources, and array of strings
        for tags as described above

    Returns:
    Nothing
    """
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


def create_html_errors(form):  # pragma: no cover
    """Creates an HTML string of the form's errors

    Arguments:
    :param form: an invalid Django form

    Returns:
    a string of the rrors concatenated together.
    """
    error_string = ""
    for key, error in form.errors.items():
        error_string += "{}: {}<br>".format(key, error)
    return error_string


class AjaxSelect2Shootings(LoginRequiredMixin, View):
    def get(self, request):  # pragma: no cover
        """Ajax Only

        Provides select2 with the results based on what the person searches. Keeps
        Select2 from becoming sluggish.

        Expects:
        {
            "term": string to filter by
        }
        Arguments:
        :param request: a WSGI Django request object with a GET dictionary described
        above

        Returns:
        a dictionary of Shootings matching that term, in a form Select2 expects.
        """
        parameter = request.GET.get("term")
        if parameter is not None:
            shootings = Shooting.objects.filter(
                bodycam__isnull=True).filter(name__icontains=parameter).order_by('-date')
            results = [{"id": shooting.id, "text": "{}, {}".format(
                shooting.name, shooting.date.strftime("%Y-%m-%d"))} for shooting in shootings]
            return JsonResponse({"results": results},
                                safe=False)


class DeleteShootingView(LoginRequiredMixin, View):
    def post(self, request):
        """Ajax Only

        Deletes a Shooting object that matches the id provided

        Expects:
        {
            "id": integer pk
        }

        Arguments:
        :param request: a WSGI Django request object with a POST dictionary described
        above

        Returns:
        200 On success
        500 and error string on failure
        """
        data = request.POST.get("id")
        try:
            Shooting.objects.get(pk=data).delete()
            return HttpResponse(status=200)
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )


class EditShootingView(LoginRequiredMixin, View):
    def post(self, request):
        """Ajax Only

        Edits a shooting based on data submitted

        Expects:
        {
            id: integer pk,
            "name": string,
            "age": integer,
            "date": datestring "YYYY-MM-DDThh:mm:ss,
            "race": integer,
            "gender": integer,
            "state": integer,
            "city": string,
            "video_url": string,
            "unfiltered_video_url": string
            "description": string,
            "tags": array of strings,
            "sources": array of strings,
        }

        Arguments:
        :param request: A WSGI Django request object with a POST dictionary as above

        Returns:
        200 on success
        400 with error string on failure
        """
        data = json.loads(request.POST.get("shooting"))
        data["date"] = data["date"].split("T")[0]
        if (isinstance(data["age"], str) and
                len(data["age"]) == 0) or data["age"] is None:
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        try:
            shooting = Shooting.objects.get(pk=int(data["id"]))
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )
        form = ShootingModelForm(data, instance=shooting)
        if form.is_valid():
            shooting = form.save()
            shooting.tags.all().delete()
            shooting.sources.all().delete()
            shooting.unfiltered_video_url = data["video_url"]
            shooting.save()
            connect_sources_and_tags(shooting, data)
            return HttpResponse(status=200)
        return HttpResponse(create_html_errors(form), status=400)


class SubmitShootingView(LoginRequiredMixin, View):
    def post(self, request):
        """Ajax only

        Creates a shooting based on the data submitted

        Expects:
        {
            id: integer pk,
            "name": string,
            "age": integer,
            "date": datestring "YYYY-MM-DDThh:mm:ss,
            "race": integer,
            "gender": integer,
            "state": integer,
            "city": string,
            "video_url": string,
            "unfiltered_video_url": string
            "description": string,
            "tags": array of strings,
            "sources": array of strings,
        }

        Arguments:
        :param request: A WSGI Django request object with a POST dictionary as above

        Returns:
        200 on success
        400 with error string on failure
        """
        data = json.loads(request.POST.get("shooting"))
        data["date"] = data["date"].split("T")[0]
        if (isinstance(data["age"], str) and
                len(data["age"]) == 0) or data["age"] is None:
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        form = ShootingModelForm(data)
        if form.is_valid():
            shooting = form.save()
            shooting.unfiltered_video_url = data["video_url"]
            shooting.save()
            connect_sources_and_tags(shooting, data)
            return HttpResponse(shooting.id, status=200)
        return HttpResponse(create_html_errors(form), status=400)


class RosterListView(View):
    def get(self, request, date=datetime.datetime.now().year):
        '''Returns the roster index view

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of index.html, a list of killings for the year selected
        the number of killing, the year, and the departments
        '''
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
