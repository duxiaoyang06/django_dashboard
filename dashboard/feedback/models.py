from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Info(models.Model):
	feedback_id = models.IntegerField(primary_key=True)
	status_code = models.IntegerField()


