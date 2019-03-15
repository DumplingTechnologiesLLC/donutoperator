from django.views.generic.detail import DetailView
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Count
from bodycams.models import Bodycam
from django.urls import reverse
from config.utils import mobileBrowser
from django.contrib import messages
from roster.models import Shooting, Tag
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import json
import logging
from django.views import View
from bodycams.forms import BodycamModelForm
from bodycams.serializers import BodycamWithShootingSerializer
from rest_framework.generics import ListAPIView


def link_bodycam_and_shooting(bodycam, data, request):
    """Links a bodycam to a shooting

    Arguments:
    :param bodycam: a Bodycam object
    :param data: a dict taken from the WSGI request
    :param request: the WSGI request from the endpoint

    Returns:
    :on success: None
    :on error: HttpResponse
    """
    if data["shooting"] == -1:
        bodycam.shooting = None
        bodycam.save()
        return None
    elif data["shooting"] != "" and data["shooting"] is not None:
        try:
            shooting = Shooting.objects.get(pk=int(data["shooting"]))
        except Exception as e:
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            return HttpResponse(
                ("We've created the bodycam but when we tried to link "
                 "the bodycam to the shooting you requested, we couldn't find the shooting."
                 " Please refresh the page and try to link the bodycam manually."),
                status=406
            )
        bodycam.shooting = shooting
        shooting.has_bodycam = True
        shooting.save()
        bodycam.save()
    return None


def submit_form(form, data):
    """Submits a bodycam and adds tags to the bodycam

    Arguments:
    :param form: a validated BodycamModelForm
    :param data: a dictionary containing a JSON array of tags

    Returns:
    a Bodycam object with tags attached
    """
    bodycam = form.save()
    bodycam.tags.clear()
    for tag in data["tags"]:
        mmtag, created = Tag.objects.get_or_create(text=tag)
        mmtag.bodycams.add(bodycam)
    return bodycam


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


