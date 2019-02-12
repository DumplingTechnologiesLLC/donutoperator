from django.shortcuts import render
from django.views import View


class APIList(View):
    def get(self, request):
        return render(request, "config/api_list.html", {})


class Sitemap(View):
    def get(self, request):
        return render(request, "config/sitemap.html")


class ChangeLog(View):
    def get(self, request):
        return render(request, "config/changelog.html", {})


class AboutPage(View):
    def get(self, request):
        return render(request, "config/about.html", {})
