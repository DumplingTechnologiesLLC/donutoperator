from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from rest_framework import viewsets
from .models import Video, Tag
from .serializers import VideoSerializer
import datetime
from django.contrib import messages
# Create your views here.


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing Videos.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    lookup_url_kwarg = "date"

    def get_queryset(self):
        query = {}
        for key in self.request.query_params:
            if key != 'tags[]' and key != 'state__in[]':
                query[key] = self.request.query_params[key][0] if isinstance(
                    self.request.query_params[key], list) else self.request.query_params[key]
            elif key == 'state__in[]':
                query['state__in'] = self.request.query_params.getlist(key)
        tags = self.request.query_params.getlist('tags[]', [])
        if len(tags) == 0:
            queryset = Video.objects.filter(**query)
        else:
            print(tags)
            tags = Tag.objects.filter(text__in=tags)
            queryset = Video.objects.none()
            for tag in tags:
                queryset = queryset.union(
                    tag.videos.filter(**query), queryset)
        return queryset


class VideoIndexView(View):
    def get(self, request, date=datetime.datetime.now().year):
        '''Returns the bodycam index view

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of the videos, the number of videos, the year, and the departments
        '''
        display_date = None
        try:
            display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        except (ValueError, OverflowError):
            messages.warning(request, "No data exists for that year.")
            return HttpResponseRedirect(reverse("videos:index"))
        # if mobileBrowser(request):
        #     template = "mobile/bodycam/bodycam_index.html"
        # else:
        template = "videos/index.html"
        return render(request, template, {
            "year": display_date.year,
        })
