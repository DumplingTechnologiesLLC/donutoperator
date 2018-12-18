from django.contrib import admin
from roster.models import *
from roster.forms import ShootingModelForm
# Register your models here.


class TagAdminInline(admin.TabularInline):
    model = Tag.shootings.through


class SourceAdminInline(admin.TabularInline):
    model = Source


class ShootingAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ['name']
    inlines = (TagAdminInline, SourceAdminInline)
    form = ShootingModelForm


admin.site.register(Shooting, ShootingAdmin)
admin.site.register(Tag)
admin.site.register(Source)
admin.site.register(Tip)
