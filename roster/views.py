from django.shortcuts import render
from roster.models import Shooting
# Create your views here.

class CompetitionListView(View):
    def get(self, request):
        shootings = Shooting.objects.all()
        return render(request, "competition/competition_list.html", {
            "shootings": shootings,
        })