from django.contrib import admin
from .models import Traffic

# Register your models here.
class TrafficAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','intersection_name','phase_one','phase_two','appr1_name','appr2_name','is_params','is_auto')

admin.site.register(Traffic, TrafficAdmin)
