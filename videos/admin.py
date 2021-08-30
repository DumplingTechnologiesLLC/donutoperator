from django.contrib import admin
from .models import Video, Tag
# Register your models here.


class TagAdminInline(admin.TabularInline):
    model = Tag.videos.through


class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date')
    search_fields = ['title']
    inlines = (TagAdminInline,)
    # form = VideoModelForm


admin.site.register(Video, VideoAdmin)
admin.site.register(Tag)
