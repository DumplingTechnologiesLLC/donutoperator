from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.list import ListView
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from roster.models import Shooting, Tag, Source, Tip
from roster.forms import ShootingModelForm, TipModelForm, FeedbackModelForm
from roster.serializers import ShootingSerializer
from rest_framework.generics import ListAPIView
import datetime
import logging
import json


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
        mmtag, created = Tag.objects.get_or_create(text=tag)
        mmtag.shootings.add(shooting)


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


def submit_form(form, data):
    """Submits a shooting and adds tags to the shooting

    Arguments:
    :param form: a validated ShootingModelForm
    :param data: a dictionary containing a JSON array of tags

    Returns:
    a Shooting object with tags attached
    """
    shooting = form.save()
    shooting.tags.clear()
    shooting.sources.all().delete()
    shooting.unfiltered_video_url = data["video_url"]
    shooting.save()
    connect_sources_and_tags(shooting, data)
    return shooting


class ShootingsAPI(ListAPIView):
    serializer_class = ShootingSerializer
    model = Shooting

    def validate(date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def get_queryset(self):
        print("test")
        race_lookup_table = {
            "NA": 0,
            "A": 1,
            "B": 2,
            "PI": 3,
            "W": 4,
            "L": 5,
            "None": 6,
            "O": 7,
        }
        gender_lookup_table = {
            "M": 0,
            "F": 1,
            "U": 2
        }
        state_lookup_table = {
            "AL": 0,
            "AK": 1,
            "AZ": 2,
            "AR": 3,
            "CA": 4,
            "CO": 5,
            "CT": 6,
            "DE": 7,
            "FL": 8,
            "GA": 9,
            "HI": 10,
            "ID": 11,
            "IL": 12,
            "IN": 13,
            "IA": 14,
            "KS": 15,
            "KY": 16,
            "LA": 17,
            "ME": 18,
            "MD": 19,
            "MA": 20,
            "MI": 21,
            "MN": 22,
            "MS": 23,
            "MO": 24,
            "MT": 25,
            "NE": 26,
            "NV": 27,
            "NH": 28,
            "NJ": 29,
            "NM": 30,
            "NY": 31,
            "NC": 32,
            "ND": 33,
            "OH": 34,
            "OK": 35,
            "OR": 36,
            "PA": 37,
            "RI": 38,
            "SC": 39,
            "SD": 40,
            "TN": 41,
            "TX": 42,
            "UT": 43,
            "VT": 44,
            "VA": 45,
            "WA": 46,
            "WV": 47,
            "WI": 48,
            "WY": 49,
            "DC": 50,
            "PR": 51,
            "GU": 52,
        }
        name = self.request.GET.get("name", None)
        dateBefore = self.request.GET.get("dateBefore", None)
        dateAfter = self.request.GET.get("dateAfter", None)
        date = self.request.GET.get("date", None)
        tags = self.request.GET.get("tags", None)
        race = self.request.GET.get("race", None)
        gender = self.request.GET.get("gender", None)
        state = self.request.GET.get("state", None)
        youngerThan = self.request.GET.get("youngerThan", None)
        olderThan = self.request.GET.get("olderThan", None)
        age = self.request.GET.get("age", None)
        text = self.request.GET.get("text", None)
        city = self.request.GET.get("city", None)
        year = self.request.GET.get("year", None)
        queryset = None
        if year is not None:
            queryset = Shooting.objects.filter(date__year=year).prefetch_related(
                "tags", "sources", "bodycams")
        else:
            queryset = Shooting.objects.filter(
                date__year=datetime.datetime.now().year).prefetch_related(
                "tags", "sources", "bodycams")
        if tags is not None:
            if "," in tags:
                tags = tags.split(",")
                tags = Tag.objects.filter(text__in=tags)
                queryset = Shooting.objects.none()
                for t in tags:
                    queryset = queryset.union(queryset, t.shootings.all())
                queryset = queryset.prefetch_related("tags", "sources", "bodycams")
            else:
                tags = Tag.objects.filter(text=tags)
                queryset = tags.shootings.all().prefetch_related(
                    "tags", "sources", "bodycams")
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        if dateBefore is not None and self.validate(dateBefore):
            queryset = queryset.filter(date__lte=dateBefore)
        if dateAfter is not None and self.validate(dateAfter):
            queryset = queryset.filter(date__gte=dateAfter)
        if date is not None and self.validate(date):
            queryset = queryset.filter(date=date)
        if race is not None and race_lookup_table.get(race) is not None:
            queryset = queryset.filter(race=race_lookup_table.get(race))
        if gender is not None and gender_lookup_table.get(gender) is not None:
            queryset = queryset.filter(gender=gender_lookup_table.get(gender))
        if state is not None and state_lookup_table.get(state) is not None:
            queryset = queryset.filter(state=state_lookup_table.get(state))
        if youngerThan is not None and isinstance(youngerThan, int):
            queryset = queryset.filter(age__lte=youngerThan)
        if olderThan is not None and isinstance(olderThan, int):
            queryset = queryset.filter(age__gte=olderThan)
        if age is not None and isinstance(age, int):
            queryset = queryset.filter(age=age)
        if text is not None:
            queryset = queryset.filter(description__icontains=text)
        if city is not None:
            queryset = queryset.filter(city__icontains=city)
        print("still alive")
        return queryset


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
                has_bodycam=False).filter(name__icontains=parameter).order_by('-date')
            results = [
                {
                    "id": shooting.id, "text": "{}, {}".format(
                        shooting.name,
                        shooting.date.strftime("%Y-%m-%d")
                    )} for shooting in shootings]
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
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
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
                len(data["age"]) == 0) or data["age"] is None or data["age"] == "No Age":
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        try:
            shooting = Shooting.objects.get(pk=int(data["id"]))
        except Shooting.DoesNotExist as e:
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            return HttpResponse(str(e), status=500, )
        form = ShootingModelForm(data, instance=shooting)
        if form.is_valid():
            shooting = submit_form(form, data)
            return HttpResponse(shooting.id, status=200)
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
                len(data["age"]) == 0) or data["age"] is None or data["age"] == "No Age":
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        form = ShootingModelForm(data)
        if form.is_valid():
            shooting = submit_form(form, data)
            return HttpResponse(shooting.id, status=200)
        return HttpResponse(create_html_errors(form), status=400)