class BodycamsAPI(ListAPIView):
    """
    Description:
    Returns a list of all bodycams, with nested information on killings, defaults to bodycams of the current year unless arguments are provided.


    Behavior:
    - Queryset limits will not remove the current year default.
    - Invalid arguments are ignored.
    - Arguments and Comma Separated Arguments will be used to filter against all bodycams,
    not just the current year.
    - tag_limit will override tag_intersect if both are set to true, and both tag_limit and tag_intersect have the same behavior when only one tag is provided
    - None of the arguments below are run against the bodycams that may or may not be attached to a killing. To filter based on details of the killing, use api


    Arguments:
    :String title: Filters out bodycams whose title does not contain (case insensitive) the provided text
    :String text: Filters out bodycams whose description does not contain (case insensitive) the provided text
    :String department: Filters out bodycams whose department doesn't contain (case insensitive) the text provided.
    :String dateBefore: a datestring (format YYYY-mm-dd) filtering out bodycams that came after the supplied date
    :String dateAfter: a datestring (format YYYY-mm-dd) filtering out bodycams that came before the supplied date
    :String date: a datestring (format YYYY-mm-dd) that will filter for bodycams that occured on that date


    Comma-Separable Arguments:

    :String city: Filters out bodycams who's cities do not match the provided city/cities.
        For filtering by "no city", enter city=null

    :String state: Filters out bodycams which occurred in a state not listed.
        options=All valid two letter state codes

    :Integer year: An integer representation of a year (YYYY format), will filter out bodycams not in that year
    :Integer id: filters by the id of the bodycams

    :String tags: Filters out bodycams that do not have at least one of the tags listed (see tag_intersect and tag_limit in Queryset Limits for additional behaviors)
        options= GET /api/tags for a list of all tags.
        For filtering by no tags, enter tags=null

    Queryset Limits:

    :Integer limit: limits the returned data set to the number provided
    :Integer offset: offsets the returned data by the number provided
    :Boolean tag_intersect: (True or False) Defaults to False. When set to True, Only shootings whose tags include at least all tags provided will be returned.
    :Boolean tag_limit: (True or False) Defaults to False. When set to True, only shootings whose tags match EXACTLY the tags provided will be returned.
    """
    serializer_class = BodycamWithShootingSerializer
    model = Tag
    name = "Bodycams API"

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

    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def valid_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def get_queryset(self):
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
        title = self.request.GET.get("title", None)  # tested
        text = self.request.GET.get("text", None)  # tested
        department = self.request.GET.get("department", None)  # tested
        dateBefore = self.request.GET.get("dateBefore", None)  # tested
        dateAfter = self.request.GET.get("dateAfter", None)  # tested
        date = self.request.GET.get("date", None)  # tested
        city = self.request.GET.get("city", None)  # tested
        state = self.request.GET.get("state", None)  # tested
        year = self.request.GET.get("year", None)  # tested
        tags = self.request.GET.get("tags", None)
        bodycam_id = self.request.GET.get("id", None)  # tested
        limit = self.request.GET.get("limit", None)  # tested
        offset = self.request.GET.get("offset", None)  # tested
        tag_intersect = self.convert_to_bool(self.request.GET.get("tag_intersect", None))
        tag_limit = self.convert_to_bool(self.request.GET.get("tag_limit", None))
        date_filtering_necesssary = True
        queryset = Bodycam.objects.all().order_by("-date")
        if tags is not None:
            if "," in tags:
                tags = tags.split(",")
                tag_texts = tags
                tags = Tag.objects.filter(text__in=tags)
                queryset = tags.first().bodycams.all()
                for t in tags:
                    if tag_intersect:
                        queryset = queryset.intersection(queryset, t.bodycams.all())
                    else:
                        queryset = queryset.union(queryset, t.bodycams.all())
                date_filtering_necesssary = False
                if tag_limit:
                    queryset3 = Bodycam.objects.annotate(
                        num_tags=Count("tags"),
                    ).filter(
                        num_tags=tags.count())
                    for t in tag_texts:
                        queryset3 = queryset3.filter(tags__text__in=[t])
                    queryset = queryset3
                queryset = queryset.order_by("-date")
            elif tags == "null":
                date_filtering_necesssary = False
                queryset = Bodycam.objects.annotate(
                    number_of_tags=Count("tags")).filter(
                    number_of_tags=0
                ).order_by("-date")
            else:
                date_filtering_necesssary = False
                tags = Tag.objects.filter(text=tags)
                if tags.count() > 0:
                    tags = tags.first()
                    if tag_intersect or tag_limit:
                        queryset = Bodycam.objects.annotate(
                            num_tags=Count("tags"),
                        ).filter(num_tags=1).filter(
                            tags__text=tags.text).order_by("-date")
                    else:
                        queryset = tags.bodycams.all().order_by("-date")
        if state is not None:
            if "," in state:
                corrected_states = self.split_arg(state, state_lookup_table)
                if len(corrected_states) > 0:  # we only filter if there is at least one
                    date_filtering_necesssary = False
                    queryset = queryset.filter(state__in=corrected_states)
            elif state_lookup_table.get(state) is not None:
                date_filtering_necesssary = False
                queryset = queryset.filter(state=state_lookup_table.get(state))
        if text is not None:
            date_filtering_necesssary = False
            queryset = queryset.filter(description__icontains=text)
        if department is not None:
            date_filtering_necesssary = False
            queryset = queryset.filter(department__icontains=department)
        if title is not None:
            date_filtering_necesssary = False
            queryset = queryset.filter(title__icontains=title)
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
        if bodycam_id is not None:
            date_filtering_necesssary = False
            if "," in bodycam_id:
                bodycam_id = bodycam_id.split(",")
                valid = True
                for id in bodycam_id:
                    if not self.valid_int(id):
                        valid = False
                        break
                if valid:
                    queryset = queryset.filter(pk__in=bodycam_id)
            elif self.valid_int(bodycam_id):
                queryset = queryset.filter(pk=int(bodycam_id))

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
            "tags", "shooting__sources", "shooting")


class BodycamLink(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request):
        """AJAX only
        Links an existing bodycam and an existing killing together based on id

        Expects:
        bodycam_id: integer id of an existing bodycam,
        shooting_id: integer id of an existing killing,

        Arguments:
        :param request: a Django WSGI request object with the data described above

        Returns:
        on success - HTTP Status 200,
        on error - HTTP Status 500,  exception string
        """
        try:
            bodycam_id = int(request.POST.get("bodycam_id"))
            shooting_id = int(request.POST.get("shooting_id"))
        except ValueError as e:  # pragma: no cover
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            print(e)
            return HttpResponse(str(e), status=500,)
        try:
            bodycam = Bodycam.objects.get(pk=bodycam_id)
            shooting = Shooting.objects.get(pk=shooting_id)
            bodycam.shooting = shooting
            bodycam.save()
            shooting.has_bodycam = True
            shooting.save()
            return HttpResponse(status=200)
        except (Bodycam.DoesNotExist, Shooting.DoesNotExist) as e:
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            return HttpResponse(str(e), status=500, )


