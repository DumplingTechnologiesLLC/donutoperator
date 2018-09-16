from django.contrib import admin
from roster.models import *
from roster.forms import ShootingModelForm
# Register your models here.


class ShootingAdmin(admin.ModelAdmin):
    list_display = ('date', 'name')
    search_fields = ['name']
    form = ShootingModelForm


admin.site.register(Shooting, ShootingAdmin)
admin.site.register(Tag)
admin.site.register(Source)
