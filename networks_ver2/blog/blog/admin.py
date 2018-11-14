from django.contrib import admin
from .models import Traffic

# Register your models here.
class TrafficAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','intersection_name','phase_one','phase_two','is_params','is_auto')

admin.site.register(Traffic, TrafficAdmin)
