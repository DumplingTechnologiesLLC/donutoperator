from django.conf import settings
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from .models import Video, Tag
from .serializers import VideoDataSerializer, VideoSerializer
import datetime
from django.contrib import messages
# Create your views here.


def generate_query(query_params):
    query = {}
    for key in query_params:
        if key == 'page':
            # we don't filter on page
            continue
        if key != 'tags[]' and key != 'state__in[]':
            query[key] = query_params[key][0] if isinstance(
                query_params[key], list) else query_params[key]
        elif key == 'state__in[]':
            query['state__in'] = query_params.getlist(key)
    return query


def retrieve_queryset(query, tags):
    if len(tags) == 0:
        return Video.objects.filter(**query).order_by('-date')
    else:
        tags = Tag.objects.filter(text__in=tags)
        queryset = Video.objects.none()
        for tag in tags:
            queryset = queryset.union(
                tag.videos.filter(**query), queryset)
        return queryset.order_by('-date')


class StandardResultsSetPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing Videos.
    """
    queryset = Video.objects.all().order_by('-date')
    serializer_class = VideoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = generate_query(self.request.query_params)
        tags = self.request.query_params.getlist('tags[]', [])
        return retrieve_queryset(query, tags)


class EditorVideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = generate_query(self.request.query_params)
        tags = self.request.query_params.getlist('tags[]', [])
        return retrieve_queryset(query, tags)

    def create(self, request, *args, **kwargs):
        serializer = VideoDataSerializer(data=request.data)
        tags = request.data.get('tags')
        del request.data['tags']
        if serializer.is_valid():
            video = serializer.save()
            for tag in tags:
                djangoTag = Tag.objects.filter(pk=tag.get('id'))
                if djangoTag.exists():
                    djangoTag = djangoTag.first()
                    djangoTag.videos.add(video)
                else:
                    tag = Tag.objects.create(
                        text=tag.get('display')
                    )
                    tag.videos.add(video)
            return HttpResponse('Success', status=status.HTTP_201_CREATED)
        return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # its date instead of id because of the lookup_url_kwargs
        model = get_object_or_404(Video, pk=kwargs.get('pk'))

        serializer = VideoDataSerializer(data=request.data, instance=model)
        tags = request.data.get('tags')
        del request.data['tags']
        if serializer.is_valid():
            video = serializer.save()
            for tag in tags:
                djangoTag = Tag.objects.filter(pk=tag.get('id'))
                if djangoTag.exists():
                    djangoTag = djangoTag.first()
                    djangoTag.videos.add(video)
                else:
                    tag = Tag.objects.create(
                        text=tag.get('display')
                    )
                    tag.videos.add(video)
            return HttpResponse('Success', status=status.HTTP_200_OK)
        return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoIndexView(View):
    def get(self, request):
        '''Returns the bodycam index view

        Arguments:
        :param request: a Django WSGI request object
        :param date: an optional parameter that defaults to the current year if not
        provided

        Returns:
        a render of the videos, the number of videos, the year, and the departments
        '''
        # if mobileBrowser(request):
        #     template = "mobile/bodycam/bodycam_index.html"
        # else:
        template = "videos/index.html"
        context = {
            "page_size": settings.PAGE_SIZE
        }
        return render(request, template, context)
