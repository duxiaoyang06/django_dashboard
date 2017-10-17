from __future__ import unicode_literals

from django.db import models

class Info(models.Model):
	user_id = models.IntegerField(primary_key=True)
	pin = models.CharField(max_length=255)
	nickname = models.CharField(max_length=255)
	login_email = models.CharField(max_length=255)
	create_time = models.CharField(max_length=255)




