from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

app_name='mushrooms'

# urlpatterns = [    
#     url(r'^receivedata$',views.receive_data, name='data')
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
