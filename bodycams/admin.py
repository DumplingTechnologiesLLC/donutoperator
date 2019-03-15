from django.contrib import admin
from . import models
from roster.models import Tag
# Register your models here.


class TagAdminInline(admin.TabularInline):
    model = Tag.bodycams.through


class BodycamAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date')
    search_fields = ['title']
    inlines = (TagAdminInline,)
    # form = BodycamModelForm


admin.site.register(models.Bodycam, BodycamAdmin)
