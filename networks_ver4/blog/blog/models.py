from djgeojson.fields import PolygonField
from django.db import models
from django.contrib.auth.models import User

class MushroomSpot(models.Model):

    title = models.CharField(max_length=256)
    description = models.TextField()
    picture = models.FileField()
    geom = PolygonField()

    def __unicode__(self):
        return self.title

    @property
    def picture_url(self):
        return self.picture.null

class Traffic(models.Model):   
    intersection_id = models.CharField(max_length=30, primary_key=True)
    intersection_name = models.CharField(max_length=30)
    phase_one = models.IntegerField()
    phase_two = models.IntegerField()
    appr1_name = models.CharField(max_length=80)
    appr2_name = models.CharField(max_length=80)
    is_params = models.BooleanField(default=False)
    is_auto = models.BooleanField(default=False)

class Infointer(models.Model):   
    intersection_id = models.CharField(max_length=30)
    appr_id = models.CharField(max_length=30)
    appr_name = models.CharField(max_length=80)
    vtb = models.FloatField()
    vhc_come = models.IntegerField()
    vhc_out = models.IntegerField()    