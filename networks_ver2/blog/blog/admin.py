from django.contrib import admin
from .models import Traffic

# Register your models here.
class TrafficAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','phase_one','phase_two')

admin.site.register(Traffic, TrafficAdmin)
