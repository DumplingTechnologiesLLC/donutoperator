from django.shortcuts import render
from django.views import View


class AboutPage(View):
    def get(self, request):
        return render(request, "config/about.html", {})
