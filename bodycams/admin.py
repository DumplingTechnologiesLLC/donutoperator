from django.contrib import admin
from . import models
from roster.models import Tag
from .forms import BodycamModelForm
# Register your models here.


class TagAdminInline(admin.TabularInline):
    model = Tag


class BodycamAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ['title']
    inlines = (TagAdminInline,)
    # form = BodycamModelForm


admin.site.register(models.Bodycam, BodycamAdmin)