class TipPage(FormView):
    template_name = "config/tip.html"
    form_class = TipModelForm
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "Thank you for the input, we will look into it.")
        form.save()
        return super().form_valid(form)


class FeedbackPage(FormView):
    template_name = "config/feedback.html"
    form_class = FeedbackModelForm
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "Thank you for the input, we will look into it.")
        form.save()
        return super().form_valid(form)


class TipList(LoginRequiredMixin, ListView):
    model = Tip

    def post(self, request):
        ids = request.POST.getlist("tips[]")
        for id in ids:
            id = int(id)
            Tip.objects.get(pk=id).delete()
        return HttpResponse(status=200)


class RosterListData(View):
    def get(self, request):
        try:
            date = int(request.GET.get("year", datetime.datetime.now().year))
        except ValueError as e:
            return HttpResponse("Invalid date", status=400,)
        shootings = Shooting.objects.filter(
            date__year=date).order_by('-date').prefetch_related(
            "tags", "sources", "bodycams")
        return JsonResponse(
            {
                "shootings": [obj.as_dict() for obj in shootings],
                "total": shootings.count()
            },
            safe=False
        )


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
        display_date = None
        try:
            display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        except ValueError as e:
            messages.warning(request, "No data exists for that year.")
            return HttpResponseRedirect(reverse("roster:index"))
        return render(request, "roster/index.html", {
            "year": display_date.year,
        })
