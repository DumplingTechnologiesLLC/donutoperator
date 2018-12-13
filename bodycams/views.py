from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from bodycams.models import Bodycam
from django.urls import reverse
from django.contrib import messages
from roster.models import Shooting, Tag
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import json
import logging
from django.views import View
from bodycams.forms import BodycamModelForm


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


class BodycamLink(LoginRequiredMixin, View):
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
    def get(self, request, date=datetime.datetime.now().year):
        """Return sthe admin page for managing bodycams

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of the bodycams, the number of bodycams, the year, and the departments
        """
        display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        return render(request, "bodycam/bodycam_dashboard.html", {
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
        departments = [obj['department'] if obj['department'] is not None else "Unknown" for obj in departments[0]]
        bodycams = [obj.as_dict() for obj in bodycams],
        return JsonResponse({
            "bodycams": bodycams,
            "departments": departments
        }, safe=False)


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
        display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        return render(request, "bodycam/bodycam_index.html", {

            "year": display_date.year,
        })
