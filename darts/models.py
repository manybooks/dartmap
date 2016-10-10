from django.db import models

class Dart(models.Model):
    address = models.CharField(max_length=40)
    place_name = models.CharField(max_length=100)
    link_url = models.CharField(max_length=400)
    src_url = models.CharField(max_length=400)
