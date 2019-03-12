from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import TruncMonth
from itertools import chain
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.list import ListView
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from roster.models import Shooting, Tag, Source, Tip
from roster.forms import ShootingModelForm, TipModelForm, FeedbackModelForm
from roster.serializers import ShootingSerializer, TagSerializer
from rest_framework.generics import ListAPIView
import datetime
import logging
import json


QUERYSET_KEY = "SHOOTINGS"


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


class TagsAPI(ListAPIView):
    """
    Description:
    Returns a list of all tags that currently exist. Accepts no querystring arguments.
    """
    serializer_class = TagSerializer
    model = Tag
    name = "Tags API"
    queryset = Tag.objects.all()


class ShootingsAPI(ListAPIView):
    """
    Description:
    Returns a list of killings, defaults to killings of the current year unless arguments are provided.


    Behavior:
    - Queryset limits will not remove the current year default.
    - Invalid arguments are ignored.
    - Killings with age of -1 are killings where the age is unknown.
    - Arguments and Comma Separated Arguments will be used to filter against all killings,
    not just the current year.
    - tag_limit will override tag_intersect if both are set to true, and both tag_limit and tag_intersect have the same behavior when only one tag is provided
    - None of the arguments below are run against the bodycams that may or may not be attached to a killing. To filter based on bodycams, use /api/bodycams


    Arguments:

    :String name: Filters out killings whose name does not contain (case insensitive) the provided text
    :String text: Filters out killings whose description does not contain (case insensitive) the provided text
    :Integer youngerThan: Filters out killings older than the supplied age. Killings with unknown ages are excluded.
    :Integer olderThan: Filters out killings younger than the supplied age. Killings with unknown ages are excluded.
    :String dateBefore: a datestring (format YYYY-mm-dd) filtering out killings that came after the supplied date
    :String dateAfter: a datestring (format YYYY-mm-dd) filtering out killings that came before the supplied date
    :String date: a datestring (format YYYY-mm-dd) that will filter for killings that occured on that date


    Comma-Separable Arguments: (These arguments can be delineated with commas, or left as single units)

    :String race: Filters out killings where the race of the victim does not match the provided race(s)
        options=[NA=Native American, A=Asian, B=Black, PI=Pacific Islander, W=White, L=Latino, None=None, O=Other], 

    :String gender: Filters out killings where the gender of the victim does not match the provided gender(s)
        options=[M=Male, F=Female,U=Unknown]

    :String tags: Filters out killings that do not have at least one of the tags listed (see tag_intersect and tag_limit in Queryset Limits for additional behaviors)
        options= GET /api/tags for a list of all tags.
        For filtering by no tags, enter tags=null

    :String state: Filters out killings which occurred in a state not listed.
        options=All valid two letter state codes

    :String city: Filters out killings who's cities do not match the provided city/cities.
        For filtering by "no city", enter city=null

    :Integer year: An integer representation of a year (YYYY format), will filter out killings not in that year
    :Integer age: Filters out killings where the age of the victim does not match the provided age(s)
    :Integer id: filters by the id of the killings


    Queryset Limits:
    :Integer limit: limits the returned data set to the number provided
    :Integer offset: offsets the returned data by the number provided
    :Boolean tag_intersect: (True or False) Defaults to False. When set to True, Only shootings whose tags include at least all tags provided will be returned.
    :Boolean tag_limit: (True or False) Defaults to False. When set to True, only shootings whose tags match EXACTLY the tags provided will be returned.
    """
    serializer_class = ShootingSerializer
    model = Shooting
    name = "Killings API"

    def valid_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def split_arg(self, arg, arg_lookup_table):
        arg = arg.split(",")
        corrected_args = []
        for s in arg:
            if arg_lookup_table.get(s) is not None:
                corrected_args.append(arg_lookup_table.get(s))
        return corrected_args

    def convert_to_bool(self, arg):
        if arg == "true" or arg == "True":
            return True
        elif arg == "false" or arg == "False":
            return False
        return False

    def get_queryset(self):
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
        name = self.request.GET.get("name", None)  # tested
        dateBefore = self.request.GET.get("dateBefore", None)  # tested
        dateAfter = self.request.GET.get("dateAfter", None)  # tested
        date = self.request.GET.get("date", None)  # tested
        tags = self.request.GET.get("tags", None)
        race = self.request.GET.get("race", None)  # tested
        gender = self.request.GET.get("gender", None)  # tested
        state = self.request.GET.get("state", None)  # tested
        youngerThan = self.request.GET.get("youngerThan", None)  # tested
        olderThan = self.request.GET.get("olderThan", None)  # tested
        age = self.request.GET.get("age", None)  # tested
        text = self.request.GET.get("text", None)  # tested
        city = self.request.GET.get("city", None)  # tested
        year = self.request.GET.get("year", None)  # tested
        limit = self.request.GET.get("limit", None)  # tested
        offset = self.request.GET.get("offset", None)  # tested
        shooting_id = self.request.GET.get("id", None)  # tested
        tag_intersect = self.convert_to_bool(self.request.GET.get("tag_intersect", None))
        tag_limit = self.convert_to_bool(self.request.GET.get("tag_limit", None))
        date_filtering_necesssary = True

        queryset = Shooting.objects.all().order_by("-date")
        if tags is not None:
            if "," in tags:
                tags = tags.split(",")
                tag_texts = tags
                tags = Tag.objects.filter(text__in=tags)
                queryset = tags.first().shootings.all()
                for t in tags:
                    if tag_intersect:
                        queryset = queryset.intersection(queryset, t.shootings.all())
                    else:
                        queryset = queryset.union(queryset, t.shootings.all())
                date_filtering_necesssary = False
                if tag_limit:
                    queryset3 = Shooting.objects.annotate(
                        num_tags=Count("tags"),
                    ).filter(
                        num_tags=tags.count())
                    for t in tag_texts:
                        queryset3 = queryset3.filter(tags__text__in=[t])
                    queryset = queryset3
                queryset = queryset.order_by("-date")
            elif tags == "null":
                date_filtering_necesssary = False
                queryset = Shooting.objects.annotate(
                    number_of_tags=Count("tags")).filter(
                    number_of_tags=0
                ).order_by("-date")
            else:
                date_filtering_necesssary = False
                tags = Tag.objects.filter(text=tags)
                if tags.count() > 0:
                    tags = tags.first()
                    if tag_intersect or tag_limit:
                        queryset = Shooting.objects.annotate(
                            num_tags=Count("tags"),
                        ).filter(num_tags=1).filter(
                            tags__text=tags.text).order_by("-date")
                    else:
                        queryset = tags.shootings.all().order_by("-date")
        if name is not None:
            date_filtering_necesssary = False
            queryset = queryset.filter(name__icontains=name)
        if state is not None:
            if "," in state:
                corrected_states = self.split_arg(state, state_lookup_table)
                if len(corrected_states) > 0:  # we only filter if there is at least one
                    date_filtering_necesssary = False
                    queryset = queryset.filter(state__in=corrected_states)
            elif state_lookup_table.get(state) is not None:
                date_filtering_necesssary = False
                queryset = queryset.filter(state=state_lookup_table.get(state))
        if race is not None:
            if "," in race:
                corrected_races = self.split_arg(race, race_lookup_table)
                if len(corrected_races) > 0:  # we only filter if there is at least one
                    date_filtering_necesssary = False
                    queryset = queryset.filter(race__in=corrected_races)
            elif race_lookup_table.get(race) is not None:
                date_filtering_necesssary = False
                queryset = queryset.filter(race=race_lookup_table.get(race))
        if gender is not None:
            date_filtering_necesssary = False
            if "," in gender:
                corrected_genders = self.split_arg(gender, gender_lookup_table)
                if len(corrected_genders) > 0:  # we only filter if there is at least one
                    date_filtering_necesssary = False
                    queryset = queryset.filter(gender__in=corrected_genders)
            elif gender_lookup_table.get(gender) is not None:
                date_filtering_necesssary = False
                queryset = queryset.filter(gender=gender_lookup_table.get(gender))
        if text is not None:
            date_filtering_necesssary = False
            queryset = queryset.filter(description__icontains=text)
        if city is not None:
            if "," in city:
                date_filtering_necesssary = False
                cities = city.split(",")
                queryset = queryset.filter(city__iregex=r'(' + '|'.join(cities) + ')')
            elif city == "null":
                date_filtering_necesssary = False
                queryset = queryset.filter(city__isnull=True)
            else:
                date_filtering_necesssary = False
                queryset = queryset.filter(city__icontains=city)
        if shooting_id is not None:
            date_filtering_necesssary = False
            if "," in shooting_id:
                shooting_id = shooting_id.split(",")
                valid = True
                for id in shooting_id:
                    if not self.valid_int(id):
                        valid = False
                        break
                if valid:
                    queryset = queryset.filter(pk__in=shooting_id)
            elif self.valid_int(shooting_id):
                queryset = queryset.filter(pk=int(shooting_id))

        if youngerThan is not None and self.valid_int(youngerThan):
            date_filtering_necesssary = False
            queryset = queryset.filter(age__lte=int(youngerThan), age__gt=-1)
        if olderThan is not None and self.valid_int(olderThan):
            date_filtering_necesssary = False
            queryset = queryset.filter(age__gte=int(olderThan))
        if age is not None:
            if "," in age:
                age = age.split(",")
                corrected_ages = []
                for a in age:
                    if self.valid_int(a):
                        corrected_ages.append(int(corrected_ages))
                if len(corrected_ages) > 0:  # we only filter if there is at least one
                    date_filtering_necesssary = False
                    queryset = queryset.filter(age__in=corrected_ages)
            elif self.valid_int(age):
                date_filtering_necesssary = False
                queryset = queryset.filter(age=int(age))

        if dateBefore is not None and self.validate(dateBefore):
            queryset = queryset.filter(date__lte=dateBefore)
            date_filtering_necesssary = False
        if dateAfter is not None and self.validate(dateAfter):
            queryset = queryset.filter(date__gte=dateAfter)
            date_filtering_necesssary = False
        if year is not None:
            if "," in year:
                year = year.split(",")
                valid = True
                for y in year:
                    if not self.valid_int(y):
                        valid = False
                if valid:
                    date_filtering_necesssary = False
                    queryset = queryset.filter(date__year__in=year)
            elif self.valid_int(year):
                date_filtering_necesssary = False
                queryset = queryset.filter(date__year=int(year))
        if date is not None and self.validate(date):
            date_filtering_necesssary = False
            queryset = queryset.filter(date=date)
        if date_filtering_necesssary:
            queryset = queryset.filter(
                date__year=datetime.datetime.now().year)

        if limit is not None and self.valid_int(limit):
            queryset = queryset[0:int(limit)]
        if offset is not None and self.valid_int(limit):
            queryset = queryset[int(offset):]

        return queryset.prefetch_related(
            "tags", "sources", "bodycams")


