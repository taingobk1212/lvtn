from django.contrib import admin
from .models import Traffic, Infointer, trafficlightinfo

# Register your models here.
class TrafficAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','intersection_name','appr1_name','appr2_name','is_params','is_auto')

class InfointerAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','appr_id','appr_name','vtb','vhc_come','vhc_out','vhc_queue_length','wait_avrg')

class trafficlightinfoAdmin(admin.ModelAdmin):
    list_display = ('intersection_id','appr_id','appr_name','tlgreen','tlyellow','tlred')    

admin.site.register(Traffic, TrafficAdmin)
admin.site.register(Infointer, InfointerAdmin)
admin.site.register(trafficlightinfo, trafficlightinfoAdmin)