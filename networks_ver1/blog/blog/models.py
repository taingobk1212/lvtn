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
    phase_one = models.CharField(max_length=30)
    phase_two = models.CharField(max_length=30)