class Graphs(View):
    def get(self, request, year=datetime.datetime.now().year):
        if int(year) < 2013:
            return HttpResponseRedirect(
                reverse("roster:graphs-year", kwargs={"year": 2013}))
        elif int(year) > datetime.datetime.now().year:
            return HttpResponseRedirect(
                reverse(
                    "roster:graphs-year",
                    kwargs={"year": datetime.datetime.now().year}))
        tag_data = []
        tags = Tag.objects.all()
        for tag in tags:
            tag_data.append({
                "label": tag.text,
                "data": tag.shootings.filter(date__year=year).count()
            })
        shootings = Shooting.objects.filter(date__year=year)
        race_data = []
        races = shootings.values(
            "race").annotate(sum=Count("race")).order_by("sum")
        for race in races:
            race_data.append({
                "label": Shooting.RACE_CHOICES[race["race"]][1],
                "data": race["sum"]
            })
        gender_data = []
        genders = shootings.values(
            "gender").annotate(sum=Count("gender")).order_by("sum")
        for gender in genders:
            gender_data.append({
                "label": Shooting.GENDER_CHOICES[gender["gender"]][1],
                "data": gender["sum"]
            })
        states_data = []
        states = shootings.values(
            "state").annotate(sum=Count("state")).order_by("sum")
        for state in states:
            states_data.append({
                "label": Shooting.STATE_CHOICES[state["state"]][1],
                "data": state["sum"]
            })
        month_data = []
        months = [
            {
                "month": "January",
                "sum": shootings.filter(date__month=0).count()

            },
            {
                "month": "February",
                "sum": shootings.filter(date__month=1).count()

            },
            {
                "month": "March",
                "sum": shootings.filter(date__month=2).count()

            },
            {
                "month": "April",
                "sum": shootings.filter(date__month=3).count()

            },
            {
                "month": "May",
                "sum": shootings.filter(date__month=4).count()

            },
            {
                "month": "June",
                "sum": shootings.filter(date__month=5).count()

            },
            {
                "month": "July",
                "sum": shootings.filter(date__month=6).count()

            },
            {
                "month": "August",
                "sum": shootings.filter(date__month=7).count()

            },
            {
                "month": "September",
                "sum": shootings.filter(date__month=8).count()

            },
            {
                "month": "October",
                "sum": shootings.filter(date__month=9).count()

            },
            {
                "month": "November",
                "sum": shootings.filter(date__month=10).count()

            },
            {
                "month": "December",
                "sum": shootings.filter(date__month=11).count()

            },
        ]
        for month in months:
            month_data.append({
                "label": month["month"],
                "data": month["sum"]
            })
        year_data = []
        years = [
            {
                "year": "January",
                "sum": shootings.filter(date__month__lte=0).count()
            },
            {
                "year": "February",
                "sum": shootings.filter(date__month__lte=1).count()
            },
            {
                "year": "March",
                "sum": shootings.filter(date__month__lte=2).count()
            },
            {
                "year": "April",
                "sum": shootings.filter(date__month__lte=3).count()
            },
            {
                "year": "May",
                "sum": shootings.filter(date__month__lte=4).count()
            },
            {
                "year": "June",
                "sum": shootings.filter(date__month__lte=5).count()
            },
            {
                "year": "July",
                "sum": shootings.filter(date__month__lte=6).count()
            },
            {
                "year": "August",
                "sum": shootings.filter(date__month__lte=7).count()
            },
            {
                "year": "September",
                "sum": shootings.filter(date__month__lte=8).count()
            },
            {
                "year": "October",
                "sum": shootings.filter(date__month__lte=9).count()
            },
            {
                "year": "November",
                "sum": shootings.filter(date__month__lte=10).count()
            },
            {
                "year": "December",
                "sum": shootings.filter(date__month__lte=11).count()
            },
        ]
        for y in years:
            year_data.append({
                "label": y["year"],
                "data": y["sum"]
            })
        oldest_age = shootings.latest("age").age
        ages = []
        for x in range(0, oldest_age):
            ages.append({
                "label": x,
                "data": shootings.filter(age=x).count()
            })
        shootings_w_bodycam = shootings.filter(has_bodycam=True).count()
        shootings_wo_bodycam = shootings.filter(has_bodycam=False).count()
        bodycam_data = [
            {
                "label": "Bodycam Available",
                "data": shootings_w_bodycam,
            },
            {
                "label": "No Bodycam Available",
                "data": shootings_wo_bodycam,
            }
        ]
        tag_data = sorted(tag_data, key=lambda k: k['label'])
        race_data = sorted(race_data, key=lambda k: k['label'])
        ages = sorted(ages, key=lambda k: k['label'])
        states_data = sorted(states_data, key=lambda k: k['label'])
        gender_data = sorted(gender_data, key=lambda k: k['label'])
        bodycam_data = sorted(bodycam_data, key=lambda k: k['label'])
        return render(request, "config/charts.html", {
            "year": year,
            "years": range(2013, datetime.datetime.now().year + 1),
            "tag_data": tag_data,
            "tag_range": range(len(tag_data)),
            "race_data": race_data,
            "race_range": range(len(race_data)),
            "month_data": month_data,
            "year_data": year_data,
            "age_data": ages,
            "state_data": states_data,
            "state_range": range(len(states_data)),
            "gender_data": gender_data,
            "gender_range": range(len(gender_data)),
            "bodycam_data": bodycam_data,
            "bodycam_range": range(len(bodycam_data)),
        })


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
            year = Shooting.objects.get(pk=data).date.year
            Shooting.objects.get(pk=data).delete()
            cache.delete("{}{}".format(QUERYSET_KEY, year))
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
            cache.delete("{}{}".format(QUERYSET_KEY, shooting.date.year))
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


