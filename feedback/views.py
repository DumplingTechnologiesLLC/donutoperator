from django.shortcuts import render
from .forms import FeedbackModelForm
from django.views.generic.edit import FormView
from django.contrib import messages

# Create your views here.


class FeedbackPage(FormView):
    template_name = "config/feedback.html"
    form_class = FeedbackModelForm
    success_url = "/"

    def form_valid(self, form):
        messages.success(
            self.request, "Thank you for the input, we will look into it.")
        form.save()
        return super().form_valid(form)