class BodycamEdit(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request):
        """AJAX only
        Edits an existing bodycam, including tags, then returns the id of the
        bodycam to the client.

        If a shooting id is included in the bodycam, then the bodycam will be linked
        to the shooting. If the shooting id is -1, then the bodycam will be unlinked
        from its current shooting.

        Expects:
        a stringified bodycam JSON object in the following format:
        bodycam: {
            id: integer,
            title: string,
            video: string iframe embed code with a width and height specified,
            description: string,
            department: string,
            state: string,
            city: string,
            date: string: "YYYY-MM-DDTH:mm:ss",
            tags: [],
            shooting: integer (pk),
        },
        Arguments:
        :param request: a Django WSGI request object with the data described above

        Returns:
        on success - HTTP Status 200, created bodycam id
        on error - HTTP Status 400,  form errors as HTML
        """
        data = json.loads(request.POST.get("bodycam"))
        id = data["id"]
        try:
            bodycam = Bodycam.objects.get(pk=id)
        except Bodycam.DoesNotExist:
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            return HttpResponse(
                "We couldn't find that bodycam in our database anymore.", status=400)
        data["date"] = data["date"].split("T")[0]
        form = BodycamModelForm(data, instance=bodycam)
        if form.is_valid():
            bodycam = submit_form(form, data)
            return_value = link_bodycam_and_shooting(bodycam, data, request)
            if return_value is not None:
                return return_value
            return HttpResponse(bodycam.id, status=200)
        return HttpResponse(create_html_errors(form), status=400)


class BodycamSubmit(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request):
        '''AJAX only
        Creates a new bodycam, with tags added to it, and then returns the id of the
        bodycam to the client

        If a shooting id is included in the bodycam, then the bodycam will be linked
        to the shooting.

        Expects:
        A stringified bodycam JSON object in the following format:
        bodycam: {
                id: integer,
                title: string,
                video: string iframe embed code with a width and height specified,
                description: string,
                department: string,
                state: string,
                city: string,
                date: string: "YYYY-MM-DDTH:mm:ss",
                tags: [],
                shooting: integer (pk),
        },

        Arguments:
        :param request: a Django WSGI request object with the data described above

        Returns:
        on success - HTTP Status 200, created bodycam id
        on error - HTTP Status 400,  form errors as HTML
        '''
        data = json.loads(request.POST.get("bodycam"))
        data["date"] = data["date"].split("T")[0]
        form = BodycamModelForm(data)
        if form.is_valid():
            bodycam = submit_form(form, data)
            return_value = link_bodycam_and_shooting(bodycam, data, request)
            if return_value is not None:
                return return_value
            return HttpResponse(bodycam.id, status=200)
        return HttpResponse(create_html_errors(form), status=400)


class BodycamDashboard(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, date=datetime.datetime.now().year):
        """Return sthe admin page for managing bodycams

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of the bodycams, the number of bodycams, the year, and the departments
        """
        display_date = None
        try:
            display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        except ValueError:
            return HttpResponseRedirect(reverse("bodycams:dashboard"))
        return render(request, "bodycams/bodycam_dashboard.html", {
            "year": display_date.year,
        })

    def post(self, request):
        """AJAX only

        Deletes the Bodycam that has a pk matching the one provided

        Expects:
        pk - an integer id for a Bodycam
        Arguments:
        :param request: a Django WSGI request object

        Returns:
        On success - Redirect with successful message
        On error - Redirect with failure message
        """
        pk = request.POST.get("pk")
        try:
            article = Bodycam.objects.get(pk=pk)
            article.delete()
            messages.success(request, "Bodycam deleted successfully")
            return HttpResponseRedirect(reverse("bodycams:dashboard"))
        except Bodycam.DoesNotExist:
            error_data = json.dumps(request.POST).replace("\\\"", "'")
            logging.error("request data: {}".format(error_data))
            messages.error(request, "We couldn't find that bodycam in the database.")
            return HttpResponseRedirect(reverse("bodycams:dashboard"))


class BodycamData(View):
    def get(self, request):
        date = int(request.GET.get("year", datetime.datetime.now().year))
        bodycams = Bodycam.objects.filter(
            date__year=date).order_by("-date").prefetch_related("tags", "shooting")
        departments = bodycams.order_by(
            "department").values('department').distinct(),
        departments = [obj['department'] if obj['department']
                       is not None else "Unknown" for obj in departments[0]]
        bodycams = [obj.as_dict() for obj in bodycams],
        return JsonResponse({
            "bodycams": bodycams,
            "departments": departments
        }, safe=False)


class BodycamDetailView(DetailView):
    model = Bodycam

    def get_context_data(self, **kwargs):
        context = super(BodycamDetailView, self).get_context_data(**kwargs)
        return context


class BodycamIndexView(View):
    def get(self, request, date=datetime.datetime.now().year):
        '''Returns the bodycam index view

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of the bodycams, the number of bodycams, the year, and the departments
        '''
        display_date = None
        try:
            display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        except ValueError:
            messages.warning(request, "No data exists for that year.")
            return HttpResponseRedirect(reverse("bodycams:bodycams"))
        if mobileBrowser(request):
            template = "mobile/bodycam/bodycam_index.html"
        else:
            template = "bodycams/bodycam_index.html"
        return render(request, template, {
            "year": display_date.year,
        })