class TestCaching(View):
    def get(self, request, year=datetime.datetime.now().year):
        date = year
        shootings1 = cache.get("{}{}1".format(QUERYSET_KEY, date))
        shootings2 = cache.get("{}{}2".format(QUERYSET_KEY, date))
        shootings3 = cache.get("{}{}3".format(QUERYSET_KEY, date))
        shootings4 = cache.get("{}{}4".format(QUERYSET_KEY, date))
        if shootings1 is not None and shootings2 is not None and shootings3 is not None and shootings4 is not None:
            shootings = list(chain(shootings1, shootings2, shootings3, shootings4))
        else:
            shootings = Shooting.objects.filter(
                date__year=date).order_by('-date').prefetch_related(
                "tags", "sources", "bodycams")
            total = shootings.count()
            if total % 4 == 0:
                offset = total / 4
            else:
                offset = int(total / 4)
            cache.get("{}{}1".format(QUERYSET_KEY, date), shootings[0:offset])
            cache.get("{}{}2".format(QUERYSET_KEY, date), shootings[offset:(2 * offset)])
            cache.get("{}{}3".format(QUERYSET_KEY, date), shootings[(offset * 2):(offset * 3)])
            cache.get("{}{}4".format(QUERYSET_KEY, date), shootings[offset * 3:])
            # cache.set("{}{}".format(QUERYSET_KEY, date), shootings)
        return JsonResponse(
            {
                "shootings": [obj.as_dict() for obj in shootings],
                "total": shootings.count()
            },
            safe=False
        )


class RosterListData(View):
    def get(self, request):
        try:
            date = int(request.GET.get("year", datetime.datetime.now().year))
        except ValueError as e:
            return HttpResponse("Invalid date", status=400,)
        shootings = cache.get("{}{}".format(QUERYSET_KEY, date))
        if not shootings:
            shootings = Shooting.objects.filter(
                date__year=date).order_by('-date').prefetch_related(
                "tags", "sources", "bodycams")
            cache.set("{}{}".format(QUERYSET_KEY, date), shootings)
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
